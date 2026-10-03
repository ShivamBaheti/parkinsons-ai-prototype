"""Template-free kinematic features from a drawn spiral trajectory (x, y, time only).

The SAME function is used for training (ml/scripts/train_drawing.py) and live inference,
so features cannot drift apart. Pressure and pen angle are deliberately not used: a mouse or
finger cannot supply them.
"""
from dataclasses import dataclass

import numpy as np
from scipy.signal import savgol_filter, welch

RESAMPLE_HZ = 50.0
FEATURE_NAMES = [
    "duration_s", "path_length", "turns",
    "speed_mean", "speed_std", "speed_cv", "pause_fraction",
    "accel_rms", "jerk_rms",
    "tremor_band_ratio", "tremor_peak_hz",
    "heading_change_std", "radial_residual_rms",
]


@dataclass(frozen=True)
class Frame:
    """Coordinate frame of the guide spiral: its centre and outer radius, in input units."""
    cx: float
    cy: float
    radius: float


def clean_trajectory(x, y, t_s):
    """Drop non-finite samples and any sample whose time does not advance."""
    x, y, t = (np.asarray(a, dtype=float) for a in (x, y, t_s))
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(t)
    x, y, t = x[ok], y[ok], t[ok]
    if len(t) == 0:
        return x, y, t
    keep = np.concatenate([[True], t[1:] > np.maximum.accumulate(t)[:-1]])
    return x[keep], y[keep], t[keep]


def extract_features(x, y, t_s, frame: Frame) -> dict[str, float]:
    x, y, t = clean_trajectory(x, y, t_s)
    if len(t) < 20 or t[-1] - t[0] < 1.0:
        raise ValueError("trajectory too short to extract features")

    # Normalise space by the guide radius and resample to a uniform time grid.
    xn, yn = (x - frame.cx) / frame.radius, (y - frame.cy) / frame.radius
    grid = np.arange(t[0], t[-1], 1.0 / RESAMPLE_HZ)
    xs, ys = np.interp(grid, t, xn), np.interp(grid, t, yn)

    # Smoothed derivatives (Savitzky-Golay) to limit digitiser noise amplification.
    win, dt = 9, 1.0 / RESAMPLE_HZ
    d = lambda s, n: savgol_filter(s, win, 3, deriv=n, delta=dt)
    vx, vy = d(xs, 1), d(ys, 1)
    ax, ay = d(xs, 2), d(ys, 2)
    jx, jy = d(xs, 3), d(ys, 3)
    speed = np.hypot(vx, vy)

    # Tremor: share of 4-8 Hz power within 1-12 Hz in the high-passed speed signal.
    detrended = speed - savgol_filter(speed, 51, 2)
    freqs, psd = welch(detrended, fs=RESAMPLE_HZ, nperseg=min(128, len(detrended)))
    band = lambda lo, hi: (freqs >= lo) & (freqs <= hi)
    total = psd[band(1, 12)].sum()
    tremor_ratio = psd[band(4, 8)].sum() / total if total > 0 else 0.0
    search = band(2, 12)
    peak_hz = freqs[search][np.argmax(psd[search])] if total > 0 else 0.0

    # Heading changes and spiral regularity (radius should grow smoothly with angle).
    heading = np.unwrap(np.arctan2(vy, vx))
    theta = np.unwrap(np.arctan2(ys, xs))
    r = np.hypot(xs, ys)
    fit = np.polyval(np.polyfit(theta, r, 3), theta)

    return {
        "duration_s": float(t[-1] - t[0]),
        "path_length": float(np.hypot(np.diff(xs), np.diff(ys)).sum()),
        "turns": float(abs(theta[-1] - theta[0]) / (2 * np.pi)),
        "speed_mean": float(speed.mean()),
        "speed_std": float(speed.std()),
        "speed_cv": float(speed.std() / speed.mean()) if speed.mean() > 0 else 0.0,
        "pause_fraction": float((speed < 0.1 * np.median(speed)).mean()),
        "accel_rms": float(np.sqrt(np.mean(ax**2 + ay**2))),
        "jerk_rms": float(np.sqrt(np.mean(jx**2 + jy**2))),
        "tremor_band_ratio": float(tremor_ratio),
        "tremor_peak_hz": float(peak_hz),
        "heading_change_std": float(np.diff(heading).std()),
        "radial_residual_rms": float(np.sqrt(np.mean((r - fit) ** 2))),
    }
