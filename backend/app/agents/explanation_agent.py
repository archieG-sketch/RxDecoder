import json
import uuid
from typing import List, Dict, Any, Tuple, Optional
from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from app.config import settings
from app.models.schemas import MedicationItem, MedicationChecklistItem, TimeOfDay
from app.utils.logger import logger

EXPLANATION_PROMPT = """You are Agent 6: Human-Friendly Patient Explanation & Medication Schedule Specialist in RxDecoder.
Your mission is to transform complex medical prescription data into warm, crystal-clear, accessible language for patients and elderly caregivers.

RULES:
1. "Simple Explanation": Write a warm, 5th-grade reading level explanation. Completely eliminate confusing Latin medical jargon.
2. "Detailed Medical Information": Provide a comprehensive clinical summary including pharmacological classes and administration specifics.
3. "Daily Medication Checklist": Group daily doses into logical time slots: "Morning", "Afternoon", "Evening", "Bedtime", or "As Needed".
   Include exact food instructions (e.g. "after breakfast", "with plenty of water").
   If any medication had low confidence or uncertain handwriting, set "requires_verification": true and include a verification reminder.
4. "TTS Narration Script": Write a smooth, pleasant, spoken-audio script suitable for text-to-speech reading aloud to an elderly patient.

Input medications:
{medications_json}

Respond ONLY in valid JSON matching this schema:
{{
  "simple_explanation": "A friendly, empathetic explanation...",
  "detailed_explanation": "A detailed clinical summary...",
  "checklist": [
    {{
      "time_of_day": "Morning" | "Afternoon" | "Evening" | "Bedtime" | "As Needed",
      "medication_name": "Medicine Name",
      "dosage": "1 unit",
      "instructions": "Take as directed",
      "food_relation": "With water",
      "requires_verification": false,
      "verification_reason": null
    }}
  ],
  "tts_narration_script": "Spoken audio script..."
}}"""

class ExplanationAgent(LlmAgent):
    name: str = "explanation_agent"
    description: str = "Patient-friendly explanation and checklist specialist for medication instructions."
    model: str = settings.default_model
    instruction: str = EXPLANATION_PROMPT

    def get_client(self) -> Optional[genai.Client]:
        if settings.gemini_api_key and settings.gemini_api_key.startswith("AIzaSy"):
            try:
                return genai.Client(api_key=settings.gemini_api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")
        return None

    async def generate_explanations_and_checklist(
        self, medications: List[MedicationItem]
    ) -> Tuple[str, str, List[MedicationChecklistItem], str]:
        """
        Generates simple and detailed explanations, an interactive daily medication checklist, and a TTS audio script.
        """
        logger.info(f"Agent 6 (ExplanationAgent): Generating patient explanations & checklist for {len(medications)} medication(s).")
        
        if not medications:
            return (
                "No medications were detected in the prescription document.",
                "Clinical parsing did not return active medication lines.",
                [],
                "No medications detected in the document."
            )

        client = self.get_client()
        if client:
            try:
                meds_payload = [
                    {
                        "name": m.name,
                        "generic_name": m.generic_name,
                        "strength": m.strength,
                        "dosage": m.dosage,
                        "frequency": m.frequency,
                        "route": m.route,
                        "duration": m.duration,
                        "timing_instructions": m.timing_instructions,
                        "food_instructions": m.food_instructions,
                        "confidence": m.confidence,
                        "confidence_reason": m.confidence_reason
                    }
                    for m in medications
                ]

                prompt = EXPLANATION_PROMPT.format(medications_json=json.dumps(meds_payload, indent=2))
                response = client.models.generate_content(
                    model=settings.default_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=settings.temperature
                    )
                )

                if response.text:
                    parsed = json.loads(response.text)
                    simple_exp = parsed.get("simple_explanation", "")
                    detailed_exp = parsed.get("detailed_explanation", "")
                    tts_script = parsed.get("tts_narration_script", "")
                    raw_checklist = parsed.get("checklist", [])

                    if simple_exp and raw_checklist:
                        checklist_items: List[MedicationChecklistItem] = []
                        for idx, item in enumerate(raw_checklist):
                            t_slot = item.get("time_of_day", "Morning")
                            if t_slot not in ["Morning", "Afternoon", "Evening", "Bedtime", "As Needed"]:
                                t_slot = "Morning"

                            c_item = MedicationChecklistItem(
                                id=f"chk_{idx + 1}_{uuid.uuid4().hex[:6]}",
                                time_of_day=t_slot,
                                medication_name=item.get("medication_name", "Prescription Medicine"),
                                dosage=item.get("dosage", "1 dose"),
                                instructions=item.get("instructions", "Take as directed"),
                                food_relation=item.get("food_relation", "With water"),
                                requires_verification=item.get("requires_verification", False),
                                verification_reason=item.get("verification_reason"),
                                completed=False
                            )
                            checklist_items.append(c_item)

                        logger.info(f"Agent 6: Successfully generated Gemini explanations & {len(checklist_items)} checklist items.")
                        return simple_exp, detailed_exp, checklist_items, tts_script
            except Exception as e:
                logger.warning(f"Agent 6: Gemini explanation notice ({e}). Generating dynamic clinical explanation.")

        # Dynamic Rule-Based Explanation & Checklist Builder
        return self._generate_dynamic_explanation(medications)

    def _generate_dynamic_explanation(
        self, medications: List[MedicationItem]
    ) -> Tuple[str, str, List[MedicationChecklistItem], str]:
        simple_paragraphs = [
            "Here is your personalized prescription understanding guide:\n"
        ]
        detailed_paragraphs = [
            "**Clinical Prescription Regimen Summary**:\n"
        ]
        checklist: List[MedicationChecklistItem] = []
        tts_lines = [
            "Hello. Here is your daily prescription summary from RxDecoder."
        ]

        for idx, m in enumerate(medications):
            is_unclear = m.confidence in ["low", "unclear"]

            if is_unclear:
                simple_paragraphs.append(
                    f"⚠️ **{m.name}**: The doctor's handwriting for this item could not be identified with certainty. Please have your pharmacist or prescribing doctor verify this medication and dosage before taking it."
                )
                detailed_paragraphs.append(
                    f"• **Line {idx + 1} (Uncertain Confidence)**: Unresolved sig signature. Verification with dispensing pharmacist required."
                )
                tts_lines.append(
                    f"Please note: medication {idx + 1} has unclear handwriting and must be verified with your pharmacist before taking."
                )

                checklist.append(
                    MedicationChecklistItem(
                        id=f"chk_{idx + 1}_{uuid.uuid4().hex[:6]}",
                        time_of_day="Morning",
                        medication_name=f"⚠️ {m.name}",
                        dosage=m.strength,
                        instructions="DO NOT TAKE YET: Have your pharmacist verify the doctor's handwriting",
                        food_relation="Verification Required",
                        requires_verification=True,
                        verification_reason="Handwriting could not be read with high confidence",
                        completed=False
                    )
                )
            else:
                uses_text = m.analysis.uses_summary if m.analysis else "Prescribed by your doctor."
                how_text = m.analysis.how_to_take_plain if m.analysis else f"Take {m.dosage} {m.frequency.lower()}."

                simple_paragraphs.append(
                    f"• **{m.name} ({m.strength})**: {uses_text} {how_text} Duration: {m.duration}."
                )
                detailed_paragraphs.append(
                    f"• **{m.name} {m.strength}**: {m.dosage} | Sig: {m.frequency} | Route: {m.route} | Duration: {m.duration}. {m.analysis.mechanism_summary if m.analysis and m.analysis.mechanism_summary else ''}"
                )
                tts_lines.append(
                    f"For {m.name} {m.strength}: take {m.dosage} {m.frequency.lower()}, {m.food_instructions.lower()}."
                )

                # Generate intelligent time slots based on frequency
                freq_lower = m.frequency.lower()
                timing_lower = m.timing_instructions.lower()

                if "three times" in freq_lower or "tid" in freq_lower:
                    checklist.append(
                        MedicationChecklistItem(
                            id=f"chk_{idx + 1}_m_{uuid.uuid4().hex[:6]}",
                            time_of_day="Morning",
                            medication_name=f"{m.name} {m.strength}",
                            dosage=m.dosage,
                            instructions="Dose 1 of 3",
                            food_relation=m.food_instructions,
                            completed=False
                        )
                    )
                    checklist.append(
                        MedicationChecklistItem(
                            id=f"chk_{idx + 1}_a_{uuid.uuid4().hex[:6]}",
                            time_of_day="Afternoon",
                            medication_name=f"{m.name} {m.strength}",
                            dosage=m.dosage,
                            instructions="Dose 2 of 3 (spaced ~8 hrs after morning dose)",
                            food_relation=m.food_instructions,
                            completed=False
                        )
                    )
                    checklist.append(
                        MedicationChecklistItem(
                            id=f"chk_{idx + 1}_e_{uuid.uuid4().hex[:6]}",
                            time_of_day="Evening",
                            medication_name=f"{m.name} {m.strength}",
                            dosage=m.dosage,
                            instructions="Dose 3 of 3",
                            food_relation=m.food_instructions,
                            completed=False
                        )
                    )
                elif "twice" in freq_lower or "bid" in freq_lower:
                    checklist.append(
                        MedicationChecklistItem(
                            id=f"chk_{idx + 1}_m_{uuid.uuid4().hex[:6]}",
                            time_of_day="Morning",
                            medication_name=f"{m.name} {m.strength}",
                            dosage=m.dosage,
                            instructions="Morning dose (with breakfast)",
                            food_relation=m.food_instructions,
                            completed=False
                        )
                    )
                    checklist.append(
                        MedicationChecklistItem(
                            id=f"chk_{idx + 1}_e_{uuid.uuid4().hex[:6]}",
                            time_of_day="Evening",
                            medication_name=f"{m.name} {m.strength}",
                            dosage=m.dosage,
                            instructions="Evening dose (with dinner)",
                            food_relation=m.food_instructions,
                            completed=False
                        )
                    )
                elif "bedtime" in freq_lower or "qhs" in freq_lower or "night" in timing_lower:
                    checklist.append(
                        MedicationChecklistItem(
                            id=f"chk_{idx + 1}_b_{uuid.uuid4().hex[:6]}",
                            time_of_day="Bedtime",
                            medication_name=f"{m.name} {m.strength}",
                            dosage=m.dosage,
                            instructions="Take at night before sleeping",
                            food_relation=m.food_instructions,
                            completed=False
                        )
                    )
                elif "needed" in freq_lower or "prn" in freq_lower:
                    checklist.append(
                        MedicationChecklistItem(
                            id=f"chk_{idx + 1}_p_{uuid.uuid4().hex[:6]}",
                            time_of_day="As Needed",
                            medication_name=f"{m.name} {m.strength}",
                            dosage=m.dosage,
                            instructions="Only when needed for symptoms (spaced at least 6 hrs apart)",
                            food_relation=m.food_instructions,
                            completed=False
                        )
                    )
                else:
                    checklist.append(
                        MedicationChecklistItem(
                            id=f"chk_{idx + 1}_m_{uuid.uuid4().hex[:6]}",
                            time_of_day="Morning",
                            medication_name=f"{m.name} {m.strength}",
                            dosage=m.dosage,
                            instructions=f"Take {m.frequency.lower()}",
                            food_relation=m.food_instructions,
                            completed=False
                        )
                    )

        # Add daily safety checklist item
        checklist.append(
            MedicationChecklistItem(
                id=f"chk_safety_{uuid.uuid4().hex[:6]}",
                time_of_day="Morning",
                medication_name="Daily Safety & Storage Check",
                dosage="Daily Routine",
                instructions="Review warnings, drink adequate fluids, and keep medicines in a cool, dry place.",
                food_relation="Anytime",
                completed=False
            )
        )

        simple_exp = "\n\n".join(simple_paragraphs)
        detailed_exp = "\n\n".join(detailed_paragraphs)
        tts_script = " ".join(tts_lines)

        return simple_exp, detailed_exp, checklist, tts_script

explanation_agent = ExplanationAgent()
