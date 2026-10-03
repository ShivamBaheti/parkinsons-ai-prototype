# To-do (deferred work)

## Voice
- [ ] Get a raw-audio dataset. Preferred: ItalianPVS (IEEE DataPort; download was failing). Fallback: Arkansas phone recordings (figshare). See `ml/DATASETS.md`.
- [ ] Explore, extract features, train with subject-level CV, save model to `backend/models/voice_model.pkl`.
- [ ] Add feature extraction + prediction to `/api/voice/analyze` (currently validation only; returns `model_unavailable`).

## Drawing
- [ ] Save the chosen model (random forest on hw_dataset, 40 subjects) plus a metadata file with metrics and caveats.
- [ ] Add prediction to `/api/drawing/analyze` (currently validation only) and show the result in the UI, labelled unvalidated on mouse/touch.
- [ ] Domain-shift check: draw ~10 spirals on a mouse/phone and see whether healthy drawings get high scores.
- [ ] Known caveats: 40 subjects only; PD and controls likely recorded in different sessions; guide-spiral frame is approximate.

## Motion
- [ ] Download PADS (see DATASETS.md), run `ml/scripts/extract_motion_features.py` locally, train with subject-level CV.
- [ ] Decide PD vs HC only, or PD vs HC+DD (more realistic for screening).

## General
- [ ] Phase 5 fusion, Phase 6 UI polish, Phase 7 end-to-end testing.
- [ ] Fill in the remaining README sections.
