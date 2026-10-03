# Dataset documentation (voice modality)

Rule for this file: nothing is stated as fact unless it was read from a source.
Where a value could not be verified it says **unavailable / to verify**. Counts
marked "to verify" must be recomputed from the downloaded files and corrected here.

## Why raw audio is required
The app records audio in the browser and extracts features on the server.
Training features must come from the same extraction code as inference features.
Datasets that ship only pre-computed features (UCI Oxford, UCI Istanbul) cannot
meet this, because their original feature extraction (e.g. MDVP measures, TQWT)
cannot be reproduced from a browser recording.

## Selected for training: Italian Parkinson's Voice and Speech (ItalianPVS)
- Source: Dimauro & Girardi, IEEE DataPort, DOI 10.21227/aw6b-tg17
  (https://ieee-dataport.org/open-access/italian-parkinsons-voice-and-speech)
- Licence: CC BY 4.0 per one paper using the data. **Verify on the DataPort page.**
- Access: listed as open access. A free DataPort account may be required (to verify).
- Participants (per secondary sources): 28 PD, 22 elderly healthy controls (ages
  66-77), 15 young healthy controls (ages 19-29). Papers disagree on some
  demographics (sex split, age ranges): **take the values from the dataset's own metadata.**
- Samples: each speaker recorded five sustained vowels (a, e, i, o, u), two
  repetitions each, plus reading tasks. Total file counts: **unavailable until download**
  (secondary sources quote 495 and 593 vowel recordings for different subsets).
- Features: none provided (raw audio). We extract features ourselves.
- Target: PD vs healthy control. Label source (folder/file naming): **to verify.**
- Recording methodology: 16 kHz, quiet echo-free room, speaker 15-25 cm from the microphone.
- Participant identifiers: to verify (expected: speaker folder/file name).
  Several recordings per speaker, so **participant-level splitting is mandatory.**
- Limitations (known now):
  - About 50 older speakers: very wide confidence intervals on every metric.
  - Young healthy controls (19-29) would let a model learn age. Plan: train on
    PD vs age-comparable elderly controls only; report young controls separately.
  - Lab-quality, Italian-speaking cohort, 16 kHz: browser microphone audio is a
    different recording condition, so live-app scores are NOT validated.
  - Mostly a single region (Bari), single recording site.

## Optional external check: Arkansas phone-recorded /a/ (figshare)
- Source: Iyer, Kemp, ... Virmani, figshare DOI 10.6084/m9.figshare.23849127;
  paper: Sci Rep 13:20615 (2023). A correction was published in 2026 (not read).
- Licence: CC BY 4.0 (figshare record).
- Collected: 50 PD + 50 HC; 40 PD + 41 HC remained after the authors' preprocessing.
  Files in the figshare record: **unavailable (page blocked), to verify.**
- Recording: sustained /a/ by phone voicemail, 8 kHz, 16-bit.
- Metadata file: sample ID, age, sex, label.
- Limitations: controls ~47.9 +/- 14.5 y vs PD ~66.6 +/- 9.0 y (age confound);
  controls self-reported; 8 kHz telephone audio.
- Use: evaluation only, never mixed into training, to measure cross-dataset
  generalisation honestly.

## Not used
- UCI Oxford Parkinsons (id 174): 31 people, 23 PD, 195 recordings, CC BY 4.0.
  Pre-computed features only. Page lists 197 instances vs 195 recordings.
- UCI Parkinson's Disease Classification (Istanbul): 252 subjects, 756 recordings,
  pre-computed features only. Licence not verified on UCI.
- UCI Multiple Sound Recordings (id 301): test set contains PD patients only.
- MDVR-KCL: 37 participants (16 PD, 21 HC), read text and conversation, no
  sustained vowels. Licence not verified.
- NeuroVoz: requires a signed data-use agreement.
- PC-GITA: availability not verified.

---

# Dataset documentation (drawing modality)

## Selected: Parkinson Disease Spiral Drawings Using Digitized Graphics Tablet (UCI id 395)
- Source: Isenkul, Sakar & Kursun, Istanbul University (Cerrahpasa Faculty of Medicine);
  UCI DOI 10.24432/C5Q01S. Download: 3.5 MB zip, 129 files listed.
- Licence: CC BY 4.0 (read on the UCI page).
- Participants (UCI page): 62 people with PD and 15 healthy controls (77 total).
  **Sources disagree:** one paper reports 25 PD + 15 controls, another 61 PD + 61 controls.
  The UCI file listing shows two folders (hw_dataset, new_dataset).
  **Must be resolved from the files before any modelling.**
- Class balance (per UCI counts): about 81% PD / 19% healthy, so accuracy is
  meaningless here; report sensitivity, specificity, ROC-AUC, and PR-AUC.
  Only 15 controls: specificity will be very noisy.
- Recordings: three tests per subject: Static Spiral Test (SST: trace a displayed spiral), Dynamic Spiral Test (DST: the spiral blinks), and
  Circular Motion Test (readme: draw circles around a red point; the UCI page calls this a stability test, the readme is taken as authoritative).
  Whether every subject has all three tests: to verify.
- Signals (per papers): pen x, y, pressure, pen angle, timestamp. Exact column
  names, units and sampling rate: **unavailable until the files are read.**
- Target: PD vs healthy, from folder name (parkinson / control). To verify.
- Participant identifiers: from file names (e.g. P_..., C_...). To verify; a subject may have
  several files, so split by subject.
- Limitations / risks (known now):
  - Recorded with a Wacom pen on a tablet, tracing a template. The web canvas will be
    finger/mouse. Pressure and pen angle are unavailable on mouse, so the model will use
    **x, y, time only**, so the same features can be computed live.
  - Tablet coordinates and the template's size differ from the web canvas, so features
    must be scale- and time-normalised (e.g. relative to the spiral's radius).
  - Only SST is replicable in the app (the web canvas shows a fixed guide spiral).
  - Possible confound: if PD and control subjects were recorded in different folders/protocols,
    the model could learn the protocol instead of the disease. Check before training.
  - Very small cohort (15 controls).

## Not selected
- Kaggle "Parkinson's Drawings (Spiral and Wave)": images only (no timing). Statistics and
  licence not verified. Possible later option for an image-based model.

### Verified from the downloaded files (supersedes "to verify" above)
- Layout: hw_dataset/control (15 files), hw_dataset/parkinson (25), new_dataset/parkinson (37),
  hw_drawings (images, unused). One file per subject: 15 controls + 62 PD = 77, matching UCI.
- Format: `X;Y;Z;Pressure;GripAngle;Timestamp;TestID` (semicolon-separated, no header, per readme).
  Median sample interval 7 (consistent with milliseconds, about 143 Hz; unit is inferred, not documented).
- Static Spiral Test present in all 40 hw subjects and 36 of 37 new_dataset PD (H_p000-0017 has none, excluded).
- Coordinates: spirals start near (200, 200) and end near (400, 200), so the guide frame is
  approximately centre (200, 200), radius 200 (an assumption; the template geometry is not documented).
- Data quality: 24 backward timestamp steps across 14 file/test pairs (handled by dropping
  non-advancing samples); about 19% of hw samples have zero pressure (pen hovering, dropped).
- **Protocol confound (new_dataset):** contains PD only, and differs from hw_dataset: median
  static-spiral duration 13.0 s vs 21.2 s (control) / 25.8 s (hw PD), and 5% vs 19% zero-pressure samples.
  A classifier separates hw-PD from new-PD with AUC 0.81. Hence new_dataset is excluded from training.
- **Session confound (within hw_dataset):** zip file dates are 2012-2013 for every PD file but 2014 or 2016
  for every control file. Zip dates may not be recording dates, but PD and controls were probably
  not recorded together, so device/session differences could contribute to separation. Cannot be tested here.
