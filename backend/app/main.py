import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import drawing, health, motion, voice
from app.config import settings

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("parkinsons_api")

app = FastAPI(title=settings.app_name, version=settings.version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Log the full error server-side; never expose a stack trace to the client."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "Something went wrong on the server."},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "invalid_request", "message": "The request was missing data or had an invalid format."},
    )


app.include_router(health.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(drawing.router, prefix="/api")
app.include_router(motion.router, prefix="/api")
