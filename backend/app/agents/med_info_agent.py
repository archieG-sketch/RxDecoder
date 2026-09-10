import json
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from app.config import settings
from app.models.schemas import MedicationItem, MedicationAnalysis
from app.utils.logger import logger
from app.utils.medical_kb import lookup_drug_info

MED_INFO_PROMPT = """You are Agent 4: Medication Knowledge & Clinical Information Specialist in RxDecoder.
Your mission is to provide accurate, reliable, objective pharmaceutical information for the provided medications.

CRITICAL HEALTHCARE BOUNDARIES:
1. Explain what each medicine is generally used for in simple, everyday language.
2. Clearly translate how to take it into simple, actionable steps.
3. List common, mild side effects (e.g. mild nausea, dry mouth, tiredness).
4. Separate IMPORTANT WARNINGS (e.g. avoid alcohol, take with plenty of water, complete full antibiotic course) from ordinary side effects.
5. Identify SERIOUS SYMPTOMS requiring prompt medical attention (e.g. facial swelling, wheezing, severe rash, blood in stool) without diagnosing any disease.
6. Note any substance, allergen, or inactive ingredient warnings when applicable.
7. Include a brief pharmacological class or mechanism summary for Detailed Medical mode.

Input medications:
{medications_json}

Respond ONLY with valid JSON mapping each medication name to its MedicationAnalysis object:
{{
  "medication_analyses": {{
    "Medicine Name": {{
      "uses_summary": "Simple explanation of primary uses...",
      "how_to_take_plain": "Clear steps on taking the prescribed dose...",
      "common_side_effects": ["Mild stomach upset", "Nausea", "Headache"],
      "important_warnings": ["Take full course as prescribed", "Do not skip doses", "Avoid alcohol while taking this medicine"],
      "serious_symptoms": ["Hives or skin rash", "Difficulty breathing or swallowing", "Swelling of lips, tongue, or face"],
      "substance_allergy_warnings": ["Avoid if you have known penicillin allergies."],
      "mechanism_summary": "Beta-lactam antibiotic that inhibits bacterial cell wall synthesis."
    }}
  }}
}}"""

class MedInfoAgent(LlmAgent):
    name: str = "med_info_agent"
    description: str = "Medication knowledge enrichment specialist for clinical guidance and warnings."
    model: str = settings.default_model
    instruction: str = MED_INFO_PROMPT

    def get_client(self) -> Optional[genai.Client]:
        if settings.gemini_api_key and settings.gemini_api_key.startswith("AIzaSy"):
            try:
                return genai.Client(api_key=settings.gemini_api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")
        return None

    async def enrich_medications(self, medications: List[MedicationItem]) -> List[MedicationItem]:
        """
        Enriches a list of MedicationItem instances with detailed MedicationAnalysis information.
        """
        logger.info(f"Agent 4 (MedInfoAgent): Enriching {len(medications)} medication(s) with clinical guidance.")
        
        if not medications:
            return medications

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
                        "food_instructions": m.food_instructions,
                        "timing_instructions": m.timing_instructions
                    }
                    for m in medications
                ]
                prompt = MED_INFO_PROMPT.format(medications_json=json.dumps(meds_payload, indent=2))
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
                    analyses = parsed.get("medication_analyses", {})
                    
                    for med in medications:
                        analysis_data = analyses.get(med.name) or analyses.get(med.generic_name or "")
                        if not analysis_data:
                            for k, v in analyses.items():
                                if k.lower() in med.name.lower() or (med.generic_name and k.lower() in med.generic_name.lower()):
                                    analysis_data = v
                                    break

                        if analysis_data:
                            med.analysis = MedicationAnalysis(
                                uses_summary=analysis_data.get("uses_summary", "Commonly used as prescribed by your physician."),
                                how_to_take_plain=analysis_data.get("how_to_take_plain", f"Take {med.dosage} ({med.strength}) {med.frequency.lower()}."),
                                common_side_effects=analysis_data.get("common_side_effects", ["Mild stomach upset", "Nausea"]),
                                important_warnings=analysis_data.get("important_warnings", ["Follow prescribed duration closely."]),
                                serious_symptoms=analysis_data.get("serious_symptoms", ["Severe allergic reactions (rash, facial swelling, breathing difficulty)"]),
                                substance_allergy_warnings=analysis_data.get("substance_allergy_warnings", []),
                                mechanism_summary=analysis_data.get("mechanism_summary")
                            )
                        else:
                            med.analysis = self._generate_kb_analysis(med)

                    logger.info("Agent 4: Successfully enriched medications via Gemini.")
                    return medications
            except Exception as e:
                logger.warning(f"Agent 4: Gemini enrichment notice ({e}). Using verified clinical knowledge base.")

        # Enrich using Comprehensive Clinical Knowledge Base
        for med in medications:
            med.analysis = self._generate_kb_analysis(med)
        return medications

    def _generate_kb_analysis(self, med: MedicationItem) -> MedicationAnalysis:
        # Search clinical KB
        search_term = f"{med.name} {med.generic_name or ''}"
        kb_info = lookup_drug_info(search_term)

        if kb_info:
            return MedicationAnalysis(
                uses_summary=f"{kb_info['generic_name']} is a {kb_info['class']} commonly used for: {kb_info['uses']}",
                how_to_take_plain=f"Take {med.dosage} ({med.strength}) by mouth {med.frequency.lower()}. {med.food_instructions}. {kb_info['how_to_take']}",
                common_side_effects=kb_info.get("side_effects", ["Mild stomach upset", "Nausea"]),
                important_warnings=kb_info.get("warnings", ["Take exactly as prescribed."]),
                serious_symptoms=kb_info.get("serious_symptoms", ["Severe rash, swelling of the face, or breathing difficulty"]),
                substance_allergy_warnings=kb_info.get("allergies", []),
                mechanism_summary=f"{kb_info['class']} — {kb_info.get('mechanism', '')}"
            )

        if med.confidence in ["low", "unclear"]:
            return MedicationAnalysis(
                uses_summary="Handwriting on this prescription entry could not be identified with certainty. Requires verification with your pharmacist.",
                how_to_take_plain="DO NOT TAKE UNTIL VERIFIED: Show this prescription to your pharmacist or prescribing doctor to confirm the medicine name and dosage.",
                common_side_effects=["Side effects depend on the exact verified medication"],
                important_warnings=["CRITICAL: Do not take unverified prescription entries before pharmacist confirmation."],
                serious_symptoms=["Contact your doctor or emergency services if you experience any severe adverse symptoms."],
                substance_allergy_warnings=["Inform your pharmacist of all existing allergies before filling."],
                mechanism_summary="Unverified clinical entry pending pharmacist review."
            )

        # Standard generic guidance
        return MedicationAnalysis(
            uses_summary=f"{med.name} ({med.strength}) is prescribed for your specific clinical treatment.",
            how_to_take_plain=f"Take {med.dosage} by mouth {med.frequency.lower()} {med.food_instructions.lower()}.",
            common_side_effects=["Mild stomach upset", "Drowsiness or dizziness", "Mild headache"],
            important_warnings=[
                "Take exactly as prescribed by your doctor.",
                "Do not abruptly stop taking this medication without consulting your doctor.",
                "Keep stored in a cool, dry place away from children."
            ],
            serious_symptoms=[
                "Sudden skin rash, facial swelling, or breathing difficulty (signs of severe allergic reaction)",
                "Severe dizziness or fainting"
            ],
            substance_allergy_warnings=["Inform your pharmacist of all known drug or food allergies."],
            mechanism_summary="Prescription pharmaceutical therapeutic agent."
        )

med_info_agent = MedInfoAgent()
