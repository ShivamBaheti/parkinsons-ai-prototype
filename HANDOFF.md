# Handoff: AI-Assisted Parkinson's Screening prototype

Paste this file (and upload `parkinsons-ai.zip`) at the start of a new chat. It tells Claude what exists,
what was decided and why, what is deferred, and what is left.

## 1. The project
- Owner: Shivam, BTech CSE (AI/ML), building a CPI (Creativity, Problem Solving & Innovation) university project.
- Goal: a working full-stack **research screening prototype** (never a diagnosis) that takes three signals:
  voice, touchscreen spiral drawing, and smartphone/wearable motion data, runs ML on each, and shows a combined screening score.
- Stack: Next.js (App Router) + React + TypeScript + Tailwind v4 on the frontend; FastAPI + Python backend; scikit-learn for ML.
- The original brief was a long spec (phases 1-7). Rules from it that still apply:
  - Never claim diagnosis. Show this disclaimer prominently: "Research Prototype — Not a Medical Diagnosis. This application is an experimental AI-based screening system intended for academic research and demonstration. Its outputs should not be interpreted as a diagnosis of Parkinson's Disease or used to make medical decisions. Consult a qualified healthcare professional for clinical evaluation."
  - No fake models, no hard-coded predictions or accuracies, no invented dataset statistics (say "unavailable" instead).
  - Subject-level splitting when one person has several samples; scaling inside CV pipelines; no tuning on the final test set.
  - Report sensitivity/specificity/ROC-AUC/confusion matrix, not just accuracy; do not cherry-pick.
  - Fusion: datasets are unpaired, so do not pretend one row has voice+drawing+motion; do not present weights as medically validated.
  - Do not store uploaded data; no personal information; never expose stack traces; use Pydantic schemas and consistent JSON.
  - Explain-features wording: "had a relatively high contribution to this model's output", never "caused Parkinson's".
- User preferences: minimal, clean solutions; simple bullet points rather than cards/icons/multi-column layouts; wants a **basic working prototype**, "doesn't have to be perfect in everything"; work incrementally and explain each step.

## 2. Working-environment facts (learned the hard way)
- The user is on **Windows Command Prompt**. Give Windows commands (`.venv\Scripts\activate`, `copy`), one command per line, and say which folder to be in. `source` does not work.
- The Claude sandbox **resets between chats**: re-upload `parkinsons-ai.zip` (project, no node_modules/.venv) and any dataset needed.
- The sandbox cannot reach dataset hosts (UCI, figshare, IEEE DataPort, PhysioNet); the user downloads and uploads. Large datasets: have the user run an extraction script locally and upload the small CSV.
- No browser in the sandbox: UI code is typechecked, linted and built, but **not visually tested**. Only the homepage + "Backend connected" indicator were confirmed by the user on their machine. The voice recorder, drawing canvas and motion uploader have not been confirmed yet.
- Do not use `pkill -f "<pattern>"` where the pattern also appears in the command (it kills its own shell). Use `ps aux | grep "[u]vicorn" | awk '{print $2}' | xargs -r kill`.
- `sh` has no brace expansion: use explicit `mkdir` lists.
- Next.js here is v16 (breaking changes vs older versions); the scaffold's `AGENTS.md`/`CLAUDE.md` in `frontend/` say to read `node_modules/next/dist/docs`. React lint rule `set-state-in-effect` is active.
- Run backend: `cd backend`, `.venv\Scripts\activate`, `pip install -r requirements.txt`, `uvicorn app.main:app --reload --port 8000`. Run frontend: `cd frontend`, `copy .env.local.example .env.local`, `npm install`, `npm run dev`. Use `http://localhost:3000` (not the network IP, or CORS fails).

## 3. What is built (all in the zip, committed to git)
**Frontend** (`frontend/`)
- `/` landing page: title, subtitle, explanation, three-signal bullets, Start Screening button, disclaimer, animated spiral mark, backend-status indicator.
- `/screening`: Step 1 Voice (`VoiceRecorder`: record/stop/replay/upload, converts to WAV in-browser via `lib/wav.ts`), Step 2 Drawing (`DrawingCanvas`: 600x600 canvas, guide spiral of 3 turns, pointer events, captures x/y/t/stroke/pressure, Clear/Submit), Step 3 Motion (`MotionUploader`: CSV upload).
- `lib/api.ts`: `getHealth`, `analyzeVoice`, `analyzeDrawing`, `analyzeMotion`; `ApiError` carries the server's `{error, message}`.
- Design: paper-white/navy/teal, Newsreader + Figtree (offline @fontsource fonts).
- Not built: `/results`, `/about`, `RiskScore`, `ModalityCard`, `ResultsChart`. Framer Motion, Lucide, Recharts are not installed (add when used).

**Backend** (`backend/`, 28 passing tests via `python -m pytest`)
- `GET /api/health`. CORS for localhost:3000. Global 500 handler (no stack traces). Consistent error shape `{"error": code, "message": text}`.
- `POST /api/voice/analyze` (WAV upload), `POST /api/drawing/analyze` (JSON points), `POST /api/motion/analyze` (CSV upload): each **validates input then returns 503 `model_unavailable`** because no trained model exists. This is deliberate (no fake scores). When a model exists, replace the 501 `not_implemented` branch.
- Validation (`utils/validation.py`): audio (size, decodable, duration, silence); drawing (empty, too few points, too fast, out-of-order time, too small); motion CSV (columns, numeric, timestamp order, duration >= 5 s, >= 20 Hz; detects ms timestamps and m/s² accel).
- Features: `features/drawing_features.py` (13 template-free x/y/time features) and `features/motion_features.py` (12 rotation-invariant accel/gyro features, tested on synthetic signals). Same code is meant for training and inference.
- Model loaders: `models/{voice,drawing,motion}_model.py` return None until `backend/models/*.pkl` exist.
- Missing vs the original structure: `api/screening.py`, `models/fusion_model.py`, `features/voice_features.py`, `utils/preprocessing.py`, `GET /api/model-info`.

**ML** (`ml/`)
- `DATASETS.md`: documentation of every candidate dataset (verified facts vs "unavailable/to verify").
- `scripts/explore_drawing.py`, `scripts/train_drawing.py` (evaluation only; does not save a model), `scripts/extract_motion_features.py` (tested on synthetic files only).
- `results/drawing_evaluation.txt` (full output below), `data/processed/drawing_features.csv`.
- Empty/missing: `notebooks/`, `train_voice.py`, `train_motion.py`, `train_fusion.py`.

**Repo**: `README.md` skeleton (API table, install/run steps; many sections still "To be written"), `TODO.md`, `.gitignore`, git history.

## 4. Dataset decisions
**Voice** (nothing downloaded yet; user had trouble downloading)
- Popular UCI sets (Oxford 31 people / Istanbul 252 subjects) give only pre-computed features, so they cannot match a live browser recording. Rejected.
- Chosen: **ItalianPVS** (Dimauro & Girardi, IEEE DataPort, DOI 10.21227/aw6b-tg17), raw 16 kHz sustained vowels, CC BY 4.0 per a paper (verify). Per secondary sources: 28 PD, 22 elderly HC (66-77), 15 young HC (19-29). Plan: train PD vs elderly HC only (young HC would let the model learn age); speaker-level grouped CV.
- Fallback / external check: Arkansas phone /a/ recordings (figshare DOI 10.6084/m9.figshare.23849127, CC BY 4.0; age-confounded, 8 kHz).
- Others (MDVR-KCL: read speech, 37 people; NeuroVoz: needs signed agreement) not used.

**Drawing** (downloaded and analysed)
- UCI "Parkinson Disease Spiral Drawings Using Digitized Graphics Tablet" (id 395, CC BY 4.0). Files: `hw_dataset/control` (15), `hw_dataset/parkinson` (25), `new_dataset/parkinson` (37); `X;Y;Z;Pressure;GripAngle;Timestamp;TestID`, ~7 ms sample interval; Test 0 = static spiral (readme says Test 2 is circular motion).
- Used: **hw_dataset only, Test 0, x/y/time only, pen-up (pressure 0) dropped**: 40 subjects (15 control, 25 PD). `new_dataset` excluded (PD only; a classifier separates it from hw PD with AUC 0.81, so protocol would leak).
- Dataset frame assumed centre (200, 200), radius 200.

**Motion** (not downloaded)
- Chosen: **PADS** (PhysioNet, DOI 10.13026/m0w9-zx22, CC BY-NC-SA 4.0): 469 participants, two Apple Watches (accel g, gyro rad/s, 100 Hz), 11 seated tasks of 10-20 s; groups PD / DD / HC (a secondary paper says 291 / 99 / 79; recompute from `patients/*.json`). 735 MB zip.
- Plan: tasks `Relaxed` and `StretchHold`; one row per subject x task x wrist, grouped by subject (GroupKFold); PD vs HC first (consider PD vs HC+DD); trim first 0.5 s.

## 5. Drawing evaluation results (real output, 40 subjects, repeated stratified 5-fold x20, threshold 0.5)
- Random forest: AUC 0.855, sensitivity 0.84, specificity 0.74 (typical confusion: ~11/15 controls, ~21/25 PD correct).
- Logistic regression: AUC 0.74. SVM: AUC 0.68, specificity 0.34.
- Label-permutation check: permuted AUC ~0.50, p ~0.01, so real signal.
- Best features (univariate AUC): radial residual RMS 0.84, speed CV 0.76, heading-change std 0.73; tremor-band features near chance.
- Trained on hw data, the RF flags 34/36 new_dataset PD (positives only; specificity unmeasurable).
- Caveats: only 40 subjects (one control = ~7 points of specificity); +/- values are across CV repeats, not confidence intervals; model chosen among 3 on the same CV (mildly optimistic); every PD file is dated 2012-13 and every control 2014/2016 (likely different sessions); **trained on stylus-on-tablet data; mouse/finger transfer is untested**.

## 6. Deferred (see TODO.md)
- Drawing: save RF + metadata, wire prediction (canvas frame `Frame(300, 300, 250)`, time ms / 1000), show result labelled unvalidated, run a ~10-spiral mouse/phone sanity check.
- Voice: get dataset, voice features (Praat/parselmouth or librosa), train, wire.
- Motion: download PADS, run extraction script locally, upload CSV, train, wire.

## 7. Still to do after that
- Phase 5 fusion: modality-specific outputs combined (mean/weighted/stacking); with unpaired data this is a prototype architecture, say so; handle missing modalities by averaging those available; `POST /api/screening/analyze`, `GET /api/model-info`.
- Phase 6: results page (overall score, per-modality scores, charts, feature contributions), about page, navigation, loading/error states, accessibility, responsive.
- Phase 7: end-to-end testing; README sections (overview, motivation, research gap, results, limitations, ethics, privacy approach, future work).

## 8. Suggested way to resume
1. Upload `parkinsons-ai.zip` and this file. Ask Claude to read `TODO.md` and `ml/DATASETS.md`.
2. Fastest path to a working demo: finish Drawing (the data is already analysed; re-upload the UCI zip only if retraining). Then Phase 5/6 with whichever modalities have models, and add voice/motion when their data is available.
