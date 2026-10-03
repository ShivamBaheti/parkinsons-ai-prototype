"""One consistent JSON error shape for every endpoint: {"error": code, "message": text}."""
from fastapi.responses import JSONResponse


def api_error(status_code: int, code: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": code, "message": message, **extra},
    )
