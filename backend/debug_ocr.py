"""
Debug script to test the Google Document AI OCR and GCS bucket pipeline step-by-step.
Usage: python debug_ocr.py <path-to-prescription-file>
"""

import sys
import io
import json
import asyncio
from pathlib import Path
from PIL import Image

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from app.config import settings
from app.services.gcs_service import gcs_service
from app.services.document_ai_service import document_ai_service
from app.agents.vision_agent import vision_agent
from app.agents.phi_agent import phi_agent
from app.agents.parser_agent import parser_agent
from app.utils.logger import logger

def test_gcs_raw_upload(file_name: str, file_bytes: bytes, mime_type: str) -> str:
    """Test GCS Raw Prescription Upload"""
    print("\n=== STEP 1: GCS Raw Prescription Bucket Upload ===")
    session_id = "debug_sess_001"
    uri = gcs_service.upload_raw_prescription(
        session_id=session_id,
        file_name=file_name,
        file_bytes=file_bytes,
        mime_type=mime_type
    )
    if uri:
        print(f"[OK] Stored raw prescription successfully: {uri}")
        return uri
    else:
        print(f"[WARN] Raw bucket upload skipped or failed (Bucket: gs://{settings.raw_prescriptions_bucket})")
        print("  Check bucket existence and ensure service account has 'roles/storage.objectAdmin'.")
        return ""

def test_document_ai_ocr(file_bytes: bytes, mime_type: str) -> dict:
    """Test Google Document AI OCR API"""
    print("\n=== STEP 2: Google Document AI OCR Processing ===")
    processor_name = document_ai_service.get_processor_name()
    print(f"  Target GCP Project: {settings.gcp_project_id}")
    print(f"  Target Location: {settings.document_ai_location}")
    print(f"  Target Processor: {processor_name or 'Auto-discover / None'}")

    result = document_ai_service.process_document(
        image_bytes=file_bytes,
        mime_type=mime_type
    )

    if result and result.get("raw_transcription"):
        raw = result["raw_transcription"]
        print(f"[OK] Google Document AI OCR succeeded!")
        print(f"  Legibility Score: {result.get('legibility_score', 'N/A')}")
        print(f"  Document Type: {result.get('document_type', 'N/A')}")
        print(f"  Has Unclear Handwriting: {result.get('has_unclear_handwriting', False)}")
        print(f"  Total Characters: {len(raw)}")
        print(f"\n--- Extracted Document AI Text Preview ---")
        print(raw[:500] + ("..." if len(raw) > 500 else ""))
        print("------------------------------------------\n")
        return result
    else:
        print("[WARN] Document AI OCR returned empty or encountered an error. Engaging fallback chain...")
        return {}

async def test_vision_agent_fallback(file_bytes: bytes, mime_type: str) -> dict:
    """Test VisionAgent Multi-layer OCR"""
    print("\n=== STEP 2.5: Vision Agent OCR (DocAI + Fallback) ===")
    res = await vision_agent.extract_prescription_text(file_bytes, mime_type)
    raw = res.get("raw_transcription", "")
    print(f"[OK] Vision Agent returned {len(raw)} chars via engine: {res.get('ocr_engine', 'Unknown')}")
    print(f"  Preview: {raw[:300]}...")
    return res

async def test_phi_and_sanitized_upload(raw_text: str, file_name: str) -> tuple:
    """Test PHI Sanitization & GCS Sanitized Upload"""
    print("\n=== STEP 3: PHI Sanitization & Sanitized GCS Bucket Upload ===")
    sanitized_text, phi_report = await phi_agent.sanitize_prescription(raw_text)
    print(f"[OK] Masked {phi_report.masked_items_count} sensitive identifier(s): {', '.join(phi_report.masked_types)}")
    print(f"  Sanitized text preview:\n  {sanitized_text[:250]}...\n")

    # Upload sanitized payload
    uri = gcs_service.upload_sanitized_prescription(
        session_id="debug_sess_001",
        file_name=file_name,
        sanitized_text=sanitized_text,
        phi_report=phi_report.model_dump() if hasattr(phi_report, "model_dump") else phi_report.dict()
    )
    if uri:
        print(f"[OK] Stored sanitized non-PHI data in GCS: {uri}")
    else:
        print(f"[WARN] Sanitized bucket upload skipped/failed (Bucket: gs://{settings.sanitized_prescriptions_bucket})")

    return sanitized_text, phi_report, uri

async def test_parser_agent(sanitized_text: str) -> list:
    """Test Parser Agent Extraction"""
    print("\n=== STEP 4: Parser Agent Clinical Medication Extraction ===")
    meds, has_uncertain, summary = await parser_agent.parse_prescription(sanitized_text)
    print(f"[OK] Parser found {len(meds)} medication item(s) (Uncertainty flag: {has_uncertain}):")
    for m in meds:
        print(f"  - [{m.confidence.upper()}] {m.name} | Dose: {m.dosage} | Sig: {m.frequency} | Duration: {m.duration}")
        if m.additional_notes:
            print(f"    Notes: {m.additional_notes}")
    return meds

async def run_pipeline(file_path: Path):
    print(f"\n{'='*70}")
    print(f"RxDecoder OCR & GCP PIPELINE DEBUGGER: {file_path.name}")
    print(f"{'='*70}")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    mime_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "image/jpeg"
    print(f"File Type: {mime_type} ({len(file_bytes)} bytes)")

    # 1. GCS Raw Upload
    raw_uri = test_gcs_raw_upload(file_path.name, file_bytes, mime_type)

    # 2. Document AI OCR
    doc_ai_result = test_document_ai_ocr(file_bytes, mime_type)
    if not doc_ai_result:
        doc_ai_result = await test_vision_agent_fallback(file_bytes, mime_type)

    raw_text = doc_ai_result.get("raw_transcription", "")

    # 3. PHI Sanitization & GCS Sanitized Upload
    sanitized_text, phi_report, san_uri = await test_phi_and_sanitized_upload(raw_text, file_path.name)

    # 4. Clinical Parser
    meds = await test_parser_agent(sanitized_text)

    print(f"\n{'='*70}")
    print("DEBUG SUMMARY:")
    print(f"  GCS Raw Bucket:       {'[OK] ' + raw_uri if raw_uri else '[WARN] Pending/Offline'}")
    print(f"  OCR Engine:           {doc_ai_result.get('ocr_engine', 'Google Document AI')}")
    print(f"  Extracted Characters: {len(raw_text)}")
    print(f"  PHI Sanitized:        [OK] ({phi_report.masked_items_count} items masked)")
    print(f"  GCS Sanitized Bucket: {'[OK] ' + san_uri if san_uri else '[WARN] Pending/Offline'}")
    print(f"  Parsed Medications:   {len(meds)} item(s)")
    print(f"{'='*70}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_ocr.py <path-to-prescription-image-or-pdf>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    asyncio.run(run_pipeline(file_path))

if __name__ == "__main__":
    main()
