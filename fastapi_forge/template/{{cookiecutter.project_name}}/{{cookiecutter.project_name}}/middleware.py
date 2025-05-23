from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from {{cookiecutter.project_name}}.settings import settings
{% if cookiecutter.use_prometheus %}
from prometheus_fastapi_instrumentator import Instrumentator
{% endif %}
{% if cookiecutter.use_logfire %}
import logfire
from loguru import logger
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
{% if cookiecutter.use_logfire %}
def _add_logfire_middleware(app: FastAPI) -> None:
    """Add Logfire Middleware."""
    if settings.logfire.enabled:
        logfire.configure(
            token=settings.logfire.write_token.get_secret_value(),
            environment=settings.env,
            send_to_logfire="if-token-present",
            service_name="{{ cookiecutter.project_name }}"
        )
        logfire.instrument_fastapi(app, capture_headers=True)
        logfire.instrument_asyncpg()
        logfire.instrument_system_metrics()
        logger.configure(handlers=[logfire.loguru_handler()])
{% endif %}
def add_middleware(app: FastAPI) -> None:
    """Add all middlewares."""
    _add_cors_middleware(app)
    {%- if cookiecutter.use_prometheus %}
    _add_prometheus_middleware(app)
    {%- endif %}
    {%- if cookiecutter.use_logfire %}
    _add_logfire_middleware(app)
    {% endif %}