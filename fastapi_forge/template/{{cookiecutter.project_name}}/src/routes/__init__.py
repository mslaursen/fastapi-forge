from src.routes.health_routes import router as health_router
{% if cookiecutter.create_routes %}
{% for model_name in cookiecutter.models.names -%}
from src.routes.{{ model_name.lower() }}_routes import router as {{ model_name.lower() }}_router
{% endfor %}
{% endif %}

from fastapi import APIRouter


base_router = APIRouter(prefix="/api/v1")

base_router.include_router(health_router, tags=["health"])
{% if cookiecutter.create_routes %}
{% for model_name in cookiecutter.models.names -%}
base_router.include_router({{ model_name.lower() }}_router, tags=["{{ model_name.lower() }}"])
{% endfor %}
{% endif %}
