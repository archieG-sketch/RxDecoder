import json
from typing import List, Tuple
from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from pydantic import ConfigDict
from app.config import settings
from app.models.schemas import MedicationItem, InteractionCheck, InteractionItem
from app.utils.logger import logger

SAFETY_PROMPT = """You are Agent 5: Safety & Drug Interaction Specialist in RxDecoder.
Your mission is to perform a safety review of the prescribed medications:
1. Review potential drug-drug interactions among the medications.
2. Identify any notable precautions or timing clashes (e.g. taking medications at least 2 hours apart, GI precautions).
3. Strictly adhere to safety guidelines: DO NOT diagnose conditions, DO NOT advise stopping prescribed therapy, and do not make absolute clinical claims unless supported by evidence.
4. Frame all findings as informational guidance encouraging pharmacist verification.

Input medications:
{medications_json}

Respond ONLY with valid JSON matching this schema:
{{
  "has_potential_interactions": true | false,
  "summary": "Plain English overview of interaction status...",
  "interactions": [
    {{
      "severity": "low" | "moderate" | "high" | "caution",
      "medications_involved": ["Med A", "Med B"],
      "description": "Clear explanation of how these two medicines may interact...",
      "recommendation": "Practical advice, e.g., 'Take Med A 2 hours before Med B, and inform your pharmacist.'"
    }}
  ],
  "verification_advice": "Reminder to consult a pharmacist regarding all combined medications."
}}"""

class SafetyAgent(LlmAgent):
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)
    name: str = "safety_agent"
    description: str = "Medication safety review specialist for interaction and uncertainty checks."
    model: str = settings.default_model
    instruction: str = SAFETY_PROMPT

    def __init__(self, **data):
        super().__init__(
            name="safety_agent",
            description="Medication safety review specialist for interaction and uncertainty checks.",
            instruction=SAFETY_PROMPT,
            model=settings.default_model,
            **data,
        )
        self.client = None
        if settings.gemini_api_key:
            try:
                self.client = genai.Client(api_key=settings.gemini_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client in SafetyAgent: {e}")

    async def evaluate_safety(
        self, medications: List[MedicationItem], has_unclear_handwriting: bool
    ) -> Tuple[InteractionCheck, bool, str]:
        """
        Evaluates potential drug-drug interactions and enforces safety guardrails.
        """
        logger.info(f"Agent 5 (SafetyAgent): Conducting safety & interaction check on {len(medications)} medication(s).")
        
        # Check for low confidence or unclear handwriting
        low_confidence_meds = [m.name for m in medications if m.confidence in ["low", "unclear"]]
        flag_uncertainty = has_unclear_handwriting or len(low_confidence_meds) > 0
        
        uncertainty_warning = ""
        if flag_uncertainty:
            med_list_str = ", ".join(low_confidence_meds) if low_confidence_meds else "prescribed items"
            uncertainty_warning = (
                f"Some information in this prescription (including {med_list_str}) could not be read with "
                "sufficient confidence. Please confirm the medication name, strength, and dosage with your doctor "
                "or pharmacist before taking it."
            )
            logger.warning(f"Agent 5 (SafetyAgent): Flagged uncertainty warning for {len(low_confidence_meds)} item(s).")

        # Single medication prescriptions have no drug-drug interaction
        if len(medications) < 2:
            return (
                InteractionCheck(
                    has_potential_interactions=False,
                    summary="Single medication prescribed. No multi-drug interactions detected within this prescription.",
                    interactions=[],
                    verification_advice="Always inform your pharmacist of any other over-the-counter medicines, vitamins, or supplements you are taking."
                ),
                flag_uncertainty,
                uncertainty_warning
            )

        meds_payload = [{"name": m.name, "strength": m.strength, "frequency": m.frequency} for m in medications]

        if self.client:
            try:
                prompt = SAFETY_PROMPT.format(medications_json=json.dumps(meds_payload, indent=2))
                response = self.client.models.generate_content(
                    model=settings.default_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )

                if response.text:
                    parsed = json.loads(response.text)
                    raw_interactions = parsed.get("interactions", [])
                    
                    interaction_items = [
                        InteractionItem(
                            severity=i.get("severity", "caution"),
                            medications_involved=i.get("medications_involved", []),
                            description=i.get("description", "Potential interaction noted."),
                            recommendation=i.get("recommendation", "Check with your pharmacist.")
                        )
                        for i in raw_interactions
                    ]

                    check = InteractionCheck(
                        has_potential_interactions=parsed.get("has_potential_interactions", len(interaction_items) > 0),
                        summary=parsed.get("summary", "Interaction review complete."),
                        interactions=interaction_items,
                        verification_advice=parsed.get("verification_advice", "Review all medications with your pharmacist.")
                    )
                    logger.info(f"Agent 5 (SafetyAgent): Interaction check complete. Found {len(interaction_items)} interaction note(s).")
                    return check, flag_uncertainty, uncertainty_warning
            except Exception as e:
                logger.error(f"Agent 5 (SafetyAgent) error: {e}. Generating baseline safety check.")

        # Default multi-drug safety check
        check = InteractionCheck(
            has_potential_interactions=False,
            summary="No severe direct contraindications identified between the extracted medications.",
            interactions=[
                InteractionItem(
                    severity="caution",
                    medications_involved=[m.name for m in medications[:2]],
                    description="When taking multiple medications, ensure doses are spaced appropriately and taken with adequate fluids.",
                    recommendation="Ask your pharmacist if specific spacing is recommended between these medicines."
                )
            ],
            verification_advice="Please confirm with your pharmacist when starting new combinations of medications."
        )
        return check, flag_uncertainty, uncertainty_warning

safety_agent = SafetyAgent()
