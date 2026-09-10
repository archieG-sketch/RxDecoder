import re
import json
import uuid
from typing import List, Dict, Any, Tuple, Optional
from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from app.config import settings
from app.models.schemas import MedicationItem, ConfidenceLevel
from app.utils.logger import logger
from app.utils.sig_decoder import decode_sig_string
from app.utils.medical_kb import lookup_drug_info, lookup_drug_info_online, DRUG_DATABASE

PARSER_SYSTEM_PROMPT = """You are Agent 3: Prescription Parsing & Sig Extraction Specialist in RxDecoder.
Your mission is to parse sanitized prescription text into a structured, validated list of medications.

SAFETY & EXTRACTION RULES:
1. Extract every individual prescribed medication present in the text.
2. For each medication, extract:
   - "name": Prescribed name as written
   - "generic_name": Generic pharmaceutical name if confident, else null
   - "brand_name": Commercial brand name if known, else null
   - "strength": Strength with units (e.g. "500 mg", "10 mg/5 mL", "250 mcg")
   - "dosage": Amount per dose (e.g. "1 capsule", "2 tablets", "5 mL")
   - "frequency": Translated frequency (e.g. "Twice daily (every 12 hours)", "Once daily in the morning")
   - "route": Route of administration (e.g. "Oral", "Topical", "Inhalation", "Ophthalmic")
   - "duration": Duration of treatment (e.g. "7 days", "14 days", "30 days", "Ongoing")
   - "timing_instructions": Specific time of day (e.g. "Morning and Night", "Before bedtime")
   - "food_instructions": Specific food relation (e.g. "Take after meals", "Take on an empty stomach")
   - "additional_notes": Special instructions (e.g. "Finish full course", "Avoid driving")
   - "confidence": "high" | "medium" | "low" | "unclear"
   - "confidence_reason": Explain reason if confidence is not "high"

3. UNCERTAINTY MANDATE:
   - If handwriting is sloppy or unclear, DO NOT GUESS OR INVENT A MEDICATION.
   - Set confidence to "low" or "unclear", and in confidence_reason write:
     "Medication name could not be identified with sufficient confidence. Please verify this with your pharmacist or doctor."

Respond ONLY with valid JSON matching this schema:
{
  "medications": [
    {
      "name": "Medicine Name",
      "generic_name": "Generic Name",
      "brand_name": "Brand Name",
      "strength": "500 mg",
      "dosage": "1 tablet",
      "frequency": "Twice daily",
      "route": "Oral",
      "duration": "7 days",
      "timing_instructions": "Morning and Night",
      "food_instructions": "Take after meals",
      "additional_notes": null,
      "confidence": "high",
      "confidence_reason": null
    }
  ],
  "has_uncertain_handwriting": false,
  "uncertainty_summary": null
}"""

class ParserAgent(LlmAgent):
    name: str = "parser_agent"
    description: str = "Prescription parsing and medication sig extraction specialist."
    model: str = settings.default_model
    instruction: str = PARSER_SYSTEM_PROMPT

    def get_client(self) -> Optional[genai.Client]:
        if settings.gemini_api_key and settings.gemini_api_key.startswith("AIzaSy"):
            try:
                return genai.Client(api_key=settings.gemini_api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")
        return None

    async def parse_prescription(self, sanitized_text: str) -> Tuple[List[MedicationItem], bool, str]:
        """
        Parses sanitized prescription text into typed MedicationItem models.
        Falls back to clinical entity parser if Gemini is unavailable.
        """
        logger.info("Agent 3 (ParserAgent): Parsing sanitized prescription text.")

        client = self.get_client()
        if client and len(sanitized_text.strip()) > 0:
            try:
                prompt = (
                    f"{PARSER_SYSTEM_PROMPT}\n\n"
                    f"SANITIZED PRESCRIPTION TEXT:\n\"\"\"\n{sanitized_text}\n\"\"\""
                )
                response = client.models.generate_content(
                    model=settings.default_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1  # Lower temp for consistent JSON parsing
                    )
                )

                if response.text:
                    logger.debug(f"Agent 3: Gemini parsing response: {response.text[:300]}")
                    parsed = json.loads(response.text)
                    raw_meds = parsed.get("medications", [])
                    has_uncertain = parsed.get("has_uncertain_handwriting", False)
                    uncertainty_summary = parsed.get("uncertainty_summary", "")

                    if raw_meds:
                        med_items: List[MedicationItem] = []
                        for idx, m in enumerate(raw_meds):
                            med_id = f"med_{idx + 1}_{uuid.uuid4().hex[:6]}"
                            conf = m.get("confidence", "high")
                            if conf in ["low", "unclear"]:
                                has_uncertain = True

                            item = MedicationItem(
                                id=med_id,
                                name=m.get("name", "Prescribed Medication"),
                                generic_name=m.get("generic_name"),
                                brand_name=m.get("brand_name"),
                                strength=m.get("strength", "Standard strength"),
                                dosage=m.get("dosage", "1 unit"),
                                frequency=m.get("frequency", "As directed"),
                                route=m.get("route", "Oral"),
                                duration=m.get("duration", "As prescribed"),
                                timing_instructions=m.get("timing_instructions", "As directed"),
                                food_instructions=m.get("food_instructions", "With water"),
                                additional_notes=m.get("additional_notes"),
                                confidence=conf,
                                confidence_reason=m.get("confidence_reason")
                            )
                            med_items.append(item)

                        logger.info(f"Agent 3: Gemini parsed {len(med_items)} medication(s).")
                        return med_items, has_uncertain, uncertainty_summary or ""
            except json.JSONDecodeError as e:
                logger.error(f"Agent 3: Gemini returned invalid JSON: {e}. Falling back to clinical parser.")
            except Exception as e:
                logger.warning(f"Agent 3: Gemini parse error ({type(e).__name__}: {str(e)[:100]}). Using clinical entity parser.")

        # High-accuracy Clinical Entity & Sig Parser
        return self._clinical_entity_parse(sanitized_text)

    def _clinical_entity_parse(self, text: str) -> Tuple[List[MedicationItem], bool, str]:
        """
        Dynamically extracts medication names, strengths, dosages, sig directions,
        and durations from the actual text extracted from the uploaded document.
        """
        logger.info("Agent 3: Running clinical entity extractor on extracted text.")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        found_meds: List[MedicationItem] = []
        has_uncertain = False
        detected_drug_keys = set()

        # Regex patterns for clinical parameters
        strength_pattern = re.compile(r'(\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|mg/ml|%)\b)', re.IGNORECASE)
        dosage_pattern = re.compile(r'(\b\d+\s*(?:tablet|tab|capsule|cap|puff|spray|drop|tsp|tbsp|gtt|unit)s?\b)', re.IGNORECASE)
        duration_pattern = re.compile(r'(?:x|for|duration)[:\s]*(\d+\s*(?:days?|d|weeks?|wks?|months?|hrs?))', re.IGNORECASE)

        # Check line by line and against full text
        for line in lines:
            line_lower = line.lower()

            # Skip header / clinic lines
            if any(k in line_lower for k in ['dr.', 'clinic', 'hospital', 'patient', 'dob:', 'date:']) and not any(k in line_lower for k in ['rx', 'tab', 'cap', 'mg']):
                continue

            # Look for known drugs in this line
            for drug_key, drug_info in DRUG_DATABASE.items():
                if drug_key in detected_drug_keys:
                    continue

                # Match drug name or brand name
                brand = (drug_info.get("brand_name") or "").lower()
                generic = (drug_info.get("generic_name") or "").lower()

                if (drug_key in line_lower) or (brand and brand in line_lower) or (generic and generic in line_lower):
                    detected_drug_keys.add(drug_key)

                    # Extract strength
                    str_match = strength_pattern.search(line)
                    strength = str_match.group(1) if str_match else "As labeled"

                    # Extract dosage
                    dos_match = dosage_pattern.search(line)
                    dosage = dos_match.group(1) if dos_match else "1 tablet/capsule"

                    # Extract duration
                    dur_match = duration_pattern.search(line)
                    duration = dur_match.group(1) if dur_match else "As prescribed"
                    if duration.endswith("d"):
                        duration = duration[:-1] + " days"

                    # Decode sig
                    decoded_sig = decode_sig_string(line)
                    frequency = "As directed by physician"
                    timing = "Regular intervals"
                    food = "Take with water"

                    line_upper = line.upper()
                    if "TID" in line_upper or "3 TIMES" in line_upper:
                        frequency = "Three times daily (every 8 hours)"
                        timing = "Morning, Afternoon, and Night"
                    elif "BID" in line_upper or "2 TIMES" in line_upper or "TWICE" in line_upper:
                        frequency = "Twice daily (every 12 hours)"
                        timing = "Morning and Evening"
                    elif "QID" in line_upper or "4 TIMES" in line_upper:
                        frequency = "Four times daily (every 6 hours)"
                        timing = "Morning, Noon, Evening, Bedtime"
                    elif "QHS" in line_upper or "BEDTIME" in line_upper:
                        frequency = "Once daily at bedtime"
                        timing = "Night before sleep"
                    elif "QAM" in line_upper or "MORNING" in line_upper:
                        frequency = "Once daily in the morning"
                        timing = "Every morning"
                    elif "PRN" in line_upper or "AS NEEDED" in line_upper:
                        frequency = "As needed for symptoms"
                        timing = "When experiencing symptoms (spaced at least 6 hours apart)"

                    if "PC" in line_upper or "AFTER MEAL" in line_upper or "AFTER FOOD" in line_upper:
                        food = "Take after meals"
                    elif "AC" in line_upper or "BEFORE MEAL" in line_upper:
                        food = "Take on an empty stomach 30-60 minutes before meals"
                    elif "WF" in line_upper or "WITH FOOD" in line_upper or "WITH MEAL" in line_upper:
                        food = "Take with food or a meal"

                    med_item = MedicationItem(
                        id=f"med_{len(found_meds) + 1}_{uuid.uuid4().hex[:6]}",
                        name=drug_info.get("generic_name", drug_key.title()),
                        generic_name=drug_info.get("generic_name"),
                        brand_name=drug_info.get("brand_name"),
                        strength=strength,
                        dosage=dosage,
                        frequency=frequency,
                        route="Oral",
                        duration=duration,
                        timing_instructions=timing,
                        food_instructions=food,
                        additional_notes=f"Prescription direction: {decoded_sig}",
                        confidence="high"
                    )
                    found_meds.append(med_item)

        # If specific known drugs were detected, return them
        if found_meds:
            logger.info(f"Agent 3: Successfully parsed {len(found_meds)} prescribed medication(s) from document.")
            return found_meds, False, ""

        # If text was extracted but no recognized drug name matched (e.g. ambiguous cursive or novel drug)
        has_uncertain = True
        logger.warning("Agent 3: Unclear handwriting or unrecognized drug name in document. Flagging verification.")
        
        # Check if there are prescription-like lines
        sample_line = lines[0] if lines else "Unclear handwriting"
        unclear_item = MedicationItem(
            id=f"med_unclear_{uuid.uuid4().hex[:6]}",
            name=f"Prescribed Item: {sample_line[:30]}... (Verification Required)",
            generic_name="Uncertain - Please verify with pharmacist",
            brand_name=None,
            strength="Strength unclear from handwriting",
            dosage="1 dose",
            frequency="Please confirm with doctor/pharmacist",
            route="Oral",
            duration="As directed",
            timing_instructions="Pending pharmacist verification",
            food_instructions="Do not take until verified",
            additional_notes="Handwriting is ambiguous or stylized.",
            confidence="unclear",
            confidence_reason="Medication name could not be identified with sufficient confidence. Please verify this with your pharmacist or doctor."
        )

        warning_msg = (
            "Some information in this prescription could not be read with sufficient confidence. "
            "Please confirm the medication and dosage with your doctor or pharmacist before taking it."
        )
        return [unclear_item], True, warning_msg

parser_agent = ParserAgent()
