# RxDecoder

RxDecoder is an AI-assisted prescription understanding app. It accepts prescription images or PDFs, extracts medication instructions, protects PHI, provides safety guidance, and generates patient-friendly explanations.

## Stack

- Frontend: React, TypeScript, Vite, Axios
- Backend: Python, FastAPI, Uvicorn, Pydantic
- Agents: Google ADK-compatible agents with optional Gemini integration
- Google Cloud: Document AI, Cloud Storage, Text-to-Speech, Cloud Build, Artifact Registry, and Cloud Run

## Local Development

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm ci
copy .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173` and uses the backend at `http://localhost:8000` by default.

## Configuration

Set production secrets through Cloud Run environment variables or Secret Manager. Do not commit `.env` files, API keys, service-account files, or prescription data. Gemini is optional; local parsing and rule-based fallbacks are used when `GEMINI_API_KEY` is not configured.

## API

- `GET /api/health` - health check
- `GET /api/samples` - list demo samples
- `POST /api/decode/sample` - decode a demo sample
- `POST /api/decode` - process an uploaded prescription
- `POST /api/tts/synthesize` - generate narration
- `GET /api/pharmacies` - find nearby pharmacies

## Tests

```powershell
cd backend
pytest
```

## Deployment

The frontend and backend each have a Dockerfile and Cloud Build configuration. Cloud Build publishes container images to Artifact Registry; Cloud Run hosts the deployed services. Set the frontend build argument `VITE_API_URL` to the deployed backend URL and configure the backend `ALLOWED_ORIGINS` with the deployed frontend URL.

## Medical Disclaimer

RxDecoder is an informational aid and does not replace a doctor or pharmacist. Users should verify unclear prescriptions and medication instructions with a qualified healthcare professional before taking medication.
