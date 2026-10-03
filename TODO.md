# To-do (deferred work)

All three ML models are deferred, so the app currently validates inputs but returns no screening results.

## Drawing (closest to done: evaluation finished, model not yet saved)
- [ ] Final fit of the random forest on all 40 hw_dataset subjects; save `backend/models/drawing_model.pkl` + a metadata JSON (features, frame, metrics, caveats). `train_drawing.py` currently evaluates only.
- [ ] Add prediction to `/api/drawing/analyze` using `Frame(300, 300, 250)` for the canvas (dataset frame is (200, 200, 200)); time in seconds = ms / 1000.
- [ ] Show the result in the UI, labelled unvalidated on mouse/touch.
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
- [ ] Phase 5 fusion (`api/screening.py`, `models/fusion_model.py`, `POST /api/screening/analyze`, `GET /api/model-info`).
- [ ] Phase 6: `/results` and `/about` pages, `RiskScore`, `ModalityCard`, `ResultsChart`; add Recharts / Framer Motion / Lucide only when used.
- [ ] Phase 7: end-to-end testing; fill remaining README sections (privacy, limitations, ethics).
