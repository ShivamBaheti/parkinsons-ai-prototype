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
- [ ] Investigate: `turns` is the top-importance drawing feature (univariate AUC 0.20). It may reflect how many turns people drew in each protocol rather than disease.
- [ ] Phase 7: end-to-end testing; fill remaining README sections (privacy, limitations, ethics).
