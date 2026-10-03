"""Orientation-independent features from accelerometer (g) and gyroscope (rad/s) recordings.

Used for BOTH training and live inference. Gravity and slow drift are removed with a 0.5 Hz
high-pass; all features come from vector magnitudes / summed per-axis power, so they do not
depend on how the device is rotated (a phone and a watch are held differently).
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt, welch

FS = 50.0           # common analysis rate (Hz)
TRIM_START_S = 0.5  # PADS watches vibrate at the start of each recording
MIN_SECONDS = 5.0

FEATURE_NAMES = [
    "acc_rms", "acc_jerk_rms", "acc_rms_cv",
    "acc_tremor_ratio", "acc_peak_hz", "acc_peak_concentration", "acc_spectral_entropy",
    "gyro_rms", "gyro_tremor_ratio", "gyro_peak_hz", "gyro_peak_concentration", "gyro_spectral_entropy",
]


def prepare(acc, gyro, t_s):
    """Clean, trim, anti-alias and resample both sensors onto a uniform FS grid."""
    acc, gyro, t = (np.asarray(a, dtype=float) for a in (acc, gyro, t_s))
    ok = np.isfinite(acc).all(axis=1) & np.isfinite(gyro).all(axis=1) & np.isfinite(t)
    acc, gyro, t = acc[ok], gyro[ok], t[ok]
    keep = np.concatenate([[True], t[1:] > np.maximum.accumulate(t)[:-1]])
    acc, gyro, t = acc[keep], gyro[keep], t[keep]
    m = t >= t[0] + TRIM_START_S
    acc, gyro, t = acc[m], gyro[m], t[m]
    if len(t) < 10 or t[-1] - t[0] < MIN_SECONDS - TRIM_START_S:
        raise ValueError("recording too short")
    fs_in = 1.0 / np.median(np.diff(t))
    if fs_in > 2 * 20.0:  # low-pass below the target Nyquist before resampling
        lp = butter(4, 20.0, btype="low", fs=fs_in, output="sos")
        acc, gyro = sosfiltfilt(lp, acc, axis=0), sosfiltfilt(lp, gyro, axis=0)
    grid = np.arange(t[0], t[-1], 1.0 / FS)
    interp = lambda a: np.column_stack([np.interp(grid, t, a[:, i]) for i in range(3)])
    hp = butter(2, 0.5, btype="high", fs=FS, output="sos")
    return sosfiltfilt(hp, interp(acc), axis=0), sosfiltfilt(hp, interp(gyro), axis=0)


def _spectral(x):
    """Summed per-axis PSD (rotation invariant) -> tremor ratio, peak Hz, concentration, entropy."""
    f, p = welch(x, fs=FS, nperseg=min(256, len(x)), axis=0)
    p = p.sum(axis=1)
    band = (f >= 0.5) & (f <= 12)
    total = p[band].sum()
    if total <= 0:
        return 0.0, 0.0, 0.0, 0.0
    tremor = p[(f >= 4) & (f <= 7)].sum() / total
    search = (f >= 2) & (f <= 12)
    i = np.argmax(np.where(search, p, -np.inf))
    q = p[band] / total
    entropy = -(q[q > 0] * np.log(q[q > 0])).sum() / np.log(len(q))
    return float(tremor), float(f[i]), float(p[i] / total), float(entropy)


def extract_features(acc, gyro, t_s) -> dict[str, float]:
    a, g = prepare(acc, gyro, t_s)
    a_norm, g_norm = np.linalg.norm(a, axis=1), np.linalg.norm(g, axis=1)
    win = int(FS)  # 1 s windows
    n_win = len(a_norm) // win
    win_rms = np.sqrt((a_norm[: n_win * win].reshape(n_win, win) ** 2).mean(axis=1)) if n_win else np.array([0.0])
    jerk = np.linalg.norm(np.diff(a, axis=0) * FS, axis=1)
    at, ap, ac, ae = _spectral(a)
    gt, gp, gc, ge = _spectral(g)
    return {
        "acc_rms": float(np.sqrt(np.mean(a_norm**2))),
        "acc_jerk_rms": float(np.sqrt(np.mean(jerk**2))),
        "acc_rms_cv": float(win_rms.std() / win_rms.mean()) if win_rms.mean() > 0 else 0.0,
        "acc_tremor_ratio": at, "acc_peak_hz": ap, "acc_peak_concentration": ac, "acc_spectral_entropy": ae,
        "gyro_rms": float(np.sqrt(np.mean(g_norm**2))),
        "gyro_tremor_ratio": gt, "gyro_peak_hz": gp, "gyro_peak_concentration": gc, "gyro_spectral_entropy": ge,
    }
