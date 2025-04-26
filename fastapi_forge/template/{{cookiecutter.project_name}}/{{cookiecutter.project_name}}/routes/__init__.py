from {{cookiecutter.project_name}}.routes.health_routes import router as health_router
from {{cookiecutter.project_name}}.routes.demo_routes import router as demo_router
{% for model in cookiecutter.models.models if model.metadata.create_endpoints -%}
from {{cookiecutter.project_name}}.routes.{{ model.name }}_routes import router as {{ model.name }}_router
{% endfor %}
{% if cookiecutter.use_builtin_auth %}
from {{cookiecutter.project_name}}.routes.auth_routes import router as auth_router
{% endif %}

from fastapi import APIRouter


base_router = APIRouter(prefix="/api/v1")

base_router.include_router(health_router, tags=["health"])
base_router.include_router(demo_router, tags=["demo"])
{% for model in cookiecutter.models.models if model.metadata.create_endpoints -%}
base_router.include_router({{ model.name }}_router, tags=["{{ model.name }}"])
{% endfor %}
{% if cookiecutter.use_builtin_auth %}
base_router.include_router(auth_router, tags=["auth"])
{% endif %}
