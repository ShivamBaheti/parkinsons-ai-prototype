"""Sustained-vowel voice features (Praat via parselmouth). Same code is used for training and inference.

Design choices to avoid learning recording artefacts rather than voice:
- everything is resampled to 16 kHz first (the dataset mixes 16 kHz and 44.1 kHz recordings);
- only a steady central segment (at most 3 s) is analysed, so recording length does not matter;
- absolute pitch (f0 mean) is not used, because it mostly reflects sex and age; pitch variation is
  expressed relative to the mean (f0_cv).
"""
import math

import numpy as np
from scipy.signal import resample_poly

TARGET_SR = 16000
EDGE_TRIM_S = 0.25
MAX_SEGMENT_S = 3.0
MIN_SEGMENT_S = 1.0
F0_MIN, F0_MAX = 75.0, 500.0

FEATURE_NAMES = [
    "f0_cv", "jitter_local", "jitter_rap", "jitter_ppq5",
    "shimmer_local", "shimmer_apq3", "shimmer_apq5", "hnr_db", "voiced_fraction",
]


def steady_segment(signal: np.ndarray, sr: int) -> np.ndarray:
    """Resample to 16 kHz, trim the edges, return the central <= 3 s. Raises ValueError if too short."""
    x = np.asarray(signal, dtype=np.float64)
    if sr != TARGET_SR:
        g = math.gcd(int(sr), TARGET_SR)
        x = resample_poly(x, TARGET_SR // g, int(sr) // g)
    trim = int(EDGE_TRIM_S * TARGET_SR)
    x = x[trim:-trim] if len(x) > 2 * trim else x[:0]
    if len(x) < MIN_SEGMENT_S * TARGET_SR:
        raise ValueError("Recording too short for voice analysis.")
    n = int(MAX_SEGMENT_S * TARGET_SR)
    if len(x) > n:
        start = (len(x) - n) // 2
        x = x[start:start + n]
    peak = float(np.max(np.abs(x)))
    if peak < 1e-4:
        raise ValueError("Recording is silent.")
    return x / peak * 0.5  # fixed level so loudness does not matter


def extract_features(signal: np.ndarray, sr: int) -> dict[str, float]:
    """Return the 9 voice features. Raises ValueError if the voice cannot be analysed (e.g. no voiced sound)."""
    import parselmouth
    from parselmouth.praat import call

    x = steady_segment(signal, sr)
    snd = parselmouth.Sound(x, sampling_frequency=TARGET_SR)
    pitch = snd.to_pitch_ac(pitch_floor=F0_MIN, pitch_ceiling=F0_MAX)
    f0 = pitch.selected_array["frequency"]
    voiced = f0[f0 > 0]
    if len(voiced) < 20:
        raise ValueError("No steady voiced sound found.")

    points = call(snd, "To PointProcess (periodic, cc)", F0_MIN, F0_MAX)
    if call(points, "Get number of points") < 10:
        raise ValueError("No steady voiced sound found.")
    args = (0, 0, 0.0001, 0.02, 1.3)
    jitter = lambda kind: call(points, f"Get jitter ({kind})", *args)  # noqa: E731
    shimmer = lambda kind: call([snd, points], f"Get shimmer ({kind})", 0, 0, 0.0001, 0.02, 1.3, 1.6)  # noqa: E731
    hnr = call(snd.to_harmonicity_cc(), "Get mean", 0, 0)

    feats = {
        "f0_cv": float(np.std(voiced) / np.mean(voiced)),
        "jitter_local": jitter("local"), "jitter_rap": jitter("rap"), "jitter_ppq5": jitter("ppq5"),
        "shimmer_local": shimmer("local"), "shimmer_apq3": shimmer("apq3"), "shimmer_apq5": shimmer("apq5"),
        "hnr_db": hnr, "voiced_fraction": float(len(voiced) / len(f0)),
    }
    if not all(math.isfinite(v) for v in feats.values()):
        raise ValueError("Voice features could not be computed.")
    return {k: float(v) for k, v in feats.items()}
