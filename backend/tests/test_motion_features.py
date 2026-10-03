import numpy as np
import pytest

from app.features.motion_features import FEATURE_NAMES, extract_features

rng = np.random.default_rng(0)


def signal(freq=None, fs=100.0, seconds=15, amp=0.05, noise=0.005):
    t = np.arange(int(fs * seconds)) / fs
    acc = rng.normal(0, noise, (len(t), 3))
    gyro = rng.normal(0, noise * 4, (len(t), 3))
    acc[:, 2] += 1.0  # gravity
    if freq:
        wave = amp * np.sin(2 * np.pi * freq * t)
        acc[:, 0] += wave
        acc[:, 1] += 0.5 * wave
        gyro[:, 0] += 4 * wave
    return acc, gyro, t


def test_detects_tremor_frequency_and_band_power():
    f = extract_features(*signal(freq=5.0))
    assert set(f) == set(FEATURE_NAMES)
    assert abs(f["acc_peak_hz"] - 5.0) < 0.4 and abs(f["gyro_peak_hz"] - 5.0) < 0.4
    assert f["acc_tremor_ratio"] > 0.7


def test_no_tremor_has_low_band_ratio_and_amplitude():
    quiet, shaky = extract_features(*signal()), extract_features(*signal(freq=5.0))
    assert quiet["acc_tremor_ratio"] < 0.3
    assert quiet["acc_rms"] < shaky["acc_rms"]
    assert quiet["acc_peak_concentration"] < shaky["acc_peak_concentration"]


def test_rotation_invariance():
    acc, gyro, t = signal(freq=5.0)
    theta = 0.9
    R = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])
    a, b = extract_features(acc, gyro, t), extract_features(acc @ R.T, gyro @ R.T, t)
    for k in FEATURE_NAMES:
        assert b[k] == pytest.approx(a[k], rel=0.05, abs=0.02), k


def test_sampling_rate_independence():
    f100 = extract_features(*signal(freq=5.0, fs=100.0))
    f50 = extract_features(*signal(freq=5.0, fs=50.0))
    assert f50["acc_peak_hz"] == pytest.approx(f100["acc_peak_hz"], abs=0.4)
    assert f50["acc_rms"] == pytest.approx(f100["acc_rms"], rel=0.15)


def test_too_short_rejected():
    with pytest.raises(ValueError):
        extract_features(*signal(seconds=3))
