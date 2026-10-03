import io

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def csv_bytes(seconds=10.0, fs=100.0, ms=False, scale=1.0, drop=None, extra_ts=None) -> bytes:
    t = np.arange(int(seconds * fs)) / fs
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"timestamp": t * (1000 if ms else 1)})
    for c in ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]:
        df[c] = rng.normal(0, 0.02, len(t))
    df["accel_z"] += 1.0
    df[["accel_x", "accel_y", "accel_z"]] *= scale
    if drop:
        df = df.drop(columns=drop)
    if extra_ts is not None:
        df.loc[5, "timestamp"] = extra_ts
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode()


def post(data: bytes):
    return client.post("/api/motion/analyze", files={"file": ("motion.csv", data, "text/csv")})


def test_valid_csv_reports_model_unavailable_not_a_fake_score():
    r = post(csv_bytes())
    assert r.status_code == 503
    body = r.json()
    assert body["error"] == "model_unavailable" and "score" not in body
    assert body["recording"]["sample_rate_hz"] == 100.0 and body["recording"]["assumptions"] == []


def test_milliseconds_and_m_s2_are_detected():
    r = post(csv_bytes(ms=True, scale=9.80665))
    a = r.json()["recording"]["assumptions"]
    assert r.status_code == 503 and len(a) == 2


def test_missing_columns():
    r = post(csv_bytes(drop=["gyro_z", "accel_x"]))
    assert r.status_code == 400 and r.json()["error"] == "missing_columns"
    assert "gyro_z" in r.json()["message"]


def test_too_short():
    r = post(csv_bytes(seconds=2))
    assert r.status_code == 400 and r.json()["error"] == "motion_too_short"


def test_low_sample_rate():
    r = post(csv_bytes(seconds=30, fs=5))
    assert r.status_code == 400 and r.json()["error"] == "sample_rate_too_low"


def test_out_of_order_timestamps():
    r = post(csv_bytes(extra_ts=0.0))
    assert r.status_code == 400 and r.json()["error"] == "invalid_timestamps"


def test_garbage_and_empty():
    assert post(b"").json()["error"] == "empty_file"
    assert post(b"\x00\x01\x02 not a csv \xff\xfe").status_code == 400
