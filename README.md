# AI-Assisted Parkinson's Screening (Research Prototype)

> **Research Prototype — Not a Medical Diagnosis**
>
> This application is an experimental AI-based screening system intended for academic research and demonstration. Its outputs should not be interpreted as a diagnosis of Parkinson's Disease or used to make medical decisions. Consult a qualified healthcare professional for clinical evaluation.

**Status:** drawing and voice models exist and are wired to the app; the motion model does not (dataset not obtained yet). The voice model is shown as a demonstration only and is excluded from the combined score (see Results). Nothing here has clinical validation.

## Project Overview
A full-stack research prototype that takes a voice recording, a touchscreen spiral drawing and (planned) wearable motion data, runs a separate machine-learning model on each, and shows a combined screening score with the evidence behind it. It is a screening aid for a university project (Creativity, Problem Solving & Innovation), never a diagnosis.

## Motivation
- Parkinson's disease is usually diagnosed after motor symptoms are well established, and specialist assessment is not available to everyone.
- Voice, handwriting/drawing and movement all change in Parkinson's and can be captured with phones, tablets and watches.

## Research Gap
- Most published work studies one signal in isolation, on one dataset, often with several recordings per person split randomly between training and test sets, which inflates reported accuracy.
- This project asks a narrower question: what can honestly be said when each signal is modelled with person-level splitting, confound checks and no invented numbers, and the outputs are then combined?

## Proposed Solution
Screening from three signal types: voice recordings, touchscreen spiral/wave drawing, and smartphone/wearable motion data.

## System Architecture
Next.js frontend → REST/JSON → FastAPI backend → per-modality pipelines (voice, drawing, motion) → multimodal fusion → results dashboard.
<img width="956" height="1564" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/040f09b4-8b86-4be6-a165-06fd046b5ccc" />


## Technology Stack
- Frontend: Next.js (App Router), React, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, Uvicorn, Pydantic
- ML: NumPy, pandas, SciPy, scikit-learn, joblib, soundfile, praat-parselmouth (XGBoost, librosa, OpenCV, Recharts, Framer Motion and Lucide were not needed)

## Dataset Sources
Full notes are in `ml/DATASETS.md`. Nothing is stated as fact unless it was read from the source or the downloaded files.
- **Drawing:** UCI "Parkinson Disease Spiral Drawings Using Digitized Graphics Tablet" (id 395, CC BY 4.0). Used: `hw_dataset`, static spiral test, 40 people (15 controls, 25 Parkinson's). `new_dataset` (Parkinson's only) is excluded because the protocol differs.
- **Voice:** ItalianPVS (Dimauro & Girardi, IEEE DataPort, DOI 10.21227/aw6b-tg17). Used: sustained vowel /a/, 28 people with Parkinson's vs 22 elderly healthy controls (ages 60-77 in the metadata; mean age 67.2 vs 67.1; sex split differs, 19 M / 9 F vs 10 M / 12 F). The 15 young controls have no sustained vowels and are unused. Licence to be confirmed on the DataPort page.
- **Motion:** PADS (PhysioNet, DOI 10.13026/m0w9-zx22, CC BY-NC-SA 4.0) is the chosen dataset but has not been downloaded, so no motion model exists.

## Data Processing
- **Drawing:** pen-up samples are dropped; 13 features are extracted from x/y/time only (speed, pauses, radial error against an ideal spiral, heading change, tremor-band energy and similar). Code: `backend/app/features/drawing_features.py`, shared by training and the API.
- **Voice:** audio is resampled to 16 kHz, the first and last 0.25 s are trimmed, and the central segment (at most 3 s) is level-normalised. Nine Praat features are computed (jitter x3, shimmer x3, HNR, pitch variation, voiced fraction). Absolute pitch is deliberately not used. Code: `backend/app/features/voice_features.py`.
- **Motion:** a 12-feature extractor exists and is tested on synthetic signals only.
- **Privacy:** the API processes uploads in memory and writes nothing to disk. Raw audio folders in the voice dataset are named after real people; derived files use anonymous IDs, and `ml/data/raw/` is git-ignored.

## Machine Learning Models
All evaluation is by person (never by recording or row), with scaling inside the training folds, repeated 5-fold cross-validation x20, and a 0.5 threshold. Sensitivity, specificity, ROC-AUC and the confusion matrix are reported, not accuracy alone. The model types were fixed in advance, but each final model was picked among its candidates on the same cross-validation, so its numbers are mildly optimistic.
- **Drawing:** random forest chosen over logistic regression and SVM. Trained on 10 features; `turns`, `duration_s` and `path_length` are excluded (see Results). Scripts: `ml/scripts/train_drawing.py`, `ablate_drawing.py`, `save_drawing_model.py`.
- **Voice:** logistic regression chosen over random forest. Scripts: `ml/scripts/train_voice.py`, `save_voice_model.py`.
- **Motion:** not trained.
Re-run the `save_*_model.py` scripts after installing the requirements so the saved metrics match your own library versions.

## Multimodal Fusion
- The voice, drawing and motion datasets contain different people, so no paired data exists to train or validate a fusion model.
- The prototype therefore uses an equal-weight mean of the modality probabilities that are available; missing modalities are left out.
- Modalities flagged unreliable (currently voice) are shown but left out of the mean.
- The score is shown out of 100; 0.5 is the models' default threshold, not a clinically validated cut-off.
- The equal weights are a design choice, not medically validated. Weighted, logistic-regression and stacking fusion were not attempted because they need paired data.
- Code: `backend/app/models/fusion_model.py`, `backend/app/api/screening.py`.

## API Documentation
| Method | Path | Status |
| --- | --- | --- |
| GET | `/api/health` | Implemented |
| POST | `/api/voice/analyze` | WAV upload; returns a score flagged `reliable: false` |
| POST | `/api/drawing/analyze` | JSON trajectory; returns a score flagged `validated_for_this_input: false` |
| POST | `/api/motion/analyze` | Input validation only; returns `model_unavailable` |
| POST | `/api/screening/analyze` | JSON `{voice, drawing, motion}` (each 0-1 or omitted); combines the reliable ones |
| GET | `/api/model-info` | Which models are installed, with their saved training metadata |

Errors always use `{"error": code, "message": text}`; stack traces are never returned. Interactive docs while the backend runs: http://localhost:8000/docs

## Frontend
- Pages: `/` (landing), `/screening` (three tests), `/results` (combined score), `/about`.
- The screening page passes the numeric scores to `/results` in the URL; nothing is stored.
- Plain styling with bullets and simple bars; no charting library.

## Installation
Requirements: Python 3.11+, Node.js 20+. Windows Command Prompt commands shown; on macOS/Linux use `source .venv/bin/activate` and `cp`.
```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd ..\frontend
copy .env.local.example .env.local
npm install
```

## Running the Backend
```
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```
Check http://localhost:8000/api/health. Tests: `python -m pytest`.

## Running the Frontend
```bash
cd frontend
npm run dev
```
Open http://localhost:3000. The header shows whether the backend is reachable.

## Model Training
Datasets are not in the repository. Download them into `ml/data/raw/`, then (from `ml/scripts`, with the backend environment active):
- Drawing: `python explore_drawing.py`, `python train_drawing.py`, `python ablate_drawing.py`, `python save_drawing_model.py`
- Voice: `python explore_voice.py`, `python extract_voice_features.py`, `python train_voice.py`, `python save_voice_model.py`
Evaluation outputs are saved in `ml/results/`.

## Results
Numbers below come from the saved model metadata (`backend/models/*.json`, produced by the scripts above) and `ml/results/`. They are cross-validated estimates on small datasets, not clinical performance.

**Drawing (40 people)**
- ROC-AUC 0.77, sensitivity 0.79, specificity 0.59 (about 1 in 5 Parkinson's cases missed in the data).
- With all 13 features AUC was 0.86, but `turns`, `duration_s` and `path_length` alone reached AUC 0.81. They describe how much was drawn, not how, and the web canvas fixes the guide spiral, so they were removed.
- A label-permutation test on the original model gave p of about 0.01. Recordings of the two Parkinson's groups in the dataset can be told apart by protocol (AUC 0.81), so a recording-session effect cannot be ruled out.
- The model was trained on stylus-on-tablet data. Mouse and finger drawings are not validated.

**Voice (50 people)**
- Cross-validated ROC-AUC 0.91, sensitivity 0.91, specificity 0.81. This is not trusted.
- The direction is the opposite of the clinical expectation: patients have about half the shimmer of the controls and a higher harmonics-to-noise ratio. The controls were also recorded differently (silence before the voice, different lengths), and 10 patients were recorded at 44.1 kHz. The model probably separates recording setups rather than disease.
- The voice score is therefore displayed as a demonstration and excluded from the combined score (`EXCLUDED_FROM_SCORE` in `fusion_model.py`). It should be removed from that list only after an external check on a different dataset.

**Combined score:** the equal-weight mean of the reliable modalities (currently drawing only). It has not been validated.

## Limitations
- Small datasets (40 and 50 people); wide uncertainty on every metric.
- No clinical validation and no external test set for either model.
- Domain shift: training data came from a stylus tablet and a lab or clinic microphone setup; the app uses a mouse/finger on a web canvas and a browser microphone.
- Recording-protocol differences between patients and controls may drive the voice (and possibly the drawing) results.
- The three datasets contain different people, so the fusion rule is unvalidated.
- Motion is not implemented. Browser-based motion capture is not supported.
- The web interface has been checked by rendering in a headless browser and by the author on the drawing flow, not on a range of devices.

## Ethical Considerations
- Presented as a screening prototype, never a diagnosis; the disclaimer appears on every page and in API responses.
- A false reassurance or a false alarm could affect a person's decisions, which is why scores are shown with their caveats and users are pointed to a healthcare professional.
- Privacy: uploads are processed in memory and not stored; no names, accounts or medical records are collected; the results page carries only numeric scores in the address.
- Source data from people with a health condition is used under the datasets' licences; folder names containing personal names are not reproduced.

## Future Work
- Obtain PADS and build the motion pipeline.
- Test the voice model on an independent dataset (for example the Arkansas phone recordings) before trusting it, or retire it.
- Collect a small set of mouse/touch spirals to measure the domain shift for drawing.
- Paired multimodal data, if it can be found, to evaluate real fusion.
- Spiral visualisation and accessibility checks on the results page.

## Result levels (UI)

The results page shows the combined score as a Low / Medium / High screening signal (`frontend/lib/risk.ts`):
Low 0-29, Medium 30-49, High 50-100. The 50 boundary matches the backend threshold (0.5). The Low/Medium
split is a presentation choice only. None of the levels are clinically validated.

## Replay, "why this score" and printing

- The results page replays the drawing and shows how the model weighed its measurements. The drawing is kept only in the browser tab (sessionStorage) and is never stored by the server. The breakdown comes from `app/models/explain.py` (exact per-drawing contributions of the random forest) and is returned by `/api/drawing/analyze` as `baseline` and `contributions`.
- "Print result" uses the browser print dialog (choose "Save as PDF").
- Voice is left out of the combined score by default because its model is unreliable. To count it anyway, set the environment variable `INCLUDE_VOICE_IN_SCORE=true` before starting the backend (it is read from the environment, not auto-loaded from `.env`).
