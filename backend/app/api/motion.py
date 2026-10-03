import logging

from fastapi import APIRouter, UploadFile

from app.models.motion_model import load_motion_model
from app.utils.errors import api_error
from app.utils.validation import MAX_CSV_BYTES, ValidationError, validate_motion_csv

router = APIRouter(tags=["motion"])
logger = logging.getLogger("parkinsons_api.motion")


@router.post("/motion/analyze")
async def analyze_motion(file: UploadFile):
    data = await file.read(MAX_CSV_BYTES + 1)  # processed in memory, never stored
    try:
        _, info = validate_motion_csv(data)
    except ValidationError as err:
        return api_error(err.status_code, err.code, err.message)

    if load_motion_model() is None:
        logger.warning("Motion analysis requested but no trained model is installed.")
        return api_error(
            503,
            "model_unavailable",
            "The CSV is valid, but the motion model has not been trained yet, so no result can be produced.",
            recording={
                "n_samples": info.n_samples,
                "duration_s": info.duration_s,
                "sample_rate_hz": info.sample_rate_hz,
                "assumptions": info.assumptions,
            },
        )

    return api_error(501, "not_implemented", "Motion prediction is not implemented yet.")
