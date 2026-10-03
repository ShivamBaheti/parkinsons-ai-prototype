import logging

from fastapi import APIRouter, UploadFile

from app.models.voice_model import load_voice_model
from app.utils.errors import api_error
from app.utils.validation import MAX_AUDIO_BYTES, ValidationError, validate_audio

router = APIRouter(tags=["voice"])
logger = logging.getLogger("parkinsons_api.voice")


@router.post("/voice/analyze")
async def analyze_voice(file: UploadFile):
    # Read one byte past the limit so oversized uploads are detected without loading everything.
    data = await file.read(MAX_AUDIO_BYTES + 1)
    try:
        _, _, info = validate_audio(data)
    except ValidationError as err:
        return api_error(err.status_code, err.code, err.message)

    if load_voice_model() is None:
        logger.warning("Voice analysis requested but no trained model is installed.")
        return api_error(
            503,
            "model_unavailable",
            "The recording is valid, but the voice model has not been trained yet, so no result can be produced.",
            recording={"duration_s": info.duration_s, "sample_rate": info.sample_rate},
        )

    # Feature extraction + prediction are added with the trained model.
    return api_error(501, "not_implemented", "Voice prediction is not implemented yet.")
