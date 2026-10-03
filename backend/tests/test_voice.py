import io

import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def wav_bytes(seconds=2.0, amplitude=0.5, sr=16000, freq=220.0) -> bytes:
    t = np.arange(int(seconds * sr)) / sr
    buf = io.BytesIO()
    sf.write(buf, (amplitude * np.sin(2 * np.pi * freq * t)).astype("float32"), sr, format="WAV")
    return buf.getvalue()


def post(data: bytes):
    return client.post("/api/voice/analyze", files={"file": ("rec.wav", data, "audio/wav")})


def test_valid_audio_reports_model_unavailable_not_a_fake_score():
    r = post(wav_bytes())
    assert r.status_code == 503
    body = r.json()
    assert body["error"] == "model_unavailable"
    assert "score" not in body
    assert body["recording"]["sample_rate"] == 16000


def test_too_short():
    r = post(wav_bytes(seconds=0.5))
    assert r.status_code == 400 and r.json()["error"] == "audio_too_short"


def test_silence():
    r = post(wav_bytes(amplitude=0.0))
    assert r.status_code == 400 and r.json()["error"] == "no_sound_detected"


def test_corrupted_file():
    r = post(b"this is not audio")
    assert r.status_code == 400 and r.json()["error"] == "invalid_audio"


def test_empty_file():
    r = post(b"")
    assert r.status_code == 400 and r.json()["error"] == "empty_file"


def test_too_large():
    r = post(b"\0" * (10 * 1024 * 1024 + 2))
    assert r.status_code == 413 and r.json()["error"] == "file_too_large"


def test_missing_file_field():
    r = client.post("/api/voice/analyze")
    assert r.status_code == 422
