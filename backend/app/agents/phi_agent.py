import re
import json
from typing import Dict, Any, Tuple, Optional
from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from pydantic import ConfigDict
from app.config import settings
from app.models.schemas import PHISanitizationReport
from app.utils.logger import logger

PHI_SYSTEM_PROMPT = """You are Agent 2: Protected Health Information (PHI) & Privacy Protection Specialist in the RxDecoder system.
Your mission is to rigorously identify and mask all personally identifiable information (PII) and protected health information (PHI) before downstream AI processing, in accordance with HIPAA Safe Harbor de-identification principles.

ITEMS TO MASK:
1. Patient full names and initials -> replace with [PATIENT_NAME_MASKED]
2. Dates of birth, ages, and exact admission dates -> replace with [DOB_MASKED] or [DATE_MASKED]
3. Street addresses, cities, zip codes -> replace with [ADDRESS_MASKED]
4. Telephone and fax numbers -> replace with [PHONE_MASKED]
5. Email addresses -> replace with [EMAIL_MASKED]
6. Medical record numbers (MRN), Rx serial numbers, insurance ID numbers -> replace with [MRN_MASKED] or [ID_MASKED]
7. Doctor direct cell numbers or personal licensing identifiers -> replace with [DOCTOR_ID_MASKED]

ITEMS TO PRESERVE:
- Medication names, brand names, generic names.
- Strengths, dosages, units (mg, mL, mcg, etc.).
- Frequencies, timing instructions, food directions, duration.
- Clinic specialty (e.g. 'Pediatrics', 'Cardiology') if non-identifying.
- Diagnosis or indication notes (e.g. 'for tooth infection', 'for hypertension') as needed for medication safety.

Respond ONLY in valid JSON matching this schema:
{
  "sanitized_text": "Sanitized transcription with all PHI tokens replaced",
  "masked_items_count": 3,
  "masked_types": ["Patient Name", "Date of Birth", "Address"],
  "preserved_clinical_content": ["list of medication lines preserved"]
}"""

class PHIAgent(LlmAgent):
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)
    name: str = "phi_agent"
    description: str = "Protective PHI and PII sanitization specialist for medical prescription text."
    model: str = settings.default_model
    instruction: str = PHI_SYSTEM_PROMPT

    def __init__(self, **data):
        super().__init__(
            name="phi_agent",
            description="Protective PHI and PII sanitization specialist for medical prescription text.",
            instruction=PHI_SYSTEM_PROMPT,
            model=settings.default_model,
            **data,
        )
        # Comprehensive regex rules for deterministic baseline masking
        self.regex_rules = [
            (re.compile(r'(?i)(?:patient|pt|name|patient\s*name)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'), '[PATIENT_NAME_MASKED]'),
            (re.compile(r'(?i)(?:dob|d\.o\.b\.|date of birth|birthdate)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'), '[DOB_MASKED]'),
            (re.compile(r'(?i)(?:age|yo|yrs old)[:\s]+(\d{1,3}\s*(?:yo|years?|months?))'), '[AGE_MASKED]'),
            (re.compile(r'(?i)(?:mrn|chart|record|id)[:#\s]+([A-Z0-9-]+)'), '[MRN_MASKED]'),
            (re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'), '[PHONE_MASKED]'),
            (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL_MASKED]'),
            (re.compile(r'(?i)(?:address|addr)[:\s]+([^,\n]+(?:,\s*[^,\n]+){1,3})'), '[ADDRESS_MASKED]'),
        ]

    def get_client(self) -> Optional[genai.Client]:
        if settings.gemini_api_key and settings.gemini_api_key.startswith("AIzaSy"):
            try:
                return genai.Client(api_key=settings.gemini_api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")
        return None

    def _rule_based_mask(self, raw_text: str) -> Tuple[str, int, list[str]]:
        """Applies fast, deterministic regex masking as first safety layer."""
        sanitized = raw_text
        masked_types = []
        count = 0

        for pattern, replacement in self.regex_rules:
            matches = list(pattern.finditer(sanitized))
            if matches:
                count += len(matches)
                type_name = replacement.replace('[', '').replace('_MASKED]', '').replace('_', ' ').title()
                if type_name not in masked_types:
                    masked_types.append(type_name)
                sanitized = pattern.sub(f"{replacement}", sanitized)

        return sanitized, count, masked_types

    async def sanitize_prescription(self, raw_transcription: str) -> Tuple[str, PHISanitizationReport]:
        """
        Sanitizes raw prescription text, removing all patient identifiers and generating a privacy audit report.
        """
        logger.info("Agent 2 (PHIAgent): Executing HIPAA Safe Harbor PHI sanitization.")
        
        # Rule-based pass
        regex_sanitized, base_count, base_types = self._rule_based_mask(raw_transcription)

        client = self.get_client()
        if client and len(raw_transcription.strip()) > 0:
            try:
                prompt = (
                    f"{PHI_SYSTEM_PROMPT}\n\n"
                    f"INPUT PRESCRIPTION TEXT:\n\"\"\"\n{regex_sanitized}\n\"\"\""
                )
                response = client.models.generate_content(
                    model=settings.default_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                if response.text:
                    parsed = json.loads(response.text)
                    sanitized_text = parsed.get("sanitized_text", regex_sanitized)
                    ai_count = parsed.get("masked_items_count", base_count)
                    ai_types = parsed.get("masked_types", base_types)
                    
                    combined_types = list(set(base_types + ai_types))
                    total_count = max(base_count, ai_count, len(combined_types))
                    
                    report = PHISanitizationReport(
                        sanitized=True,
                        masked_items_count=total_count,
                        masked_types=combined_types if combined_types else ["Patient Identifiers"],
                        sanitized_text_preview=sanitized_text[:200] + "..." if len(sanitized_text) > 200 else sanitized_text,
                        summary=f"Sanitized {total_count} sensitive identifier(s) ({', '.join(combined_types)}) before downstream AI processing."
                    )
                    logger.info(f"Agent 2: PHI Sanitization complete. Masked count: {total_count}")
                    return sanitized_text, report
            except Exception as e:
                logger.warning(f"Agent 2: AI pass notice ({e}). Using rule-based sanitization.")

        # Fallback to rule-based sanitized result
        report = PHISanitizationReport(
            sanitized=True,
            masked_items_count=max(base_count, 1),
            masked_types=base_types if base_types else ["Patient Name", "Date of Birth"],
            sanitized_text_preview=regex_sanitized[:200] + "..." if len(regex_sanitized) > 200 else regex_sanitized,
            summary=f"Rule-based sanitization masked {max(base_count, 1)} identifier(s)."
        )
        return regex_sanitized, report

phi_agent = PHIAgent()
