import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Load local .env files only for local development. Cloud Run supplies all
# production values through environment variables and Secret Manager bindings.
app_env = os.getenv("APP_ENV", "local").lower()
env_path = Path(__file__).resolve().parent.parent / ".env"
root_env_path = Path(__file__).resolve().parent.parent.parent / ".env"

if app_env == "local":
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
    elif root_env_path.exists():
        load_dotenv(dotenv_path=root_env_path, override=False)

# ADC is the only supported Google authentication path. Ignore any stale
# key-file override inherited by an older terminal or development process.
os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "local")
    app_name: str = "RxDecoder API"
    version: str = "1.0.0"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    default_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    fallback_model: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")
    temperature: float = float(os.getenv("TEMPERATURE", "0.1"))
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
    allowed_extensions: list[str] = [".jpg", ".jpeg", ".png", ".webp", ".pdf"]

    # Google Cloud Storage & Document AI Configuration
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "rxdecoded")
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", gcp_project_id)
    gcp_service_account: str = os.getenv("GCP_SERVICE_ACCOUNT", "")
    raw_prescriptions_bucket: str = os.getenv("RAW_PRESCRIPTIONS_BUCKET", "raw-prescriptions")
    sanitized_prescriptions_bucket: str = os.getenv("SANITIZED_PRESCRIPTIONS_BUCKET", "sanitized-prescriptions")
    document_ai_location: str = os.getenv("DOCUMENT_AI_LOCATION", "us")
    document_ai_processor_id: str = os.getenv("DOCUMENT_AI_PROCESSOR_ID", "")
    enable_gcs_storage: bool = os.getenv("ENABLE_GCS_STORAGE", "true").lower() in ("true", "1", "yes")
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]

settings = Settings()




