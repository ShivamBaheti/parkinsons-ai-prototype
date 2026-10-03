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
