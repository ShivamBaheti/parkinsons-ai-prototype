"""Input validation. Raises ValidationError with a user-safe message."""
import io
from dataclasses import dataclass

import numpy as np
import soundfile as sf

MAX_AUDIO_BYTES = 10 * 1024 * 1024
MIN_AUDIO_SECONDS = 1.5
MAX_AUDIO_SECONDS = 60.0
MIN_SAMPLE_RATE = 8000
SILENCE_PEAK = 0.01  # peak amplitude (full scale = 1.0) below this counts as silence


class ValidationError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class AudioInfo:
    duration_s: float
    sample_rate: int
    peak: float


def read_audio(data: bytes) -> tuple[np.ndarray, int]:
    """Decode WAV bytes to a mono float32 signal. Never trusts the filename or content-type."""
    if not data:
        raise ValidationError("empty_file", "The uploaded file is empty.")
    if len(data) > MAX_AUDIO_BYTES:
        raise ValidationError(
            "file_too_large",
            f"The audio file is larger than {MAX_AUDIO_BYTES // (1024 * 1024)} MB.",
            status_code=413,
        )
    try:
        signal, sample_rate = sf.read(io.BytesIO(data), dtype="float32", always_2d=True)
    except Exception:
        raise ValidationError(
            "invalid_audio", "The file could not be read as a WAV audio recording."
        ) from None
    return signal.mean(axis=1), int(sample_rate)


def validate_audio(data: bytes) -> tuple[np.ndarray, int, AudioInfo]:
    signal, sample_rate = read_audio(data)
    if sample_rate < MIN_SAMPLE_RATE:
        raise ValidationError(
            "sample_rate_too_low", "The recording's sample rate is too low to analyse."
        )
    duration = len(signal) / sample_rate
    if duration < MIN_AUDIO_SECONDS:
        raise ValidationError(
            "audio_too_short",
            f"The recording is too short ({duration:.1f}s). Please record at least {MIN_AUDIO_SECONDS:.1f} seconds.",
        )
    if duration > MAX_AUDIO_SECONDS:
        raise ValidationError(
            "audio_too_long",
            f"The recording is too long. Please keep it under {int(MAX_AUDIO_SECONDS)} seconds.",
        )
    if not np.isfinite(signal).all():
        raise ValidationError("invalid_audio", "The audio contains invalid data.")
    peak = float(np.abs(signal).max())
    if peak < SILENCE_PEAK:
        raise ValidationError(
            "no_sound_detected",
            "No sound was detected. Check your microphone and try again.",
        )
    return signal, sample_rate, AudioInfo(round(duration, 2), sample_rate, round(peak, 3))


# ---- Drawing ----------------------------------------------------------------
MIN_DRAWING_POINTS = 50
MIN_DRAWING_SECONDS = 2.0
MIN_DRAWING_EXTENT = 0.15  # drawing must span at least 15% of the canvas width or height


@dataclass(frozen=True)
class DrawingInfo:
    n_points: int
    duration_s: float
    n_strokes: int


def validate_drawing(
    xs: list[float], ys: list[float], ts_ms: list[float], strokes: list[int], canvas_size: float
) -> DrawingInfo:
    n = len(xs)
    if n == 0:
        raise ValidationError("empty_drawing", "Nothing was drawn. Please trace the spiral first.")
    if n < MIN_DRAWING_POINTS:
        raise ValidationError(
            "drawing_too_short", "The drawing is too short. Please trace the whole spiral."
        )
    if any(b < a for a, b in zip(ts_ms, ts_ms[1:])):
        raise ValidationError("invalid_timestamps", "The drawing's timestamps are out of order.")
    duration = (ts_ms[-1] - ts_ms[0]) / 1000.0
    if duration < MIN_DRAWING_SECONDS:
        raise ValidationError(
            "drawing_too_fast",
            f"The drawing was completed in {duration:.1f}s, which is too fast to analyse. Please trace the spiral slowly.",
        )
    extent = max(max(xs) - min(xs), max(ys) - min(ys)) / canvas_size
    if extent < MIN_DRAWING_EXTENT:
        raise ValidationError(
            "drawing_too_small", "The drawing covers too little of the canvas. Please trace the whole spiral."
        )
    return DrawingInfo(n, round(duration, 2), len(set(strokes)))


# ---- Motion -----------------------------------------------------------------
MAX_CSV_BYTES = 10 * 1024 * 1024
MOTION_COLUMNS = ["timestamp", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]
MIN_MOTION_SECONDS = 5.0
MIN_MOTION_HZ = 20.0


@dataclass(frozen=True)
class MotionInfo:
    n_samples: int
    duration_s: float
    sample_rate_hz: float
    assumptions: list[str]


def validate_motion_csv(data: bytes):
    """Parse and validate a motion CSV. Returns (DataFrame with columns MOTION_COLUMNS, MotionInfo).

    Assumes timestamp in seconds (milliseconds are detected), accel in g (m/s^2 is detected and
    converted) and gyro in rad/s. Every assumption applied is reported back.
    """
    import pandas as pd

    if not data:
        raise ValidationError("empty_file", "The uploaded file is empty.")
    if len(data) > MAX_CSV_BYTES:
        raise ValidationError("file_too_large", "The CSV file is larger than 10 MB.", status_code=413)
    try:
        df = pd.read_csv(io.BytesIO(data))
    except Exception:
        raise ValidationError("invalid_csv", "The file could not be read as a CSV.") from None
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in MOTION_COLUMNS if c not in df.columns]
    if missing:
        raise ValidationError(
            "missing_columns", "The CSV is missing required columns: " + ", ".join(missing) + "."
        )
    df = df[MOTION_COLUMNS].apply(pd.to_numeric, errors="coerce").dropna()
    if len(df) < 10:
        raise ValidationError("invalid_csv", "The CSV has too few valid numeric rows.")
    t = df["timestamp"].to_numpy(dtype=float)
    if (np.diff(t) <= 0).any():
        raise ValidationError("invalid_timestamps", "Timestamps must be strictly increasing.")
    assumptions = []
    if np.median(np.diff(t)) >= 1.0:  # a 1 s step would be useless, so this must be milliseconds
        df["timestamp"] = t / 1000.0
        assumptions.append("timestamps treated as milliseconds")
    duration = float(df["timestamp"].iloc[-1] - df["timestamp"].iloc[0])
    rate = 1.0 / float(np.median(np.diff(df["timestamp"].to_numpy())))
    if duration < MIN_MOTION_SECONDS:
        raise ValidationError(
            "motion_too_short",
            f"The recording is {duration:.1f}s long. Please provide at least {MIN_MOTION_SECONDS:.0f} seconds.",
        )
    if rate < MIN_MOTION_HZ:
        raise ValidationError(
            "sample_rate_too_low",
            f"The sampling rate ({rate:.0f} Hz) is too low. At least {MIN_MOTION_HZ:.0f} Hz is required.",
        )
    acc_cols = ["accel_x", "accel_y", "accel_z"]
    if 8.0 < np.median(np.linalg.norm(df[acc_cols].to_numpy(), axis=1)) < 11.0:
        df[acc_cols] = df[acc_cols] / 9.80665
        assumptions.append("acceleration treated as m/s^2 and converted to g")
    return df, MotionInfo(len(df), round(duration, 2), round(rate, 1), assumptions)
