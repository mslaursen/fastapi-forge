from collections.abc import Callable

from nicegui import ui
from pydantic import BaseModel, ValidationError

from fastapi_forge.dtos import (
    Model,
    ModelField,
    ModelRelationship,
    ProjectSpec,
)
from fastapi_forge.enums import FieldDataType
from fastapi_forge.frontend import notifications as n


class ProjectState(BaseModel):
    models: list[Model] = []
    selected_model: Model | None = None
    selected_field: ModelField | None = None
    selected_relation: ModelRelationship | None = None

    render_models_fn: Callable | None = None
    select_model_fn: Callable | None = None

    project_name: str = ""
    use_postgres: bool = False
    use_alembic: bool = False
    use_builtin_auth: bool = False
    use_redis: bool = False
    use_rabbitmq: bool = False

    def initialize_from_project(self, project: ProjectSpec) -> None:
        """Initialize the state from an existing project specification"""
        self.project_name = project.project_name
        self.use_postgres = project.use_postgres
        self.use_alembic = project.use_alembic
        self.use_builtin_auth = project.use_builtin_auth
        self.use_redis = project.use_redis
        self.use_rabbitmq = project.use_rabbitmq
        self.models = project.models.copy()

        if self.render_models_fn:
            self.render_models_fn()

    def add_model(self, model_name: str) -> None:
        if self.render_models_fn is None:
            n.notify_something_went_wrong()
            return

        if any(model.name == model_name for model in self.models):
            n.notify_model_exists(model_name)
            return

        try:
            default_id_field = ModelField(
                name="id",
                type=FieldDataType.UUID,
                primary_key=True,
                nullable=False,
                unique=True,
                index=True,
            )

            new_model = Model(name=model_name, fields=[default_id_field])
            self.models.append(new_model)

            self.render_models_fn()

        except ValidationError as exc:
            n.notify_validation_error(exc)

    def delete_model(self, model: Model) -> None:
        if model not in self.models:
            ui.notify("Something went wrong...", type="warning")
            return
        self.models.remove(model)
        if self.selected_model == model:
            self.selected_model = None
        if self.render_models_fn:
            self.render_models_fn()

    def update_model_name(self, model: Model, new_name: str) -> None:
        if any(m.name == new_name for m in self.models if m != model):
            n.notify_model_exists(new_name)
            return

        old_name = model.name
        model.name = new_name
        self._update_relationships_for_rename(old_name, new_name)

        if self.render_models_fn:
            self.render_models_fn()

    def select_model(self, model: Model) -> None:
        if self.select_model_fn is None:
            n.notify_something_went_wrong()
            return
        self.selected_model = model
        self.select_model_fn(model)

    def get_project_spec(self) -> ProjectSpec:
        return ProjectSpec(
            project_name=self.project_name,
            use_postgres=self.use_postgres,
            use_alembic=self.use_alembic,
            use_builtin_auth=self.use_builtin_auth,
            use_redis=self.use_redis,
            use_rabbitmq=self.use_rabbitmq,
            models=self.models,
        )

    def _cleanup_relationships_for_deleted_model(
        self,
        deleted_model_name: str,
    ) -> None:
        for model in self.models:
            model.relationships = [
                rel
                for rel in model.relationships
                if rel.target_model != deleted_model_name
            ]

    def _update_relationships_for_rename(
        self,
        old_name: str,
        new_name: str,
    ) -> None:
        for model in self.models:
            for relationship in model.relationships:
                if relationship.target_model == old_name:
                    relationship.target_model = new_name


state: ProjectState = ProjectState()
