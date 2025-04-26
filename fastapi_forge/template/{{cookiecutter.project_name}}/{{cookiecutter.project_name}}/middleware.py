from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from {{cookiecutter.project_name}}.settings import settings
{% if cookiecutter.use_prometheus %}
from prometheus_fastapi_instrumentator import Instrumentator
{% endif %}

def _add_cors_middleware(app: FastAPI) -> None:
    """Add CORS Middleware."""
    app.add_middleware(CORSMiddleware, allow_origins=["*"])
{% if cookiecutter.use_prometheus %}
def _add_prometheus_middleware(app: FastAPI) -> None:
    """Add Prometheus Middleware."""
    if settings.prometheus.enabled:
        instrumenter = Instrumentator().instrument(app)
        instrumenter.expose(app)
{% endif %}
def add_middleware(app: FastAPI) -> None:
    """Add all middlewares."""
    _add_cors_middleware(app)
    {%- if cookiecutter.use_prometheus %}
    _add_prometheus_middleware(app)
    {% endif %}