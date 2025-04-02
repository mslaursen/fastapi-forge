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
from fastapi_forge.frontend.notifications import (
    notify_model_exists,
    notify_something_went_wrong,
    notify_validation_error,
)


class ProjectState(BaseModel):
    """Central state management for the project configuration."""

    models: list[Model] = []
    selected_model: Model | None = None
    selected_field: ModelField | None = None
    selected_relation: ModelRelationship | None = None

    render_models_fn: Callable | None = None
    render_model_editor_fn: Callable | None = None
    select_model_fn: Callable[[Model], None] | None = None
    deselect_model_fn: Callable | None = None

    project_name: str = ""
    use_postgres: bool = False
    use_alembic: bool = False
    use_builtin_auth: bool = False
    use_redis: bool = False
    use_rabbitmq: bool = False

    def initialize_from_project(self, project: ProjectSpec) -> None:
        """Initialize state from an existing project specification."""
        self.project_name = project.project_name
        self.use_postgres = project.use_postgres
        self.use_alembic = project.use_alembic
        self.use_builtin_auth = project.use_builtin_auth
        self.use_redis = project.use_redis
        self.use_rabbitmq = project.use_rabbitmq
        self.models = project.models.copy()

        self._trigger_ui_refresh()

    def add_model(self, model_name: str) -> None:
        """Add a new model to the project."""
        if not self._validate_ui_callbacks():
            return

        if self._model_exists(model_name):
            notify_model_exists(model_name)
            return

        try:
            self.models.append(self._create_default_model(model_name))
            self._trigger_ui_refresh()
        except ValidationError as exc:
            notify_validation_error(exc)

    def delete_model(self, model: Model) -> None:
        """Remove a model from the project."""
        if not self._validate_model_operation(model):
            return

        self.models.remove(model)
        self._cleanup_relationships_for_deleted_model(model.name)
        self._deselect_current_model()
        self._trigger_ui_refresh()

    def update_model_name(self, model: Model, new_name: str) -> None:
        """Rename an existing model."""
        if model.name == new_name:
            return

        if self._model_exists(new_name, exclude=model):
            notify_model_exists(new_name)
            return

        old_name = model.name
        model.name = new_name
        self._update_relationships_for_rename(old_name, new_name)

        if model == self.selected_model and self.select_model_fn:
            self.select_model_fn(model)

        self._trigger_ui_refresh()

    def select_model(self, model: Model) -> None:
        """Set the currently selected model."""
        if self.selected_model == model or not self._validate_ui_callbacks():
            return

        self.selected_model = model
        self.select_model_fn(model)  # type: ignore
        self._trigger_ui_refresh()

    def get_project_spec(self) -> ProjectSpec:
        """Generate a ProjectSpec from the current state."""
        return ProjectSpec(
            project_name=self.project_name,
            use_postgres=self.use_postgres,
            use_alembic=self.use_alembic,
            use_builtin_auth=self.use_builtin_auth,
            use_redis=self.use_redis,
            use_rabbitmq=self.use_rabbitmq,
            models=self.models,
        )

    def _create_default_model(self, name: str) -> Model:
        """Create a new model with default fields."""
        return Model(
            name=name,
            fields=[
                ModelField(
                    name="id",
                    type=FieldDataType.UUID,
                    primary_key=True,
                    nullable=False,
                    unique=True,
                    index=True,
                )
            ],
        )

    def _cleanup_relationships_for_deleted_model(self, deleted_model_name: str) -> None:
        """Remove relationships pointing to deleted models."""
        for model in self.models:
            model.relationships = [
                rel
                for rel in model.relationships
                if rel.target_model != deleted_model_name
            ]

    def _update_relationships_for_rename(self, old_name: str, new_name: str) -> None:
        """Update relationships when a model is renamed."""
        for model in self.models:
            for relationship in model.relationships:
                if relationship.target_model == old_name:
                    relationship.target_model = new_name

    def _model_exists(self, name: str, exclude: Model | None = None) -> bool:
        """Check if a model with the given name already exists."""
        return any(model.name == name for model in self.models if model != exclude)

    def _validate_ui_callbacks(self) -> bool:
        """Verify required UI callbacks are set."""
        if not all([self.render_models_fn, self.select_model_fn]):
            notify_something_went_wrong()
            return False
        return True

    def _validate_model_operation(self, model: Model) -> bool:
        """Validate conditions for model operations."""
        if model not in self.models or not all(
            [self.deselect_model_fn, self.render_models_fn]
        ):
            ui.notify("Something went wrong...", type="warning")
            return False
        return True

    def _deselect_current_model(self) -> None:
        """Clear current model selection."""
        if self.deselect_model_fn:
            self.deselect_model_fn()
        self.selected_model = None

    def _trigger_ui_refresh(self) -> None:
        """Refresh all relevant UI components."""
        if self.render_models_fn:
            self.render_models_fn()
        if self.render_model_editor_fn:
            self.render_model_editor_fn()


state: ProjectState = ProjectState()
