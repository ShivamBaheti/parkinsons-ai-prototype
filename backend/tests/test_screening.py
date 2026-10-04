import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.fusion_model import fuse

client = TestClient(app)


def test_fuse_is_equal_weight_mean_of_available_modalities():
    r = fuse({"voice": 0.72, "drawing": 0.61, "motion": 0.70})
    assert r.score == pytest.approx((0.72 + 0.61 + 0.70) / 3)
    assert r.modalities_missing == []
    assert sum(r.contributions.values()) == pytest.approx(r.score * 100, abs=0.2)


def test_fuse_skips_missing_modalities():
    r = fuse({"voice": None, "drawing": 0.4, "motion": 0.8})
    assert r.score == pytest.approx(0.6)
    assert r.modalities_used == ["drawing", "motion"]
    assert r.modalities_missing == ["voice"]
    assert r.interpretation == "elevated_screening_signal"


def test_fuse_below_threshold():
    assert fuse({"drawing": 0.3}).interpretation == "lower_screening_signal"


def test_fuse_rejects_empty_unknown_and_out_of_range():
    with pytest.raises(ValueError):
        fuse({})
    with pytest.raises(ValueError):
        fuse({"voice": None})
    with pytest.raises(ValueError):
        fuse({"eeg": 0.5})
    with pytest.raises(ValueError):
        fuse({"voice": 1.2})


def test_screening_endpoint_all_three_excludes_unreliable_voice():
    r = client.post("/api/screening/analyze", json={"voice": 0.72, "drawing": 0.61, "motion": 0.70})
    assert r.status_code == 200
    body = r.json()
    assert body["screening_score"] == 66  # mean of drawing and motion only
    assert body["modalities"] == {"voice": 0.72, "drawing": 0.61, "motion": 0.70}
    assert body["fusion"]["modalities_excluded"] == ["voice"]
    assert body["fusion"]["modalities_used"] == ["drawing", "motion"]
    assert body["fusion"]["validated"] is False
    assert "Not a Medical Diagnosis" in body["disclaimer"]


def test_screening_endpoint_partial():
    r = client.post("/api/screening/analyze", json={"drawing": 0.5})
    assert r.status_code == 200
    body = r.json()
    assert body["fusion"]["modalities_missing"] == ["voice", "motion"]
    assert body["modalities"]["voice"] is None


def test_screening_endpoint_voice_only_is_refused_with_a_clear_message():
    r = client.post("/api/screening/analyze", json={"voice": 0.9})
    assert r.status_code == 422 and r.json()["error"] == "no_reliable_modalities"


def test_screening_endpoint_rejects_no_scores():
    r = client.post("/api/screening/analyze", json={})
    assert r.status_code == 422 and r.json()["error"] == "no_modalities"


@pytest.mark.parametrize("payload", [{"voice": 1.5}, {"voice": -0.1}, {"voice": "high"}])
def test_screening_endpoint_rejects_bad_values(payload):
    r = client.post("/api/screening/analyze", json=payload)
    assert r.status_code == 422 and r.json()["error"] == "invalid_request"


def test_model_info_reports_only_installed_models():
    r = client.get("/api/model-info")
    assert r.status_code == 200
    body = r.json()
    assert set(body["modalities"]) == {"voice", "drawing", "motion"}
    assert body["modalities"]["drawing"]["available"] is True
    assert body["modalities"]["drawing"]["metadata"]["n_subjects"] == 40
    assert body["modalities"]["voice"]["available"] is True
    assert body["modalities"]["voice"]["metadata"]["reliable"] is False
    assert body["modalities"]["motion"]["available"] is False and body["modalities"]["motion"]["metadata"] is None
    assert body["fusion"]["validated"] is False
