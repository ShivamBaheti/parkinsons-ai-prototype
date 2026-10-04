# AI-Assisted Parkinson's Screening (Research Prototype)

> **Research Prototype — Not a Medical Diagnosis**
>
> This application is an experimental AI-based screening system intended for academic research and demonstration. Its outputs should not be interpreted as a diagnosis of Parkinson's Disease or used to make medical decisions. Consult a qualified healthcare professional for clinical evaluation.

**Status:** Setup and input handling done for voice and drawing; no ML models exist yet. Voice model training is deferred until a raw-audio dataset is obtained. See `ml/DATASETS.md`.

## Project Overview
_To be written._

## Motivation
_To be written._

## Research Gap
_To be written._

## Proposed Solution
Screening from three signal types: voice recordings, touchscreen spiral/wave drawing, and smartphone/wearable motion data.

## System Architecture
Next.js frontend → REST/JSON → FastAPI backend → per-modality pipelines (voice, drawing, motion) → multimodal fusion → results dashboard.

## Technology Stack
- Frontend: Next.js (App Router), React, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, Uvicorn, Pydantic
- Planned, added when first used: NumPy, pandas, SciPy, scikit-learn, XGBoost, joblib, librosa, soundfile, OpenCV, Framer Motion, Lucide React, Recharts

## Dataset Sources
_Documented per modality in Phases 2–4. No dataset statistics are stated until verified from the source._

## Data Processing
_To be written._

## Machine Learning Models
_To be written._

## Multimodal Fusion
- The voice, drawing and motion datasets contain different people, so no paired data exists to train or validate a fusion model.
- The prototype therefore uses an equal-weight mean of the modality probabilities that are available; missing modalities are left out.
- The score is shown out of 100; 0.5 is the models' default threshold, not a clinically validated cut-off.
- The equal weights are a design choice, not medically validated. Weighted, logistic-regression and stacking fusion were not attempted because they need paired data.
- Code: `backend/app/models/fusion_model.py`, `backend/app/api/screening.py`.

## API Documentation
| Method | Path | Status |
| --- | --- | --- |
| GET | `/api/health` | Implemented |
| POST | `/api/voice/analyze` | Input validation only; returns `model_unavailable` until a model is trained |
| POST | `/api/drawing/analyze` | Input validation only; returns `model_unavailable` until a model is trained |
| POST | `/api/motion/analyze` | Input validation only; returns `model_unavailable` until a model is trained |
| POST | `/api/screening/analyze` | Implemented: fuses modality probabilities (JSON `{voice, drawing, motion}`, each 0-1 or omitted) |
| GET | `/api/model-info` | Implemented: which models are installed, plus training metadata if present |

Interactive docs while the backend runs: http://localhost:8000/docs

## Frontend
- Pages: `/` (landing), `/screening` (three tests), `/results` (combined score), `/about`.
- The screening page passes the numeric scores to `/results` in the URL; nothing is stored.
- Plain styling with bullets and simple bars; no charting library.

## Installation

Requirements: Python 3.11+, Node.js 20+.

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
cp .env.local.example .env.local
npm install
```

## Running the Backend
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
Check: http://localhost:8000/api/health

Tests: `python -m pytest`

## Running the Frontend
```bash
cd frontend
npm run dev
```
Open http://localhost:3000. The header shows whether the backend is reachable.

## Model Training
_To be written (Phases 2–5)._

## Results
_No results yet. Metrics will be reported with their full evaluation methodology._

## Limitations
_To be written._

## Ethical Considerations
- Presented as a screening prototype, never a diagnosis.
- Privacy: uploaded recordings, drawings and sensor data are not to be stored permanently; no names, medical records or other personal identifiers are collected. (Implemented and documented in detail as each pipeline is built.)

## Future Work
_To be written._
