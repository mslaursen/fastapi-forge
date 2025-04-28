from collections.abc import Callable

from pydantic import BaseModel, ValidationError

from fastapi_forge.enums import FieldDataTypeEnum
from fastapi_forge.frontend.notifications import (
    notify_enum_exists,
    notify_model_exists,
    notify_something_went_wrong,
    notify_validation_error,
)
from fastapi_forge.render import create_jinja_render_manager
from fastapi_forge.render.manager import RenderManager
from fastapi_forge.schemas import (
    CustomEnum,
    CustomEnumValue,
    Model,
    ModelField,
    ModelRelationship,
    ProjectSpec,
)
from fastapi_forge.type_info_registry import enum_registry


class ProjectState(BaseModel):
    """Central state management for the project configuration."""

    models: list[Model] = []
    selected_model: Model | None = None
    selected_field: ModelField | None = None
    selected_relation: ModelRelationship | None = None

    custom_enums: list[CustomEnum] = []
    selected_enum: CustomEnum | None = None
    selected_enum_value: CustomEnumValue | None = None
    select_enum_fn: Callable[[CustomEnum], None] | None = None
    deselect_enum_fn: Callable | None = None

    render_model_editor_fn: Callable | None = None
    render_actions_fn: Callable | None = None
    select_model_fn: Callable[[Model], None] | None = None
    deselect_model_fn: Callable | None = None

    render_content_fn: Callable | None = None
    display_item_editor_fn: Callable | None = None

    show_models: bool = True
    show_enums: bool = False

    project_name: str = ""
    use_postgres: bool = False
    use_alembic: bool = False
    use_builtin_auth: bool = False
    use_redis: bool = False
    use_rabbitmq: bool = False
    use_taskiq: bool = False
    use_prometheus: bool = False

    def get_render_manager(self) -> RenderManager:
        """Get the render manager for the current project."""
        return create_jinja_render_manager(project_name=self.project_name)

    def switch_item_editor(
        self,
        show_models: bool = False,
        show_enums: bool = False,
    ) -> None:
        if sum([show_models, show_enums]) != 1:
            msg = "One flag has to be True."
            raise ValueError(msg)

        self.show_models = show_models
        self.show_enums = show_enums

        if self.render_content_fn:
            self.render_content_fn.refresh()

        self._deselect_content()
        self.display_item_editor_fn.refresh()

    def initialize_from_project(self, project: ProjectSpec) -> None:
        """Initialize state from an existing project specification."""
        self.project_name = project.project_name
        self.use_postgres = project.use_postgres
        self.use_alembic = project.use_alembic
        self.use_builtin_auth = project.use_builtin_auth
        self.use_redis = project.use_redis
        self.use_rabbitmq = project.use_rabbitmq
        self.use_taskiq = project.use_taskiq
        self.use_prometheus = project.use_prometheus
        self.models = project.models.copy()
        self.custom_enums = project.custom_enums.copy()

        self._trigger_ui_refresh()

    def add_model(self, model_name: str) -> None:
        """Add a new model to the project."""
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
        self._deselect_content()
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
        if self.selected_model == model:
            return

        self.selected_model = model
        self.select_model_fn(model)  # type: ignore
        self._trigger_ui_refresh()

    def _enum_exists(self, name: str, exclude: CustomEnum | None = None) -> bool:
        return any(
            enum.name.lower() == name.lower()
            for enum in self.custom_enums
            if enum != exclude
        )

    def add_enum(self, enum_name: str) -> None:
        if self._enum_exists(enum_name):
            notify_enum_exists(enum_name)
            return

        try:
            self.custom_enums.append(CustomEnum(name=enum_name))
            self._trigger_ui_refresh()
        except ValidationError as exc:
            notify_validation_error(exc)

    def select_enum(self, enum: CustomEnum) -> None:
        if self.selected_enum == enum:
            return

        self.selected_enum = enum
        self.select_enum_fn(enum)  # type: ignore
        self._trigger_ui_refresh()

    def delete_enum(self, enum: CustomEnum) -> None:
        """Remove an enum from the project."""
        self.custom_enums.remove(enum)
        enum_registry.remove(enum.name)
        self._deselect_content()
        self._trigger_ui_refresh()

    def update_enum_name(self, enum: CustomEnum, new_name: str) -> None:
        """Rename an existing enum."""
        if enum.name == new_name:
            return

        if self._enum_exists(new_name, exclude=enum):
            notify_enum_exists(new_name)
            return

        enum_registry.update_key(enum.name, new_name)
        enum.name = new_name

        if enum == self.selected_enum and self.select_enum_fn:
            self.select_enum_fn(enum)

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
            use_taskiq=self.use_taskiq,
            use_prometheus=self.use_prometheus,
            models=self.models,
            custom_enums=self.custom_enums,
        )

    def _create_default_model(self, name: str) -> Model:
        """Create a new model with default fields."""
        return Model(
            name=name,
            fields=[
                ModelField(
                    name="id",
                    type=FieldDataTypeEnum.UUID,
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

    def _validate_model_operation(self, model: Model) -> bool:
        """Validate conditions for model operations."""
        if model not in self.models or not all(
            [self.deselect_model_fn, self.render_content_fn]
        ):
            notify_something_went_wrong()
            return False
        return True

    def _deselect_content(self) -> None:
        if self.deselect_model_fn:
            self.deselect_model_fn()
        if self.deselect_enum_fn:
            self.deselect_enum_fn()

        self.selected_model = None
        self.selected_enum = None

    def _trigger_ui_refresh(self) -> None:
        """Refresh all relevant UI components."""
        if self.render_content_fn:
            self.render_content_fn.refresh()
        if self.render_model_editor_fn:
            self.render_model_editor_fn()
        if self.render_actions_fn:
            self.render_actions_fn.refresh()

    def get_auth_model(self) -> Model | None:
        return next(
            (model for model in self.models if model.metadata.is_auth_model),
            None,
        )

    def get_enum_by_name(self, name: str) -> CustomEnum | None:
        return next(
            (enum for enum in self.custom_enums if enum.name == name),
            None,
        )


state: ProjectState = ProjectState()
