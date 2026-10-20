import math

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def spiral(n=200, seconds=4.0, size=600, radius=250):
    pts = []
    for i in range(n):
        theta = 6 * math.pi * i / (n - 1)
        r = radius * theta / (6 * math.pi)
        pts.append({"x": size / 2 + r * math.cos(theta), "y": size / 2 + r * math.sin(theta),
                    "t": seconds * 1000 * i / (n - 1), "stroke": 0})
    return pts


def post(points, size=600):
    return client.post("/api/drawing/analyze", json={"points": points, "canvas_size": size})


def test_valid_drawing_reports_model_unavailable_not_a_fake_score(monkeypatch):
    monkeypatch.setattr("app.api.drawing.load_drawing_model", lambda: None)
    r = post(spiral())
    assert r.status_code == 503
    body = r.json()
    assert body["error"] == "model_unavailable" and "score" not in body
    assert body["drawing"]["n_points"] == 200


def test_empty():
    r = post([])
    assert r.status_code == 400 and r.json()["error"] == "empty_drawing"


def test_too_few_points():
    r = post(spiral(n=10))
    assert r.status_code == 400 and r.json()["error"] == "drawing_too_short"


def test_too_fast():
    r = post(spiral(seconds=0.5))
    assert r.status_code == 400 and r.json()["error"] == "drawing_too_fast"


def test_out_of_order_timestamps():
    pts = spiral()
    pts[100]["t"] = 0
    r = post(pts)
    assert r.status_code == 400 and r.json()["error"] == "invalid_timestamps"


def test_too_small():
    r = post(spiral(radius=20))
    assert r.status_code == 400 and r.json()["error"] == "drawing_too_small"


def test_malformed_body_uses_consistent_error_shape():
    r = client.post("/api/drawing/analyze", json={"points": "nope"})
    assert r.status_code == 422 and r.json()["error"] == "invalid_request"


def test_valid_drawing_gets_a_real_model_score():
    r = post(spiral(n=400, seconds=12.0))
    assert r.status_code == 200
    body = r.json()
    assert body["modality"] == "drawing" and 0.0 <= body["score"] <= 1.0
    assert body["label"] in {"elevated_screening_signal", "lower_screening_signal"}
    assert body["validated_for_this_input"] is False
    assert set(body["features"]) >= {"speed_cv", "radial_residual_rms"}
    assert len(body["top_model_features"]) == 3
    # contributions are an exact breakdown of the score (in points, 0-100)
    assert abs(body["baseline"] + sum(body["contributions"].values()) - body["score"] * 100) < 1.0


def test_score_is_deterministic_and_scales_with_canvas_size():
    a = post(spiral(n=400, seconds=12.0)).json()["score"]
    b = post(spiral(n=400, seconds=12.0)).json()["score"]
    c = post(spiral(n=400, seconds=12.0, size=300, radius=125), size=300).json()["score"]
    assert a == b == c
