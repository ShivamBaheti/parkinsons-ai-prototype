import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.fusion_model import EXCLUDED_FROM_SCORE, METHOD, THRESHOLD, fuse
from app.utils.errors import api_error

router = APIRouter(tags=["screening"])
logger = logging.getLogger("parkinsons_api.screening")

DISCLAIMER = (
    "Research Prototype — Not a Medical Diagnosis. This application is an experimental AI-based "
    "screening system intended for academic research and demonstration. Its outputs should not be "
    "interpreted as a diagnosis of Parkinson's Disease or used to make medical decisions. Consult a "
    "qualified healthcare professional for clinical evaluation."
)


class ScreeningRequest(BaseModel):
    """Modality probabilities returned by the individual /analyze endpoints. Omit a modality that was not tested."""

    voice: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    drawing: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    motion: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)


@router.post("/screening/analyze")
def analyze_screening(req: ScreeningRequest):
    scores = req.model_dump()
    if all(v is None for v in scores.values()):
        return api_error(422, "no_modalities", "Complete at least one test (voice, drawing or motion) first.")

    scored = {m: (None if m in EXCLUDED_FROM_SCORE else v) for m, v in scores.items()}
    excluded = sorted(m for m in EXCLUDED_FROM_SCORE if scores.get(m) is not None)
    if all(v is None for v in scored.values()):
        return api_error(
            422,
            "no_reliable_modalities",
            "The voice result is a demonstration only and is not included in the combined score. Complete the drawing or motion test to get a combined score.",
        )

    result = fuse(scored)
    logger.info("Fused %d modality score(s)", len(result.modalities_used))
    return {
        "screening_score": round(result.score * 100),
        "modalities": {m: scores[m] for m in ("voice", "drawing", "motion")},
        "interpretation": result.interpretation,
        "fusion": {
            "method": METHOD,
            "validated": False,
            "threshold": THRESHOLD,
            "modalities_used": result.modalities_used,
            "modalities_missing": [m for m in result.modalities_missing if m not in excluded],
            "modalities_excluded": excluded,
            "contributions": result.contributions,
            "note": (
                "Prototype fusion: an equal-weight mean of the available modality probabilities. The datasets "
                "behind each model contain different people, so no paired data exists to train or validate "
                "a fusion model, and the equal weights are not medically validated."
            ),
        },
        "disclaimer": DISCLAIMER,
    }
