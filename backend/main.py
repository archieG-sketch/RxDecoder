from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.schemas import (
    PrescriptionDecodeResponse, PharmacySearchResponse,
    TTSRequest, DecodeSampleRequest
)
from app.services.orchestrator import orchestrator
from app.services.tts_service import tts_service
from app.services.pharmacy_service import pharmacy_service
from app.services.sample_prescriptions import get_sample_list, get_sample_response
from app.utils.logger import logger

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Production-grade AI Prescription Understanding API with HIPAA-aligned PHI sanitization and multi-agent clinical orchestration."
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

from app.services.document_ai_service import document_ai_service
from app.services.gcs_service import gcs_service

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version
    }

@app.post("/api/decode", response_model=PrescriptionDecodeResponse)
async def decode_prescription(
    file: UploadFile = File(...)
):
    """
    Decodes an uploaded prescription image or PDF document.
    Executes the 6-stage multi-agent pipeline with PHI protection.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Unsupported prescription file type.")

    logger.info("Received prescription upload.")
    
    # Read file content
    max_upload_bytes = settings.max_upload_size_mb * 1024 * 1024
    contents = await file.read(max_upload_bytes + 1)
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > max_upload_bytes:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds the maximum allowed size.")

    mime_type = file.content_type or "image/jpeg"
    if "pdf" in mime_type.lower() or (file.filename and file.filename.lower().endswith(".pdf")):
        mime_type = "application/pdf"

    try:
        response = await orchestrator.decode_prescription_image(
            image_bytes=contents,
            mime_type=mime_type,
            file_name=file.filename
        )
        return response
    except Exception:
        logger.exception("Prescription decoding failed.")
        raise HTTPException(status_code=500, detail="Failed to process prescription.")

@app.get("/api/samples")
async def list_sample_prescriptions():
    """
    Returns available sample prescription presets for instant demonstration.
    """
    return get_sample_list()

@app.post("/api/decode/sample", response_model=PrescriptionDecodeResponse)
async def decode_sample_prescription(payload: DecodeSampleRequest):
    """
    Instantly decodes a chosen sample prescription preset.
    """
    logger.info(f"Decoding sample prescription: {payload.sample_id}")
    return get_sample_response(payload.sample_id)

@app.post("/api/tts/synthesize")
async def synthesize_text_to_speech(payload: TTSRequest):
    """
    Synthesizes natural spoken audio using Google Cloud Text-to-Speech via ADC.
    Returns binary MP3 audio stream.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    audio_bytes = await tts_service.synthesize_speech(
        text=payload.text,
        voice_gender=payload.voice_gender,
        language_code=payload.language_code,
        speaking_rate=payload.speed
    )

    if audio_bytes:
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=rx_narration.mp3"}
        )
    else:
        # 204 or fallback message signaling client-side Web Speech fallback
        return Response(
            content=b"",
            status_code=204,
            headers={"X-Fallback-Client-TTS": "true"}
        )

@app.get("/api/pharmacies", response_model=PharmacySearchResponse)
async def find_pharmacies(
    lat: float = Query(None, description="User latitude"),
    lon: float = Query(None, description="User longitude"),
    query: str = Query(None, description="City or ZIP code")
):
    """
    Finds nearby pharmacies based on user coordinates or zip search.
    Permission is only prompted when the user explicitly accesses this feature.
    """
    return await pharmacy_service.find_nearby_pharmacies(lat=lat, lon=lon, query=query)
