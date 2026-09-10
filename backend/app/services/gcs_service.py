import io
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError, NotFound, Forbidden
from app.config import settings
from app.utils.auth_identity import get_auth_principal
from app.utils.logger import logger

class GCSService:
    """
    Google Cloud Storage Service for HIPAA-compliant prescription data retention:
    1. 'raw-prescriptions' bucket: Stores the original uploaded image/PDF file.
    2. 'sanitized-prescriptions' bucket: Stores the de-identified, non-PHI clinical payload & audit report.
    """

    def __init__(self):
        self.client: Optional[storage.Client] = None
        self._init_client()

    def _init_client(self):
        try:
            self.client = storage.Client(project=settings.gcp_project_id or None)
            principal = get_auth_principal(self.client._credentials)
            logger.info(
                f"GCSService: Storage client initialized for GCP project '{self.client.project}' "
                f"using principal '{principal}'."
            )
        except Exception as e:
            logger.warning(f"GCSService: Could not initialize GCS client: {e}. Local fallback enabled.")
            self.client = None

    def upload_raw_prescription(
        self,
        session_id: str,
        file_name: str,
        file_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Optional[str]:
        """
        Uploads the raw prescription image/PDF to the raw-prescriptions bucket.
        Path format: {session_id}/{timestamp}_{filename}
        Returns the gs:// URI if successful, or None.
        """
        if not settings.enable_gcs_storage or not self.client:
            logger.debug("GCSService: GCS upload skipped (storage disabled or client uninitialized).")
            return None

        bucket_name = settings.raw_prescriptions_bucket
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_filename = file_name.replace(" ", "_") if file_name else "prescription.jpg"
        blob_path = f"{session_id}/{timestamp_str}_{safe_filename}"

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            blob.content_type = mime_type
            blob.metadata = {
                "session_id": session_id,
                "original_filename": file_name or "prescription",
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "data_classification": "raw_phi_prescription"
            }

            blob.upload_from_string(file_bytes, content_type=mime_type)
            gcs_uri = f"gs://{bucket_name}/{blob_path}"
            logger.info(f"GCSService: Raw prescription successfully stored at {gcs_uri}")
            return gcs_uri
        except Forbidden as e:
            logger.warning(
                f"GCSService: Access forbidden to bucket '{bucket_name}' for principal "
                f"'{get_auth_principal(self.client._credentials)}'. "
                f"Ensure service account has 'roles/storage.objectAdmin' on gs://{bucket_name}. Details: {e}"
            )
            return None
        except NotFound as e:
            logger.warning(
                f"GCSService: Bucket '{bucket_name}' not found. Please create it or check permissions. Details: {e}"
            )
            return None
        except Exception as e:
            logger.warning(f"GCSService: Error uploading raw prescription to '{bucket_name}': {e}")
            return None

    def upload_sanitized_prescription(
        self,
        session_id: str,
        file_name: str,
        sanitized_text: str,
        phi_report: Optional[Dict[str, Any]] = None,
        extracted_medications: Optional[list] = None
    ) -> Optional[str]:
        """
        Uploads HIPAA-sanitized non-PHI clinical prescription data and audit trail to sanitized-prescriptions bucket.
        Path format: {session_id}/sanitized_data_{timestamp}.json
        Returns the gs:// URI if successful, or None.
        """
        if not settings.enable_gcs_storage or not self.client:
            logger.debug("GCSService: GCS sanitized upload skipped.")
            return None

        bucket_name = settings.sanitized_prescriptions_bucket
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        blob_path = f"{session_id}/sanitized_rx_{timestamp_str}.json"

        payload = {
            "session_id": session_id,
            "file_name": file_name,
            "sanitized_at": datetime.now(timezone.utc).isoformat(),
            "data_classification": "de_identified_non_phi",
            "sanitization_report": phi_report or {},
            "sanitized_prescription_text": sanitized_text,
            "parsed_medication_count": len(extracted_medications) if extracted_medications else 0
        }

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            blob.content_type = "application/json"
            blob.metadata = {
                "session_id": session_id,
                "data_classification": "non_phi",
                "phi_masked": "true"
            }

            blob.upload_from_string(
                json.dumps(payload, indent=2),
                content_type="application/json"
            )
            gcs_uri = f"gs://{bucket_name}/{blob_path}"
            logger.info(f"GCSService: Sanitized non-PHI data stored at {gcs_uri}")
            return gcs_uri
        except Forbidden as e:
            logger.warning(
                f"GCSService: Access forbidden to bucket '{bucket_name}' for principal "
                f"'{get_auth_principal(self.client._credentials)}'. "
                f"Ensure service account has 'roles/storage.objectAdmin' on gs://{bucket_name}. Details: {e}"
            )
            return None
        except NotFound as e:
            logger.warning(
                f"GCSService: Bucket '{bucket_name}' not found. Details: {e}"
            )
            return None
        except Exception as e:
            logger.warning(f"GCSService: Error uploading sanitized prescription to '{bucket_name}': {e}")
            return None

    def check_bucket_status(self) -> Dict[str, Any]:
        """
        Diagnostic helper to check connectivity and IAM access to both buckets.
        """
        status = {
            "gcs_client_active": self.client is not None,
            "project_id": self.client.project if self.client else settings.gcp_project_id,
            "raw_bucket": {
                "name": settings.raw_prescriptions_bucket,
                "accessible": False,
                "error": None
            },
            "sanitized_bucket": {
                "name": settings.sanitized_prescriptions_bucket,
                "accessible": False,
                "error": None
            }
        }

        if not self.client:
            return status

        # Test raw bucket
        try:
            b = self.client.get_bucket(settings.raw_prescriptions_bucket)
            status["raw_bucket"]["accessible"] = True
            status["raw_bucket"]["location"] = b.location
        except Exception as e:
            status["raw_bucket"]["error"] = str(e)

        # Test sanitized bucket
        try:
            b = self.client.get_bucket(settings.sanitized_prescriptions_bucket)
            status["sanitized_bucket"]["accessible"] = True
            status["sanitized_bucket"]["location"] = b.location
        except Exception as e:
            status["sanitized_bucket"]["error"] = str(e)

        return status

gcs_service = GCSService()
