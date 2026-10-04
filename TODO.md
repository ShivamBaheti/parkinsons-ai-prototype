# To-do (deferred work)

All three ML models are deferred, so the app currently validates inputs but returns no screening results.

## Drawing (closest to done: evaluation finished, model not yet saved)
- [x] Final fit saved (`ml/scripts/save_drawing_model.py` -> `backend/models/drawing_model.pkl` + `.json` with real CV metrics); `/api/drawing/analyze` returns a score, labelled unvalidated for mouse/touch; UI shows the note.
- [ ] Domain-shift check: ~10 spirals on a mouse/phone; do healthy drawings score high?
- [ ] Caveats to keep stating: 40 subjects; PD and controls likely recorded in different sessions; frame is approximate.

## Voice
- [ ] Get a raw-audio dataset. Preferred: ItalianPVS (IEEE DataPort, DOI 10.21227/aw6b-tg17; download was failing). Fallback: Arkansas phone recordings (figshare, DOI 10.6084/m9.figshare.23849127).
- [ ] Explore, write `backend/app/features/voice_features.py`, train with speaker-level CV (PD vs age-comparable elderly controls), save `voice_model.pkl`.
- [ ] Add feature extraction + prediction to `/api/voice/analyze`.

## Motion
- [ ] Download PADS (PhysioNet, 735 MB zip), run `ml/scripts/extract_motion_features.py <path> --limit 20`, then the full run; share `motion_features.csv`.
- [ ] Train with subject-level CV (GroupKFold); decide PD vs HC only, or PD vs HC+DD. Save `motion_model.pkl`, add prediction to `/api/motion/analyze`.

## Not started
- [x] Phase 5 fusion: done (equal-weight mean, prototype; 11 tests). Frontend `analyzeScreening` / `getModelInfo` exist in `lib/api.ts` but are not used by any page yet.
- [x] Phase 6 (core): `/results`, `/about`, shared nav, screening page carries scores to results via the URL. Deliberately plain: bullets and CSS bars, no Recharts/Framer Motion/Lucide, no card components.
- [ ] Phase 6 leftovers: signal visualisation (e.g. the drawn spiral on the results page), mobile/accessibility pass.
- [x] `turns` check done (`ml/scripts/ablate_drawing.py`, `ml/results/drawing_ablation.txt`): turns+duration+path_length alone give AUC 0.81; model without them AUC 0.77. Deployed model now excludes them (re-run `save_drawing_model.py` locally to refresh metrics).
- [ ] Phase 7: end-to-end testing; fill remaining README sections (privacy, limitations, ethics).

## Voice (ItalianPVS) - status: evaluated, NOT wired, do not use as a screening signal yet
- Data uploaded and inventoried (`ml/scripts/explore_voice.py`): 28 PD, 22 elderly HC, 15 young HC. Young HC have no sustained vowels (reading only), so they are unused. Names in folder names are replaced by anonymous IDs; keep `ml/data/raw/` out of git and out of any zip.
- Features: `backend/app/features/voice_features.py` (9 Praat features on a steady central <=3 s segment, resampled to 16 kHz, no absolute pitch). Extraction: `ml/scripts/extract_voice_features.py`.
- Evaluation (`ml/scripts/train_voice.py`, `ml/results/voice_evaluation.txt`): person-level CV gives AUC 0.91 (LR) / 0.90 (RF) for 28 PD vs 22 HC on vowel /a/.
- Why it is not trusted: the direction is physiologically backwards. PD median shimmer is about half that of the elderly controls (0.028 vs 0.058; healthy controls above the usual ~0.04 upper range) and HNR is higher in PD (22.9 vs 18.9 dB). Recording protocol clearly differs between groups (controls have silent lead-ins, PD recordings are continuous; 10 PD people were recorded at 44.1 kHz with digital-silence padding). The model is probably separating recording sessions/devices, not disease.
- 44.1 kHz vs 16 kHz PD sessions are NOT separable (AUC 0.59-0.65), so sample rate itself is not the problem; the PD-vs-control session difference is the likely one and cannot be tested within this dataset.
- Next options: (1) external check on the Arkansas phone /a/ recordings (figshare 10.6084/m9.figshare.23849127), which are a different group of people and a different setup; (2) record a few healthy volunteers with the web recorder and see where the model puts them; (3) use voice only as a demo with a clear "unreliable" label, or drop it and say why in the report.
