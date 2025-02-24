from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def _add_cors_middleware(app: FastAPI) -> None:
    """Add CORS Middleware."""
    app.add_middleware(CORSMiddleware, allow_origins=["*"])


def add_middleware(app: FastAPI) -> None:
    """Add all middlewares."""

    _add_cors_middleware(app)