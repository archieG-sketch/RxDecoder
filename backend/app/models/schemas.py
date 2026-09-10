from typing import List, Optional, Literal
from pydantic import BaseModel, Field

ConfidenceLevel = Literal["high", "medium", "low", "unclear"]
TimeOfDay = Literal["Morning", "Afternoon", "Evening", "Bedtime", "As Needed"]

class MedicationAnalysis(BaseModel):
    uses_summary: str = Field(description="Simple explanation of what this medicine is generally used for")
    how_to_take_plain: str = Field(description="Exact interpreted prescription instructions in conversational plain language")
    common_side_effects: List[str] = Field(default_factory=list, description="Common, mild side effects in plain English")
    important_warnings: List[str] = Field(default_factory=list, description="Crucial precautions and warnings distinct from side effects")
    serious_symptoms: List[str] = Field(default_factory=list, description="Serious red-flag symptoms requiring prompt medical attention without diagnosing")
    substance_allergy_warnings: List[str] = Field(default_factory=list, description="Allergy, food, or ingredient warnings when known")
    mechanism_summary: Optional[str] = Field(None, description="Pharmacological class or mechanism for detailed mode")

class MedicationItem(BaseModel):
    id: str = Field(..., description="Unique medication identifier")
    name: str = Field(..., description="Prescribed medicine name as extracted")
    generic_name: Optional[str] = Field(None, description="Generic drug name if confidently identified")
    brand_name: Optional[str] = Field(None, description="Brand name if applicable")
    strength: str = Field(..., description="Strength, e.g., 500 mg, 10 ml, 250 mcg")
    dosage: str = Field(..., description="Dosage, e.g., 1 tablet, 2 puffs, 5 ml")
    frequency: str = Field(..., description="Frequency, e.g., Twice daily, Every 8 hours, Once at bedtime")
    route: str = Field(default="Oral", description="Route of administration, e.g., Oral, Topical, Inhalation, Ophthalmic")
    duration: str = Field(default="As prescribed", description="Duration, e.g., 5 days, 14 days, 30 days, Ongoing")
    timing_instructions: str = Field(default="As directed", description="Specific timing like Morning and Night, before bed")
    food_instructions: str = Field(default="Take with or without food", description="Food directions, e.g., Take after meals, On an empty stomach")
    additional_notes: Optional[str] = Field(None, description="Doctor notes or special handling instructions")
    confidence: ConfidenceLevel = Field(default="high", description="Extraction confidence score: high, medium, low, unclear")
    confidence_reason: Optional[str] = Field(None, description="Explanation if confidence is medium, low, or unclear")
    analysis: Optional[MedicationAnalysis] = None

class InteractionItem(BaseModel):
    severity: Literal["low", "moderate", "high", "caution"] = "caution"
    medications_involved: List[str]
    description: str
    recommendation: str

class InteractionCheck(BaseModel):
    has_potential_interactions: bool = False
    summary: str = "No severe interactions identified among the extracted medications."
    interactions: List[InteractionItem] = Field(default_factory=list)
    verification_advice: str = "Always inform your pharmacist of all prescription and over-the-counter medications you take."

class MedicationChecklistItem(BaseModel):
    id: str
    time_of_day: TimeOfDay
    medication_name: str
    dosage: str
    instructions: str
    food_relation: str
    requires_verification: bool = False
    verification_reason: Optional[str] = None
    completed: bool = False

class PHISanitizationReport(BaseModel):
    sanitized: bool = True
    masked_items_count: int = 0
    masked_types: List[str] = Field(default_factory=list)
    sanitized_text_preview: str = ""
    summary: str = "Protected Health Information (PHI) has been masked before downstream AI analysis."

class PrescriptionDecodeResponse(BaseModel):
    success: bool = True
    session_id: str
    original_file_name: Optional[str] = None
    file_type: str = "image"
    phi_report: PHISanitizationReport
    raw_ocr_summary: Optional[str] = None
    medications: List[MedicationItem] = Field(default_factory=list)
    interactions: InteractionCheck = Field(default_factory=InteractionCheck)
    checklist: List[MedicationChecklistItem] = Field(default_factory=list)
    simple_explanation: str = ""
    detailed_explanation: str = ""
    has_uncertain_handwriting: bool = False
    uncertainty_warning: Optional[str] = None
    safety_disclaimer: str = (
        "RxDecoder is an educational and organizational tool designed to help patients and caregivers "
        "understand prescriptions. It is NOT a substitute for professional medical advice, diagnosis, or treatment. "
        "Never alter medication dosages without consulting your prescribing doctor or licensed pharmacist."
    )
    raw_storage_uri: Optional[str] = Field(None, description="GCS URI for stored raw prescription in raw-prescriptions bucket")
    sanitized_storage_uri: Optional[str] = Field(None, description="GCS URI for de-identified data in sanitized-prescriptions bucket")
    ocr_engine: Optional[str] = Field("Google Document AI", description="OCR Engine used for transcription")
    tts_narration_script: str = ""
    processing_time_ms: float = 0.0

class PharmacyItem(BaseModel):
    id: str
    name: str
    distance_km: float
    distance_miles: float
    address: str
    phone: Optional[str] = None
    open_status: str = "Open"
    hours_summary: str = "Standard retail hours"
    google_maps_url: str
    inventory_disclaimer: str = "Nearby pharmacy where you can check availability. Live inventory data is not tracked."

class PharmacySearchResponse(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    query_location: Optional[str] = None
    pharmacies: List[PharmacyItem] = Field(default_factory=list)
    note: str = "Nearby pharmacies where you can check availability."

class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0
    voice_gender: Literal["FEMALE", "MALE", "NEUTRAL"] = "NEUTRAL"
    language_code: str = "en-US"

class DecodeSampleRequest(BaseModel):
    sample_id: str
