from src.routes.health_routes import router as health_router
{% if cookiecutter.create_routes %}
{% for model in cookiecutter.models.models -%}
from src.routes.{{ model.name.lower() }}_routes import router as {{ model.name.lower() }}_router
{% endfor %}
{% endif %}

from fastapi import APIRouter


base_router = APIRouter(prefix="/api/v1")

base_router.include_router(health_router, tags=["health"])
{% if cookiecutter.create_routes %}
{% for model in cookiecutter.models.models -%}
base_router.include_router({{ model.name.lower() }}_router, tags=["{{ model.name.lower() }}"])
{% endfor %}
{% endif %}
