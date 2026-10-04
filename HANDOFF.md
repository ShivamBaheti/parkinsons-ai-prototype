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
- The user confirmed the app runs and works on their machine (drawing flow and results page). The voice recorder with a real microphone and the motion uploader have not been confirmed.
- Do not use `pkill -f "<pattern>"` where the pattern also appears in the command (it kills its own shell). Use `ps aux | grep "[u]vicorn" | awk '{print $2}' | xargs -r kill`.
- `sh` has no brace expansion: use explicit `mkdir` lists.
- Headless Chrome exists in the sandbox (`/home/claude/.cache/puppeteer/chrome/*/chrome-linux64/chrome`), so pages can be rendered with `--dump-dom` / `--screenshot` (a window narrower than ~500 px gets cropped, a screenshot artifact). Start servers with `setsid nohup ... &` in their own command; don't `pkill` in the same command as other work.
- Next.js here is v16 (breaking changes vs older versions); the scaffold's `AGENTS.md`/`CLAUDE.md` in `frontend/` say to read `node_modules/next/dist/docs`. React lint rule `set-state-in-effect` is active.
- Run backend: `cd backend`, `.venv\Scripts\activate`, `pip install -r requirements.txt`, `uvicorn app.main:app --reload --port 8000`. Run frontend: `cd frontend`, `copy .env.local.example .env.local`, `npm install`, `npm run dev`. Use `http://localhost:3000` (not the network IP, or CORS fails).

## 3. Current state (final for now: the user chose to stop adding features)
**Frontend** (`frontend/`): `/` landing, `/screening` (Voice, Drawing, Motion steps, each with a status line, plus a "View combined result" link), `/results?voice=&drawing=&motion=` (scores come in the URL; the page calls `POST /api/screening/analyze` and `GET /api/model-info`), `/about`, shared `SiteNav`. Deliberately plain: bullets and CSS bars, no Recharts/Framer Motion/Lucide/cards.
**Backend** (`backend/`, 44 passing tests): health, voice/drawing/motion analyze, screening analyze, model-info. Errors are `{"error", "message"}`; no stack traces. Uploads are processed in memory only.
- Drawing: real model (`backend/models/drawing_model.pkl/.json`), random forest on 10 features (turns, duration_s, path_length excluded after `ml/results/drawing_ablation.txt` showed they carry protocol signal). Saved CV (sandbox sklearn 1.8): AUC 0.77, sens 0.79, spec 0.59. Labelled unvalidated for mouse/touch.
- Voice: real model (logistic regression, 9 Praat features via parselmouth) but flagged `reliable: false`. CV AUC 0.91 is not trusted: PD shimmer is half that of controls, HNR higher, recording setups differ (see `ml/results/voice_*.txt`, TODO.md). Shown as a demo and excluded from the combined score via `EXCLUDED_FROM_SCORE = {"voice"}` in `fusion_model.py`.
- Motion: no model. `/api/motion/analyze` validates the CSV and returns 503 `model_unavailable`. 12-feature extractor exists, tested on synthetic data only. PADS download failed for the user.
- Fusion: equal-weight mean of the reliable modalities (so currently drawing only); unvalidated by design (unpaired datasets).
**ML** (`ml/`): `DATASETS.md`; scripts `explore_drawing`, `train_drawing`, `ablate_drawing`, `save_drawing_model`, `explore_voice`, `extract_voice_features`, `train_voice`, `save_voice_model`, `extract_motion_features`; results in `ml/results/`. Raw data is git-ignored and not in the zip. Voice folder names are real people's names: only anonymous IDs (PD01, EHC01...) are written anywhere.
**Docs**: README is complete (all sections, real numbers, limitations, ethics); TODO.md lists what is left.

## 4. Datasets (verified from the user's files)
- Drawing: UCI spiral tablet set (id 395), hw_dataset static spiral only, 40 people (15 control, 25 PD); `new_dataset` excluded (PD only, different protocol).
- Voice: ItalianPVS, vowel /a/, 28 PD vs 22 elderly HC (mean age 67.2 vs 67.1; sex 19M/9F vs 10M/12F). Young HC have no vowels. 10 PD people were recorded at 44.1 kHz, everyone else at 16 kHz.
- Motion: PADS (PhysioNet, CC BY-NC-SA 4.0) chosen, not downloaded.

## 5. If resumed
- Re-upload `parkinsons-ai.zip` and this file. Optional next steps (all were declined for now): external voice check on the Arkansas phone recordings (figshare 10.6084/m9.figshare.23849127); a ~10-spiral mouse/phone sanity check; motion with PADS or a smaller dataset; spiral visualisation on the results page; Phase 7 end-to-end/accessibility pass.
- After unzipping, re-run `save_drawing_model.py` and `save_voice_model.py` (in `ml/scripts`) so saved metrics match the local scikit-learn version, and `pip install -r requirements.txt` (includes praat-parselmouth).
