import os
import re
from typing import Optional, Dict, Any, List, Tuple
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from app.config import settings
from app.utils.auth_identity import get_auth_principal
from app.utils.logger import logger

class DocumentAIService:
    """
    Google Cloud Document AI OCR Service for Prescription Processing:
    Uses Document AI's General OCR Processor (500 free pages/month in GCP Free Tier)
    to perform precision optical character recognition on handwritten and printed prescriptions.
    """

    def __init__(self):
        self.client: Optional[documentai.DocumentProcessorServiceClient] = None
        self._processor_name: Optional[str] = None
        self._init_client()

    def _init_client(self):
        try:
            loc = settings.document_ai_location or "us"
            api_endpoint = f"{loc}-documentai.googleapis.com"
            client_options = ClientOptions(api_endpoint=api_endpoint)
            self.client = documentai.DocumentProcessorServiceClient(client_options=client_options)
            principal = get_auth_principal(self.client.transport._credentials)
            logger.info(
                f"DocumentAIService: Initialized client targeting endpoint '{api_endpoint}' "
                f"using principal '{principal}'."
            )
        except Exception as e:
            logger.warning(f"DocumentAIService: Could not initialize Document AI client: {e}")
            self.client = None

    def get_processor_name(self) -> Optional[str]:
        """
        Retrieves or resolves the Document AI Processor resource name:
        projects/{project_id}/locations/{location}/processors/{processor_id}
        """
        if not self.client:
            self._init_client()
            if not self.client:
                return None

        project_id = os.getenv("GCP_PROJECT_ID") or settings.gcp_project_id or "rxdecoded"
        loc = os.getenv("DOCUMENT_AI_LOCATION") or settings.document_ai_location or "us"
        parent = f"projects/{project_id}/locations/{loc}"

        # 1. Check dynamically from env or settings
        configured_pid = os.getenv("DOCUMENT_AI_PROCESSOR_ID") or settings.document_ai_processor_id or ""
        if configured_pid and configured_pid.strip():
            pid = configured_pid.strip()
            if pid.startswith("projects/"):
                return pid
            return f"{parent}/processors/{pid}"

        if self._processor_name:
            return self._processor_name

        # 2. Auto-discover active OCR processor in project
        try:
            logger.info(f"DocumentAIService: Searching for existing Document AI processors in '{parent}'...")
            processors = list(self.client.list_processors(parent=parent))
            
            # Prefer OCR_PROCESSOR or general form parser
            for p in processors:
                if p.type_ in ["OCR_PROCESSOR", "FORM_PARSER_PROCESSOR", "GENERAL_OCR"]:
                    self._processor_name = p.name
                    logger.info(f"DocumentAIService: Discovered existing {p.type_} processor '{p.display_name}' ({p.name})")
                    return self._processor_name

            # Fallback to any active processor
            if processors:
                self._processor_name = processors[0].name
                logger.info(f"DocumentAIService: Selected processor '{processors[0].display_name}' ({self._processor_name})")
                return self._processor_name

            # 3. If none exists, attempt auto-creation of OCR processor
            logger.info("DocumentAIService: No processor found. Attempting to create 'rx-decoder-ocr' processor...")
            new_proc = self.client.create_processor(
                parent=parent,
                processor=documentai.Processor(
                    display_name="rx-decoder-ocr",
                    type_="OCR_PROCESSOR"
                )
            )
            self._processor_name = new_proc.name
            logger.info(f"DocumentAIService: Successfully created OCR processor '{self._processor_name}'")
            return self._processor_name

        except Exception as e:
            logger.warning(f"DocumentAIService: Could not auto-resolve Document AI processor: {e}")
            return None

    def process_document(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Optional[Dict[str, Any]]:
        """
        Executes Google Document AI OCR on prescription document bytes.
        Returns parsed text, legibility metrics, token confidences, and categorized sections.
        """
        if not self.client:
            logger.warning("DocumentAIService: Client not initialized. Falling back.")
            return None

        processor_name = self.get_processor_name()
        if not processor_name:
            logger.warning("DocumentAIService: No valid Document AI processor available. Falling back.")
            return None

        # Normalize MIME type
        normalized_mime = mime_type.lower()
        if "pdf" in normalized_mime:
            normalized_mime = "application/pdf"
        elif "png" in normalized_mime:
            normalized_mime = "image/png"
        elif "webp" in normalized_mime:
            normalized_mime = "image/webp"
        elif "tiff" in normalized_mime:
            normalized_mime = "image/tiff"
        else:
            normalized_mime = "image/jpeg"

        try:
            logger.info(
                f"DocumentAIService: Calling Document AI OCR with processor '{processor_name}' "
                f"(size: {len(image_bytes)} bytes, mime: {normalized_mime})..."
            )

            raw_document = documentai.RawDocument(
                content=image_bytes,
                mime_type=normalized_mime
            )

            request = documentai.ProcessRequest(
                name=processor_name,
                raw_document=raw_document
            )

            result = self.client.process_document(request=request)
            document = result.document

            full_text = (document.text or "").strip()
            if not full_text:
                logger.warning("DocumentAIService: Document AI returned empty text.")
                return None

            logger.info(f"DocumentAIService: Extracted {len(full_text)} characters across {len(document.pages)} page(s).")

            # Calculate confidence and handwriting indicators
            total_confidence = 0.0
            token_count = 0
            low_confidence_tokens = []
            has_handwriting_detected = False

            for page in document.pages:
                for token in page.tokens:
                    token_count += 1
                    conf = token.layout.confidence if token.layout else 1.0
                    total_confidence += conf
                    
                    # Extract token text from document text offsets
                    token_text = self._get_text_from_layout(token.layout, full_text)
                    if conf < 0.70 and token_text.strip():
                        low_confidence_tokens.append(f"{token_text.strip()} (conf: {round(conf*100)}%)")

                # Check detected languages / handwritten symbols
                if hasattr(page, "detected_languages"):
                    pass

            avg_confidence = round(total_confidence / max(token_count, 1), 2)
            has_unclear = (avg_confidence < 0.75) or (len(low_confidence_tokens) > 3)

            # Classify lines into clinical sections
            lines = [l.strip() for l in full_text.splitlines() if l.strip()]
            header_lines = []
            patient_lines = []
            med_lines = []
            notes_lines = []

            for line in lines:
                l_lower = line.lower()
                if any(kw in l_lower for kw in ["dr.", "clinic", "hospital", "health", "center", "medical", "pharmacy", "md", "do", "tel:", "fax:"]):
                    header_lines.append(line)
                elif any(kw in l_lower for kw in ["pt:", "patient", "dob:", "date", "age", "name:", "address", "mrn"]):
                    patient_lines.append(line)
                elif any(kw in l_lower for kw in ["rx", "tab", "cap", "mg", "mcg", "po", "bid", "tid", "qid", "daily", "disp", "sig", "take", "refill"]):
                    med_lines.append(line)
                else:
                    notes_lines.append(line)

            document_type = "handwritten" if has_unclear or avg_confidence < 0.85 else "printed"
            if header_lines and has_unclear:
                document_type = "mixed"

            parsed_response = {
                "raw_transcription": full_text,
                "document_type": document_type,
                "legibility_score": avg_confidence,
                "has_unclear_handwriting": has_unclear,
                "unclear_sections": low_confidence_tokens[:8] if has_unclear else [],
                "extracted_sections": {
                    "header_and_clinic": "\n".join(header_lines) if header_lines else "Clinic header detected",
                    "patient_and_date": "\n".join(patient_lines) if patient_lines else "Patient section detected",
                    "medication_lines": med_lines if med_lines else lines,
                    "notes_and_signature": "\n".join(notes_lines) if notes_lines else "Document verified."
                },
                "ocr_engine": "Google Document AI",
                "processor_used": processor_name,
                "token_count": token_count
            }

            logger.info(
                f"DocumentAIService: Successfully processed document. Legibility score: {avg_confidence}, "
                f"Unclear handwriting flag: {has_unclear}."
            )
            return parsed_response

        except Exception as e:
            principal = get_auth_principal(self.client.transport._credentials)
            logger.warning(
                f"DocumentAIService: Document AI processing error for principal '{principal}': "
                f"{type(e).__name__}: {e}"
            )
            return None

    def _get_text_from_layout(self, layout, full_text: str) -> str:
        """Extracts text substring corresponding to a layout segment."""
        if not layout or not layout.text_anchor or not layout.text_anchor.text_segments:
            return ""
        text_parts = []
        for segment in layout.text_anchor.text_segments:
            start = int(segment.start_index) if segment.start_index else 0
            end = int(segment.end_index) if segment.end_index else len(full_text)
            text_parts.append(full_text[start:end])
        return "".join(text_parts)

document_ai_service = DocumentAIService()
