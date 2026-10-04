"""Multimodal fusion: combine per-modality screening probabilities into one score.

This is a PROTOTYPE fusion, not a trained model. The voice, drawing and motion
datasets come from different people, so there is no paired data on which a
fusion model (weights, meta-model, stacking) could be trained or validated.
The only defensible rule is therefore the plain, equal-weight mean of whichever
modality probabilities are available. The weights are a design choice, not a
medically validated quantity.
"""
from dataclasses import dataclass

MODALITIES = ("voice", "drawing", "motion")
METHOD = "equal_weight_mean"
# Modalities whose model is known to be unreliable. They are shown to the user but left out of the
# combined score. Remove a name here only after the model has passed an external check.
EXCLUDED_FROM_SCORE = frozenset({"voice"})
# 0.5 is the default decision threshold of the individual models, not a clinically validated cut-off.
THRESHOLD = 0.5


@dataclass(frozen=True)
class FusionResult:
    score: float  # 0..1 mean of the available modality probabilities
    modalities_used: list[str]
    modalities_missing: list[str]
    contributions: dict[str, float]  # each used modality's share of the overall score, in points (sums to score*100)
    interpretation: str


def fuse(scores: dict[str, float | None]) -> FusionResult:
    """Fuse modality probabilities. Missing modalities (None) are left out of the mean."""
    unknown = set(scores) - set(MODALITIES)
    if unknown:
        raise ValueError(f"Unknown modalities: {sorted(unknown)}")
    used = {m: s for m, s in scores.items() if s is not None}
    if not used:
        raise ValueError("At least one modality score is required.")
    for m, s in used.items():
        if not 0.0 <= s <= 1.0:
            raise ValueError(f"Score for {m} must be between 0 and 1.")

    n = len(used)
    mean = sum(used.values()) / n
    ordered = [m for m in MODALITIES if m in used]
    return FusionResult(
        score=mean,
        modalities_used=ordered,
        modalities_missing=[m for m in MODALITIES if m not in used],
        contributions={m: round(used[m] / n * 100, 1) for m in ordered},
        interpretation="elevated_screening_signal" if mean >= THRESHOLD else "lower_screening_signal",
    )
