import io
import json
from typing import Dict, Any, Optional
from PIL import Image
import pypdf
try:
    import winocr
except ImportError:
    winocr = None
from google.adk.agents import LlmAgent
from app.config import settings
from app.services.document_ai_service import document_ai_service
from app.utils.logger import logger

VISION_SYSTEM_PROMPT = """You are Agent 1: OCR & Prescription Vision Extraction Specialist in the RxDecoder multi-agent system.
Your mission is to accurately transcribe and read the text from handwritten or printed medical prescriptions using Google Cloud Document AI OCR.

CRITICAL HEALTHCARE ACCURACY RULES:
1. Extract all text exactly as written on the prescription (doctor info, clinic header, patient section, Rx symbol, medications, strengths, sig/instructions, refills, doctor signature).
2. For handwriting: Carefully assess legibility and token confidence. If a word or number is ambiguous, messy, or unclear, mark it with "[UNCLEAR: ...]". NEVER invent or guess a medicine name or number that you cannot read clearly.
3. Classify sections into clinic header, patient/date info, medication lines, and clinical directions.

Respond with a valid JSON structure:
{
  "raw_transcription": "Complete line-by-line transcription of the prescription document",
  "document_type": "handwritten" | "printed" | "mixed",
  "legibility_score": 0.0 to 1.0,
  "has_unclear_handwriting": true | false,
  "unclear_sections": ["list of specific lines or words that were difficult to decipher"],
  "extracted_sections": {
    "header_and_clinic": "...",
    "patient_and_date": "...",
    "medication_lines": ["line 1", "line 2", "..."],
    "notes_and_signature": "..."
  }
}"""

class VisionAgent(LlmAgent):
    name: str = "vision_agent"
    description: str = "Google Cloud Document AI OCR specialist for reading handwritten and printed prescription documents."
    model: str = settings.default_model
    instruction: str = VISION_SYSTEM_PROMPT

    def __init__(self, **data):
        super().__init__(
            name="vision_agent",
            description="Google Cloud Document AI OCR specialist for reading handwritten and printed prescription documents.",
            instruction=VISION_SYSTEM_PROMPT,
            model=settings.default_model,
            **data,
        )

    async def extract_with_winocr(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> str:
        """
        Extract text from an image using Windows native OCR as local offline fallback.
        """
        logger.info("Agent 1 (VisionAgent): Running Windows OCR fallback...")
        if winocr is None:
            logger.warning("Agent 1: Windows OCR is unavailable in this runtime.")
            return ""
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            result = await winocr.recognize_pil(image, "en")

            extracted_text = ""
            if isinstance(result, dict):
                extracted_text = (result.get("text", "") or "").strip()
            elif isinstance(result, str):
                extracted_text = result.strip()
            elif hasattr(result, "text"):
                extracted_text = (result.text or "").strip()

            if extracted_text:
                logger.info(f"Agent 1: WinOCR extracted {len(extracted_text)} characters.")
                return extracted_text

            return ""
        except Exception as e:
            logger.warning(f"Agent 1: WinOCR fallback failed: {e}")
            return ""

    async def extract_prescription_text(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Extracts prescription text using Google Cloud Document AI as the primary OCR engine.
        Fallback hierarchy:
          1. Google Cloud Document AI OCR
          2. Native PDF text extraction (if PDF)
          3. Windows Native WinOCR (for image uploads)
          4. Structured baseline response
        """
        logger.info(
            f"Agent 1 (VisionAgent): Analyzing prescription document "
            f"(size: {len(image_bytes)} bytes, mime: {mime_type})."
        )

        # =====================================================
        # 1. PRIMARY: GOOGLE CLOUD DOCUMENT AI OCR
        # =====================================================
        doc_ai_result = document_ai_service.process_document(
            image_bytes=image_bytes,
            mime_type=mime_type
        )

        if doc_ai_result and doc_ai_result.get("raw_transcription"):
            logger.info("Agent 1: Google Document AI OCR transcription successful.")
            return doc_ai_result

        logger.info("Agent 1: Document AI unavailable or returned empty. Engaging secondary local fallback...")

        extracted_text = ""
        document_type = "printed"
        legibility = 0.85
        has_unclear = False
        unclear_sections = []

        # =====================================================
        # 2. PDF NATIVE TEXT EXTRACTION
        # =====================================================
        if "pdf" in mime_type.lower():
            logger.info("Agent 1: Attempting native PDF text extraction.")
            try:
                pdf_file = io.BytesIO(image_bytes)
                reader = pypdf.PdfReader(pdf_file)
                pdf_texts = []
                for page in reader.pages:
                    t = page.extract_text()
                    if t and t.strip():
                        pdf_texts.append(t.strip())
                if pdf_texts:
                    extracted_text = "\n\n".join(pdf_texts)
                    logger.info(f"Agent 1: Extracted {len(extracted_text)} characters from PDF.")
            except Exception as e:
                logger.warning(f"Agent 1: PDF extraction failed: {e}")

        # =====================================================
        # 3. WINDOWS OCR FALLBACK FOR IMAGES
        # =====================================================
        if not extracted_text and "image" in mime_type.lower():
            logger.info("Agent 1: Attempting WinOCR fallback for image.")
            extracted_text = await self.extract_with_winocr(image_bytes, mime_type)
            if extracted_text:
                document_type = "mixed"
                legibility = 0.65

        # =====================================================
        # 4. STRUCTURE LOCAL OCR RESULT
        # =====================================================
        if extracted_text and len(extracted_text.strip()) > 5:
            lines = [l.strip() for l in extracted_text.splitlines() if l.strip()]
            header_lines = []
            patient_lines = []
            med_lines = []
            notes_lines = []

            for line in lines:
                l_lower = line.lower()
                if any(kw in l_lower for kw in ["dr.", "clinic", "hospital", "health", "center", "medical", "pharmacy", "md", "do"]):
                    header_lines.append(line)
                elif any(kw in l_lower for kw in ["pt:", "patient", "dob:", "date", "age", "name:"]):
                    patient_lines.append(line)
                elif any(kw in l_lower for kw in ["rx", "tab", "cap", "mg", "po", "bid", "tid", "qid", "daily", "disp", "sig"]):
                    med_lines.append(line)
                else:
                    notes_lines.append(line)

            return {
                "raw_transcription": extracted_text,
                "document_type": document_type,
                "legibility_score": legibility,
                "has_unclear_handwriting": has_unclear,
                "unclear_sections": unclear_sections,
                "extracted_sections": {
                    "header_and_clinic": "\n".join(header_lines) if header_lines else "Clinic Information",
                    "patient_and_date": "\n".join(patient_lines) if patient_lines else "Patient Details",
                    "medication_lines": med_lines if med_lines else lines,
                    "notes_and_signature": "Prescription document captured."
                },
                "ocr_engine": "Local OCR Fallback"
            }

        # =====================================================
        # 5. SAFE BASELINE
        # =====================================================
        logger.warning("Agent 1: All OCR extraction layers exhausted. Returning safe review fallback.")
        return {
            "raw_transcription": (
                "Prescription Document: Extraction pending review. "
                "Unable to decipher text automatically. Pharmacist verification recommended."
            ),
            "document_type": "unknown",
            "legibility_score": 0.0,
            "has_unclear_handwriting": True,
            "unclear_sections": ["Document requires visual pharmacist review."],
            "extracted_sections": {
                "header_and_clinic": "Prescription Document",
                "patient_and_date": "Patient",
                "medication_lines": [],
                "notes_and_signature": "Verification required."
            },
            "ocr_engine": "Fallback"
        }

vision_agent = VisionAgent()
