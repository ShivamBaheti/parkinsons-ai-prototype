import logging

from fastapi import APIRouter, UploadFile

from app.models.voice_model import THRESHOLD, load_voice_metadata, load_voice_model, predict_voice
from app.utils.errors import api_error
from app.utils.validation import MAX_AUDIO_BYTES, ValidationError, validate_audio

router = APIRouter(tags=["voice"])
logger = logging.getLogger("parkinsons_api.voice")


@router.post("/voice/analyze")
async def analyze_voice(file: UploadFile):
    # Read one byte past the limit so oversized uploads are detected without loading everything.
    data = await file.read(MAX_AUDIO_BYTES + 1)
    try:
        signal, sample_rate, info = validate_audio(data)
    except ValidationError as err:
        return api_error(err.status_code, err.code, err.message)

    model = load_voice_model()
    if model is None:
        logger.warning("Voice analysis requested but no trained model is installed.")
        return api_error(
            503,
            "model_unavailable",
            "The recording is valid, but the voice model has not been trained yet, so no result can be produced.",
            recording={"duration_s": info.duration_s, "sample_rate": info.sample_rate},
        )

    meta = load_voice_metadata() or {}
    try:
        score, feats = predict_voice(model, signal, sample_rate, meta.get("features"))
    except ValueError as err:
        logger.info("Voice not analysable: %s", err)
        return api_error(
            422,
            "voice_not_analysable",
            "No steady voiced sound could be found. Please record a clear, steady 'ahhh' for at least 3 seconds in a quiet room.",
        )

    importance = meta.get("feature_importance", [])
    return {
        "modality": "voice",
        "score": round(score, 3),
        "label": "elevated_screening_signal" if score >= THRESHOLD else "lower_screening_signal",
        "reliable": bool(meta.get("reliable", False)),
        "validated_for_this_input": False,
        "features": {k: round(v, 5) for k, v in feats.items()},
        "top_model_features": [d["feature"] for d in importance[:3]],  # global importance, not an explanation of this recording
        "note": (
            "Demonstration only. This voice model is probably separating recording setups rather than disease "
            "(see About), so it is shown but not included in the combined score."
        ),
    }
