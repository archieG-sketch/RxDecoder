import io
import asyncio
import pytest
from PIL import Image, ImageDraw
from app.services.gcs_service import GCSService, gcs_service
from app.services.document_ai_service import DocumentAIService, document_ai_service
from app.agents.vision_agent import vision_agent
from app.services.orchestrator import orchestrator
from app.config import settings

def create_dummy_prescription_image() -> bytes:
    """Creates a sample test prescription image with text."""
    img = Image.new("RGB", (500, 300), color="white")
    d = ImageDraw.Draw(img)
    d.text((20, 20), "Metro Clinic - Dr. Vance MD", fill="black")
    d.text((20, 50), "Pt: John Doe, DOB: 01/15/1980", fill="black")
    d.text((20, 90), "Rx: Amoxicillin 500mg", fill="black")
    d.text((20, 120), "Sig: 1 cap PO TID x 10 days", fill="black")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_gcs_service_init():
    service = GCSService()
    assert settings.raw_prescriptions_bucket == "raw-prescriptions"
    assert settings.sanitized_prescriptions_bucket == "sanitized-prescriptions"
    status = service.check_bucket_status()
    assert "raw_bucket" in status
    assert "sanitized_bucket" in status

def test_document_ai_service_init():
    doc_service = DocumentAIService()
    assert doc_service is not None
    assert settings.document_ai_location in ["us", "eu"]
    assert settings.gcp_project_id == "rxdecoded"

def test_vision_agent_extraction():
    img_bytes = create_dummy_prescription_image()
    result = asyncio.run(vision_agent.extract_prescription_text(img_bytes, mime_type="image/jpeg"))
    assert "raw_transcription" in result
    assert "legibility_score" in result
    assert "extracted_sections" in result
    assert "ocr_engine" in result

def test_orchestrator_end_to_end():
    img_bytes = create_dummy_prescription_image()
    response = asyncio.run(orchestrator.decode_prescription_image(
        image_bytes=img_bytes,
        mime_type="image/jpeg",
        file_name="test_rx.jpg"
    ))
    assert response.success is True
    assert response.session_id.startswith("sess_")
    assert response.phi_report is not None
    assert response.phi_report.sanitized is True
    assert response.ocr_engine is not None
    assert len(response.checklist) > 0
