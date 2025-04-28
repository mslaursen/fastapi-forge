from typing import Any

from fastapi_forge.logger import logger
from fastapi_forge.schemas import ProjectSpec

from .protocols import TemplateProcessor


class DefaultTemplateProcessor(TemplateProcessor):
    def process(self, spec: ProjectSpec) -> dict[str, Any]:
        context = {
            **spec.model_dump(exclude={"models"}),
            "models": {"models": [model.model_dump() for model in spec.models]},
        }

        if spec.use_builtin_auth:
            auth_user = spec.get_auth_model()
            if auth_user:
                context["auth_model"] = auth_user.model_dump()
            else:
                logger.warning("No auth model found. Skipping authentication setup.")
                context["use_builtin_auth"] = False

        return context
