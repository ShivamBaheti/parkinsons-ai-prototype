"""Application configuration, read from environment variables."""
import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


def _split(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Parkinson's AI Screening API"
    version: str = "0.1.0"
    model_dir: Path = BASE_DIR / "models"
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    # Voice is excluded from the combined score by default because its model is unreliable
    # (see README). Set INCLUDE_VOICE_IN_SCORE=true to count it anyway.
    include_voice_in_score: bool = field(
        default_factory=lambda: os.getenv("INCLUDE_VOICE_IN_SCORE", "false").strip().lower() in {"1", "true", "yes"}
    )
    cors_origins: list[str] = field(
        default_factory=lambda: _split(
            os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        )
    )


settings = Settings()
