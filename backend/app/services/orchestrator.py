import time
import uuid
from typing import Dict, Any, Optional
from google.adk.agents import SequentialAgent
from app.models.schemas import PrescriptionDecodeResponse, PHISanitizationReport
from app.agents.vision_agent import vision_agent
from app.agents.phi_agent import phi_agent
from app.agents.parser_agent import parser_agent
from app.agents.med_info_agent import med_info_agent
from app.agents.safety_agent import safety_agent
from app.agents.explanation_agent import explanation_agent
from app.services.gcs_service import gcs_service
from app.utils.logger import logger

class PrescriptionOrchestrator(SequentialAgent):
    """
    ADK-backed orchestration for the clinical pipeline:
    0. GCS Raw Storage (Store original document in 'raw-prescriptions' bucket)
    1. VisionAgent (Google Cloud Document AI OCR)
    2. PHIAgent (HIPAA Safe Harbor PHI Sanitization)
    2.5 GCS Sanitized Storage (Store non-PHI data in 'sanitized-prescriptions' bucket)
    3. ParserAgent (Sig & Medication Parsing)
    4. MedInfoAgent (Clinical Knowledge Retrieval)
    5. SafetyAgent (Interaction & Safety Evaluation)
    6. ExplanationAgent (Simplification & Daily Schedule)
    """

    def __init__(self):
        super().__init__(
            name="prescription_pipeline",
            description="Sequential ADK orchestration for prescription processing with GCS buckets and Google Document AI OCR.",
            sub_agents=[
                vision_agent,
                phi_agent,
                parser_agent,
                med_info_agent,
                safety_agent,
                explanation_agent,
            ],
        )

    async def decode_prescription_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        file_name: Optional[str] = None
    ) -> PrescriptionDecodeResponse:
        start_time = time.time()
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        logger.info(f"--- Starting Prescription Orchestration [Session: {session_id}] ---")

        # Stage 0: GCS Raw Prescription Storage
        logger.info("Pipeline Stage 0: Storing raw prescription in 'raw-prescriptions' bucket.")
        raw_storage_uri = gcs_service.upload_raw_prescription(
            session_id=session_id,
            file_name=file_name or "prescription.jpg",
            file_bytes=image_bytes,
            mime_type=mime_type
        )

        # Stage 1: Vision / OCR via Google Document AI
        logger.info("Pipeline Stage 1: Reading prescription via Vision Agent (Google Document AI OCR).")
        vision_result = await vision_agent.extract_prescription_text(image_bytes, mime_type)
        raw_text = vision_result.get("raw_transcription", "")
        has_unclear_handwriting = vision_result.get("has_unclear_handwriting", False)
        ocr_engine = vision_result.get("ocr_engine", "Google Document AI")

        # Stage 2: PHI Sanitization (Strictly separates original document from downstream AI)
        logger.info("Pipeline Stage 2: Protecting personal health information via PHI Agent.")
        sanitized_text, phi_report = await phi_agent.sanitize_prescription(raw_text)

        # Stage 2.5: GCS Sanitized Non-PHI Storage
        logger.info("Pipeline Stage 2.5: Storing de-identified non-PHI payload in 'sanitized-prescriptions' bucket.")
        sanitized_storage_uri = gcs_service.upload_sanitized_prescription(
            session_id=session_id,
            file_name=file_name or "prescription.jpg",
            sanitized_text=sanitized_text,
            phi_report=phi_report.model_dump() if hasattr(phi_report, "model_dump") else phi_report.dict()
        )

        # Stage 3: Prescription Parsing
        logger.info("Pipeline Stage 3: Extracting structured medication information via Parser Agent.")
        medications, parser_unclear_flag, uncertainty_summary = await parser_agent.parse_prescription(sanitized_text)
        if parser_unclear_flag:
            has_unclear_handwriting = True

        # Stage 4: Medication Knowledge Enrichment
        logger.info("Pipeline Stage 4: Retrieving clinical guidance via MedInfo Agent.")
        enriched_medications = await med_info_agent.enrich_medications(medications)

        # Stage 5: Safety & Interaction Review
        logger.info("Pipeline Stage 5: Checking interactions & uncertainty via Safety Agent.")
        interactions, safety_unclear_flag, uncertainty_warning = await safety_agent.evaluate_safety(
            enriched_medications, has_unclear_handwriting
        )

        # Stage 6: Human-Friendly Explanation & Daily Schedule Checklist
        logger.info("Pipeline Stage 6: Preparing patient-friendly explanation & checklist via Explanation Agent.")
        simple_exp, detailed_exp, checklist, tts_script = await explanation_agent.generate_explanations_and_checklist(
            enriched_medications
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"--- Completed Prescription Orchestration in {elapsed_ms} ms ---")

        return PrescriptionDecodeResponse(
            success=True,
            session_id=session_id,
            original_file_name=file_name or "uploaded_prescription.jpg",
            file_type="image" if "image" in mime_type.lower() else "pdf",
            phi_report=phi_report,
            raw_ocr_summary=f"Transcribed {len(enriched_medications)} medication item(s) from document using {ocr_engine}.",
            medications=enriched_medications,
            interactions=interactions,
            checklist=checklist,
            simple_explanation=simple_exp,
            detailed_explanation=detailed_exp,
            has_uncertain_handwriting=safety_unclear_flag,
            uncertainty_warning=uncertainty_warning if safety_unclear_flag else None,
            raw_storage_uri=raw_storage_uri,
            sanitized_storage_uri=sanitized_storage_uri,
            ocr_engine=ocr_engine,
            tts_narration_script=tts_script,
            processing_time_ms=elapsed_ms
        )

orchestrator = PrescriptionOrchestrator()
