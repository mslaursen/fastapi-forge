from src.routes.health_routes import router as health_router
{% if cookiecutter.create_routes %}
{% for model in cookiecutter.models.models -%}
from src.routes.{{ model.name | camel_to_snake }}_routes import router as {{ model.name | camel_to_snake }}_router
{% endfor %}
{% endif %}
{% if cookiecutter.use_builtin_auth %}
from src.routes.auth_routes import router as auth_router
{% endif %}

from fastapi import APIRouter


base_router = APIRouter(prefix="/api/v1")

base_router.include_router(health_router, tags=["health"])
{% if cookiecutter.create_routes %}
{% for model in cookiecutter.models.models -%}
base_router.include_router({{ model.name | camel_to_snake }}_router, tags=["{{ model.name | camel_to_snake }}"])
{% endfor %}
{% endif %}
{% if cookiecutter.use_builtin_auth %}
base_router.include_router(auth_router, tags=["auth"])
{% endif %}
