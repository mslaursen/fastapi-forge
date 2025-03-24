import asyncio
from nicegui import ui, native
from typing import Callable, Any
from pydantic import ValidationError
from fastapi_forge.enums import FieldDataType
from fastapi_forge.dtos import (
    Model,
    ModelField,
    ModelRelationship,
    ProjectSpec,
    FieldInput,
    ModelInput,
    ProjectInput,
)
from fastapi_forge.forge import build_project
from fastapi_forge.project_io import ProjectLoader, ProjectExporter
from pathlib import Path
import yaml
import os

COLUMNS: list[dict[str, Any]] = [
    {
        "name": "name",
        "label": "Name",
        "field": "name",
        "required": True,
        "align": "left",
    },
    {"name": "type", "label": "Type", "field": "type", "align": "left"},
    {
        "name": "primary_key",
        "label": "Primary Key",
        "field": "primary_key",
        "align": "center",
    },
    {
        "name": "foreign_key",
        "label": "Foreign Key",
        "field": "foreign_key",
        "align": "left",
    },
    {"name": "nullable", "label": "Nullable", "field": "nullable", "align": "center"},
    {"name": "unique", "label": "Unique", "field": "unique", "align": "center"},
    {"name": "index", "label": "Index", "field": "index", "align": "center"},
]


def notify_validation_error(e: ValidationError) -> None:
    msg = e.errors()[0].get("msg", "Something went wrong.")
    ui.notify(msg, type="negative")


def generate_model_instances(models: list[ModelInput]) -> list[Model]:
    try:
        model_objects = []

        for model in models:
            name = model.name
            fields, relationships = [], []

            for field in model.fields:
                mr = None
                if field.foreign_key:
                    mr = ModelRelationship(
                        field_name=field.name,
                        back_populates=field.back_populates,
                    )
                    relationships.append(mr)

                fields.append(
                    ModelField(
                        name=field.name,
                        type=field.type,
                        primary_key=field.primary_key,
                        nullable=field.nullable,
                        unique=field.unique,
                        index=field.index,
                        foreign_key=mr.target_id if mr else None,
                        is_created_at_timestamp=field.is_created_at_timestamp,
                        is_updated_at_timestamp=field.is_updated_at_timestamp,
                    )
                )

            model_objects.append(
                Model(
                    name=name,
                    fields=fields,
                    relationships=relationships,
                    metadata=model.metadata,
                )
            )

    except Exception as e:
        raise e

    return model_objects


class Header(ui.header):
    def __init__(self):
        super().__init__()
        self.dark_mode = ui.dark_mode(value=True)
        self._build()

    def _build(self) -> None:
        with self:
            ui.button(
                icon="eva-github",
                color="white",
                on_click=lambda: ui.navigate.to(
                    "https://github.com/mslaursen/fastapi-forge"
                ),
            ).classes("self-center", remove="bg-white").tooltip(
                "Drop a ⭐️ if you like FastAPI Forge!"
            )

            ui.label(text="FastAPI Forge").classes(
                "font-bold ml-auto self-center text-2xl"
            )

            ui.button(
                icon="dark_mode",
                color="white",
                on_click=lambda: self.dark_mode.toggle(),
            ).classes("ml-auto", remove="bg-white")


class ModelCreate(ui.row):
    def __init__(self, on_add_model: Callable[[str], None]):
        super().__init__(wrap=False)
        self.on_add_model = on_add_model
        self._build()

    def _build(self) -> None:
        with self.classes("w-full flex items-center justify-between"):
            self.model_input = (
                ui.input(placeholder="Model name")
                .classes("self-center")
                .tooltip(
                    "Model names should be singular (e.g., 'user' instead of 'users')."
                )
            )
            self.add_button = (
                ui.button(icon="add", on_click=self._add_model)
                .classes("self-center")
                .tooltip("Add Model")
            )

    def _add_model(self) -> None:
        model_name = self.model_input.value.strip()
        if model_name:
            self.on_add_model(model_name)
            self.model_input.value = ""


class ModelRow(ui.row):
    def __init__(
        self,
        model: ModelInput,
        on_delete: Callable[[ModelInput], None],
        on_edit: Callable[[ModelInput, str], None],
        on_select: Callable[[ModelInput], None],
        color: str | None = None,
    ):
        super().__init__(wrap=False)
        self.model = model
        self.on_delete = on_delete
        self.on_edit = on_edit
        self.on_select = on_select
        self.is_editing = False
        self.color = color
        self._build()

    def _build(self) -> None:
        with self.classes("w-full flex items-center justify-between cursor-pointer"):
            self.name_label = ui.label(text=self.model.name).classes("self-center")
            if self.color:
                self.name_label.classes(add=self.color)
            self.name_input = (
                ui.input(value=self.model.name)
                .classes("self-center")
                .bind_visibility_from(self, "is_editing")
            )
            self.name_label.bind_visibility_from(self, "is_editing", lambda x: not x)

            self.on("click", lambda: self.on_select(self.model))

            with ui.row().classes("gap-2"):
                self.edit_button = ui.button(
                    icon="edit", on_click=self._toggle_edit
                ).bind_visibility_from(self, "is_editing", lambda x: not x)
                self.save_button = ui.button(
                    icon="save", on_click=self._save_model
                ).bind_visibility_from(self, "is_editing")
                ui.button(icon="delete", on_click=self._delete_model)

    def _toggle_edit(self) -> None:
        self.is_editing = not self.is_editing

    def _save_model(self) -> None:
        new_name = self.name_input.value.strip()
        if new_name:
            self.on_edit(self.model, new_name)
            self.is_editing = False

    def _delete_model(self) -> None:
        self.on_delete(self.model)


class ModelPanel(ui.left_drawer):
    def __init__(
        self,
        on_select_model: Callable[[ModelInput | None], None],
        project_config_panel: "ProjectConfigPanel | None" = None,
        initial_models: list[ModelInput] | None = None,
    ):
        super().__init__(value=True, elevated=False, bottom_corner=True)
        self.classes("border-right[1px]")
        self.models = initial_models or []
        self.selected_model: ModelInput | None = None
        self.on_select_model = on_select_model
        self.project_config_panel = project_config_panel
        self._build()

    def _build(self) -> None:
        self.clear()
        with self:
            with ui.column().classes("items-align content-start w-full") as self.column:
                self.model_create = ModelCreate(on_add_model=self._add_model)
                self._render_model_list()

                ui.button(
                    "Export",
                    on_click=self._export_project,
                    icon="file_download",
                ).classes("w-full py-3 text-lg font-bold").tooltip(
                    "Generates a YAML file containing the project configuration."
                )

    async def _export_project(self) -> None:
        """Export the project configuration to a YAML file."""
        if self.project_config_panel is None:
            ui.notify(
                "Project configuration panel is not initialized.", type="negative"
            )
            return

        try:
            project_input = ProjectInput(
                project_name=self.project_config_panel.project_name.value,
                use_postgres=self.project_config_panel.use_postgres.value,
                use_alembic=self.project_config_panel.use_alembic.value,
                use_builtin_auth=self.project_config_panel.use_builtin_auth.value,
                use_redis=self.project_config_panel.use_redis.value,
                use_rabbitmq=self.project_config_panel.use_rabbitmq.value,
                models=self.models,
            )

            exporter = ProjectExporter(project_input)
            await exporter.export_project()

            ui.notify(
                "Project configuration exported to "
                f"{os.path.join(os.getcwd(), project_input.project_name)}.yaml",
                type="positive",
            )

        except ValidationError as e:
            notify_validation_error(e)
        except FileNotFoundError as e:
            ui.notify(f"File not found: {e}", type="negative")
        except yaml.YAMLError as e:
            ui.notify(f"Error writing YAML file: {e}", type="negative")
        except IOError as e:
            ui.notify(f"Error writing file: {e}", type="negative")
        except Exception as e:
            ui.notify(f"An unexpected error occurred: {e}", type="negative")

    def _add_model(self, model_name: str) -> None:
        if any(model.name == model_name for model in self.models):
            ui.notify(f"Model '{model_name}' already exists.", type="negative")
            return

        if model_name.endswith("s") and len(model_name) > 1:
            ui.notify(
                "Model names should be singular (e.g., 'user' instead of 'users').",
                type="warning",
            )

        try:
            default_id_field = FieldInput(
                name="id",
                type=FieldDataType.UUID,
                primary_key=True,
                nullable=False,
                unique=True,
                index=False,
                foreign_key=False,
            )

            new_model = ModelInput(name=model_name, fields=[default_id_field])
            self.models.append(new_model)
            self._render_model_list()
        except ValidationError as e:
            notify_validation_error(e)

    def _on_delete_model(self, model: ModelInput) -> None:
        self.models.remove(model)
        if self.selected_model == model:
            self.selected_model = None
            self.on_select_model(None)
        self._render_model_list()

    def _on_edit_model(self, model: ModelInput, new_name: str) -> None:
        if any(m.name == new_name for m in self.models if m != model):
            ui.notify(f"Model '{new_name}' already exists.", type="negative")
            return

        model.name = new_name
        if self.selected_model == model:
            self.on_select_model(model)
        self._render_model_list()

    def _on_select_model(self, model: ModelInput) -> None:
        self.selected_model = model
        self.on_select_model(model)

    def _render_model_list(self) -> None:
        if hasattr(self, "model_list"):
            self.model_list.clear()
        else:
            self.model_list = ui.column().classes("items-align content-start w-full")

        with self.model_list:
            for model in self.models:
                is_auth_user = model.name == "auth_user"
                color = "text-green-500" if is_auth_user else None
                ModelRow(
                    model,
                    on_delete=self._on_delete_model,
                    on_edit=self._on_edit_model,
                    on_select=self._on_select_model,
                    color=color,
                )


class ModelEditorCard(ui.card):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.foreign_key_enabled = False
        self.selected_field = None
        self.selected_model = None
        self._build()

    def _build(self) -> None:
        with self:
            with ui.row().classes("w-full justify-between items-center"):
                self.model_name_display = ui.label().classes("text-lg font-bold")

                with ui.row().classes("gap-2"):
                    with (
                        ui.button(icon="bolt", color="amber")
                        .classes("self-end")
                        .tooltip("Quick-Add")
                    ):
                        with ui.menu():
                            self.created_at_item = ui.menu_item(
                                "Created At",
                                on_click=lambda: self._toggle_quick_add(
                                    "created_at",
                                    is_created_at_timestamp=True,
                                ),
                            )
                            self.updated_at_item = ui.menu_item(
                                "Updated At",
                                on_click=lambda: self._toggle_quick_add(
                                    "updated_at",
                                    is_updated_at_timestamp=True,
                                ),
                            )

                    ui.button(icon="add", on_click=self._open_modal).classes(
                        "self-end"
                    ).tooltip("Add Field")

            self.table = ui.table(
                columns=COLUMNS,
                rows=[],
                row_key="name",
                selection="single",
                on_select=lambda e: self._on_select_field(e.selection),
            ).classes("w-full no-shadow border-[1px]")

            with ui.row().classes("w-full justify-between items-center"):
                with ui.row().classes("justify-start gap-2"):
                    ui.label("Generate:").classes("text-md font-semibold self-center")
                    self.create_endpoints_checkbox = ui.checkbox(
                        "Endpoints",
                        value=True,
                        on_change=lambda v: setattr(
                            self.selected_model.metadata, "create_endpoints", v.value
                        ),
                    )
                    self.create_tests_checkbox = ui.checkbox(
                        "Tests",
                        value=True,
                        on_change=lambda v: setattr(
                            self.selected_model.metadata, "create_tests", v.value
                        ),
                    )
                    self.create_daos_checkbox = ui.checkbox(
                        "DAOs",
                        value=True,
                        on_change=lambda v: setattr(
                            self.selected_model.metadata, "create_daos", v.value
                        ),
                    )
                    self.create_dtos_checkbox = ui.checkbox(
                        "DTOs",
                        value=True,
                        on_change=lambda v: setattr(
                            self.selected_model.metadata, "create_dtos", v.value
                        ),
                    )

                with ui.row().classes("justify-end gap-2"):
                    ui.button(
                        "Update", on_click=self._update_field_modal
                    ).bind_visibility_from(self, "selected_field")
                    ui.button(
                        "Delete", on_click=self._delete_field
                    ).bind_visibility_from(self, "selected_field")

    def _toggle_quick_add(
        self,
        name: str,
        is_created_at_timestamp: bool = False,
        is_updated_at_timestamp: bool = False,
    ) -> None:

        if not self.selected_model:
            return

        attr = (
            "is_created_at_timestamp"
            if is_created_at_timestamp
            else "is_updated_at_timestamp"
        )

        existing_quick_add = next(
            (
                field
                for field in self.selected_model.fields
                if getattr(field, attr) is True
            ),
            None,
        )

        if existing_quick_add:
            self._delete(existing_quick_add)
            return

        self._add_field(
            name,
            "DateTime",
            False,
            False,
            False,
            False,
            False,
            None,
            is_created_at_timestamp,
            is_updated_at_timestamp,
        )

    def _open_modal(self) -> None:
        self.foreign_key_enabled = False

        with ui.dialog() as self.modal, ui.card().classes("no-shadow border-[1px]"):
            ui.label("Add New Field").classes("text-lg font-bold")
            with ui.row().classes("w-full gap-2"):
                field_name = ui.input(label="Field Name").classes("w-full")
                field_type = ui.select(list(FieldDataType), label="Field Type").classes(
                    "w-full"
                )
                primary_key = ui.checkbox("Primary Key").classes("w-full")
                foreign_key = ui.checkbox(
                    "Foreign Key",
                    on_change=lambda e: self._toggle_foreign_key(e.value),
                ).classes("w-full")
                nullable = ui.checkbox("Nullable").classes("w-full")
                unique = ui.checkbox("Unique").classes("w-full")
                index = ui.checkbox("Index").classes("w-full")
                self.back_populates_input = (
                    ui.input(
                        label="Back Populates",
                        placeholder="(Not required)",
                    )
                    .classes("w-full")
                    .bind_visibility_from(self, "foreign_key_enabled")
                )

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Close", on_click=self.modal.close)
                ui.button(
                    "Add Field",
                    on_click=lambda: self._add_field_modal(
                        name=field_name.value,
                        type=field_type.value,
                        primary_key=primary_key.value,
                        nullable=nullable.value,
                        unique=unique.value,
                        index=index.value,
                        foreign_key=foreign_key.value,
                        back_populates=(
                            self.back_populates_input.value
                            if foreign_key.value
                            and self.back_populates_input.value.strip()
                            else None
                        ),
                    ),
                )

        self.modal.open()

    def _add_field_modal(
        self,
        **kwargs,
    ) -> None:
        self._add_field(**kwargs)
        self.modal.close()

    def _toggle_foreign_key(self, enabled: bool) -> None:
        """Enable/disable the back_populates input based on foreign_key."""
        self.foreign_key_enabled = enabled
        if enabled:
            self._warn_foreign_key()
        else:
            self.back_populates_input.value = None

    def _warn_foreign_key(self) -> None:
        """Show a warning when foreign_key is enabled."""
        ui.notify(
            "ForeignKey field names should refer to a different table followed by '_id'. "
            "Example: 'restaurant_id'",
            type="warning",
        )

    def _validate_field_input(
        self,
        field_input: FieldInput,
    ) -> bool:
        if not self.selected_model:
            return True

        for field in self.selected_model.fields:
            if field.name == field_input.name and field != getattr(
                self, "selected_field", None
            ):
                ui.notify(
                    f"Field '{field_input.name}' already exists in this model.",
                    type="negative",
                )
                return False

            if field.primary_key and field_input.primary_key:
                ui.notify(
                    "A model cannot have multiple primary keys. "
                    f"Current primary key: '{field.name}'",
                    type="negative",
                )
                return False
        return True

    def _refresh_table(self, fields: list[FieldInput]) -> None:
        if self.selected_model is None:
            return
        self.table.rows = [field.model_dump() for field in fields]

        quick_add_created_at_enabled = any(
            field.is_created_at_timestamp for field in fields
        )
        quick_add_updated_at_enabled = any(
            field.is_updated_at_timestamp for field in fields
        )

        self.created_at_item.enabled = not quick_add_created_at_enabled
        self.updated_at_item.enabled = not quick_add_updated_at_enabled

    def _add_field(
        self,
        name: str,
        type: str,
        primary_key: bool,
        nullable: bool,
        unique: bool,
        index: bool,
        foreign_key: bool,
        back_populates: str | None,
        is_created_at_timestamp: bool = False,
        is_updated_at_timestamp: bool = False,
    ) -> None:
        try:
            field_input = FieldInput(
                name=name,
                type=FieldDataType(type),
                primary_key=primary_key,
                nullable=nullable,
                unique=unique,
                index=index,
                foreign_key=foreign_key,
                back_populates=back_populates,
                is_created_at_timestamp=is_created_at_timestamp,
                is_updated_at_timestamp=is_updated_at_timestamp,
            )
            if not self._validate_field_input(field_input):
                return
            if self.selected_model is None:
                return

            self.selected_model.fields.append(field_input)
            self._refresh_table(self.selected_model.fields)

        except ValidationError as e:
            notify_validation_error(e)

    def _on_select_field(self, selection: list[dict[str, Any]]) -> None:
        if selection and selection[0].get("name") == "id":
            self.selected_field = None
            self.table.selected = []
        else:
            self.selected_field = FieldInput(**selection[0]) if selection else None

    def _update_field_modal(self) -> None:
        if not self.selected_field or self.selected_field.name == "id":
            return

        self.foreign_key_enabled = self.selected_field.foreign_key

        with (
            ui.dialog() as self.update_modal,
            ui.card().classes("no-shadow border-[1px]"),
        ):
            ui.label("Update Field").classes("text-lg font-bold")
            with ui.row().classes("w-full gap-2"):
                field_name = ui.input(
                    label="Field Name", value=self.selected_field.name
                ).classes("w-full")
                field_type = ui.select(
                    list(FieldDataType),
                    label="Field Type",
                    value=self.selected_field.type,
                ).classes("w-full")
                primary_key = ui.checkbox(
                    "Primary Key", value=self.selected_field.primary_key
                ).classes("w-full")
                foreign_key = ui.checkbox(
                    "Foreign Key", value=self.selected_field.foreign_key
                ).classes("w-full")
                nullable = ui.checkbox(
                    "Nullable", value=self.selected_field.nullable
                ).classes("w-full")
                unique = ui.checkbox(
                    "Unique", value=self.selected_field.unique
                ).classes("w-full")
                index = ui.checkbox("Index", value=self.selected_field.index).classes(
                    "w-full"
                )
                self.back_populates_input = (
                    ui.input(
                        label="Back Populates",
                        placeholder="Not required",
                        value=self.selected_field.back_populates,
                    )
                    .classes("w-full")
                    .bind_visibility_from(self, "foreign_key_enabled")
                )

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Close", on_click=self.update_modal.close)
                ui.button(
                    "Update Field",
                    on_click=lambda: self._update_field(
                        field_name.value,
                        field_type.value,
                        primary_key.value,
                        nullable.value,
                        unique.value,
                        index.value,
                        foreign_key.value,
                        (
                            self.back_populates_input.value
                            if foreign_key.value
                            and self.back_populates_input.value.strip()
                            else None
                        ),
                    ),
                )

        self.update_modal.open()

    def _update_field(
        self,
        name: str,
        type: str,
        primary_key: bool,
        nullable: bool,
        unique: bool,
        index: bool,
        foreign_key: bool,
        back_populates: str | None,
    ) -> None:
        if not self.selected_field or self.selected_field.name == "id":
            return

        try:
            field_input = FieldInput(
                name=name,
                type=FieldDataType(type),
                primary_key=primary_key,
                nullable=nullable,
                unique=unique,
                index=index,
                foreign_key=foreign_key,
                back_populates=back_populates,
            )
            if not self._validate_field_input(field_input):
                return
            if not self.selected_model or not self.selected_field:
                return

            model_index = self.selected_model.fields.index(self.selected_field)
            self.selected_model.fields[model_index] = field_input
            self._refresh_table(self.selected_model.fields)
            self.update_modal.close()
            self.selected_field = None
        except ValidationError as e:
            notify_validation_error(e)

    def _delete(self, field: FieldInput) -> None:
        if not self.selected_model:
            return
        self.selected_model.fields.remove(field)
        self.selected_field = None
        self._refresh_table(self.selected_model.fields)

    def _delete_field(self) -> None:
        if (
            self.selected_model
            and self.selected_field
            and self.selected_field.name != "id"
        ):
            self._delete(self.selected_field)

    def set_selected_model(self, model: ModelInput | None) -> None:
        self.selected_model = model
        if model:
            self.model_name_display.text = model.name
            metadata = model.metadata
            self.create_endpoints_checkbox.value = metadata.create_endpoints
            self.create_tests_checkbox.value = metadata.create_tests
            self.create_dtos_checkbox.value = metadata.create_dtos
            self.create_daos_checkbox.value = metadata.create_daos
            self._refresh_table(model.fields)
            self.visible = True
        else:
            self.visible = False


class ProjectConfigPanel(ui.right_drawer):
    def __init__(
        self,
        model_panel: ModelPanel,
        initial_project: ProjectInput | None = None,
    ):
        super().__init__(value=True, elevated=False, bottom_corner=True)
        self.model_panel = model_panel
        self.initial_project = initial_project
        self._build()

    def _build(self) -> None:
        with self:
            with ui.column().classes(
                "items-align content-start w-full gap-4"
            ) as self.column:
                with ui.column().classes("w-full gap-2"):
                    ui.label("Project Name").classes("text-lg font-bold")
                    self.project_name = ui.input(
                        placeholder="Project Name",
                        value=(
                            self.initial_project.project_name
                            if self.initial_project
                            else ""
                        ),
                    ).classes("w-full")

                with ui.column().classes("w-full gap-2"):
                    ui.label("Database").classes("text-lg font-bold")
                    self.use_postgres = ui.checkbox(
                        "Postgres",
                        value=(
                            self.initial_project.use_postgres
                            if self.initial_project
                            else False
                        ),
                    ).classes("w-full")
                    self.use_mysql = (
                        ui.checkbox("MySQL")
                        .classes("w-full")
                        .tooltip("Coming soon!")
                        .set_enabled(False)
                    )
                    self.use_alembic = (
                        ui.checkbox(
                            "Alembic (Migrations)",
                            value=(
                                self.initial_project.use_alembic
                                if self.initial_project
                                else False
                            ),
                        )
                        .classes("w-full")
                        .bind_enabled_from(
                            self.use_postgres or self.use_mysql,
                            "value",
                        )
                    )

                with ui.column().classes("w-full gap-2"):
                    ui.label("Authentication").classes("text-lg font-bold")
                    self.use_builtin_auth = (
                        ui.checkbox(
                            "JWT Auth",
                            value=(
                                self.initial_project.use_builtin_auth
                                if self.initial_project
                                else False
                            ),
                            on_change=lambda e: self._handle_builtin_auth_change(
                                e.value
                            ),
                        )
                        .tooltip(
                            "Authentication is built in the API itself, using JWT."
                        )
                        .classes("w-full")
                        .bind_enabled_from(self.use_postgres, "value")
                    )

                with ui.column().classes("w-full gap-2"):
                    ui.label("Messaging").classes("text-lg font-bold")
                    self.use_kafka = (
                        ui.checkbox("Kafka")
                        .classes("w-full")
                        .tooltip("Coming soon!")
                        .set_enabled(False)
                    )
                    self.use_rabbitmq = ui.checkbox(
                        "RabbitMQ",
                        value=(
                            self.initial_project.use_rabbitmq
                            if self.initial_project
                            else False
                        ),
                    )

                with ui.column().classes("w-full gap-2"):
                    ui.label("Task Queues").classes("text-lg font-bold")
                    self.use_taskiq = (
                        ui.checkbox("Taskiq")
                        .classes("w-full")
                        .tooltip("Coming soon!")
                        .set_enabled(False)
                    )
                    self.use_celery = (
                        ui.checkbox("Celery")
                        .classes("w-full")
                        .tooltip("Coming soon!")
                        .set_enabled(False)
                    )

                with ui.column().classes("w-full gap-2"):
                    ui.label("Metrics").classes("text-lg font-bold")
                    self.use_prometheus = (
                        ui.checkbox("Prometheus")
                        .classes("w-full")
                        .tooltip("Coming soon!")
                        .set_enabled(False)
                    )

                with ui.column().classes("w-full gap-2"):
                    ui.label("Search").classes("text-lg font-bold")
                    self.use_elasticsearch = (
                        ui.checkbox("ElasticSearch")
                        .classes("w-full")
                        .tooltip("Coming soon!")
                        .set_enabled(False)
                    )

                with ui.column().classes("w-full gap-2"):
                    ui.label("Caching").classes("text-lg font-bold")
                    self.use_redis = ui.checkbox(
                        "Redis",
                        value=(
                            self.initial_project.use_redis
                            if self.initial_project
                            else False
                        ),
                    ).classes("w-full")

                with ui.column().classes("w-full gap-2"):
                    self.loading_spinner = ui.spinner(size="lg").classes(
                        "hidden mt-4 self-center"
                    )

                    self.create_button = ui.button(
                        "Generate", icon="rocket", on_click=self._create_project
                    ).classes("w-full py-3 text-lg font-bold mt-4")

    def _handle_builtin_auth_change(self, enabled: bool) -> None:
        if enabled:
            if any(model.name == "auth_user" for model in self.model_panel.models):
                ui.notify("The 'auth_user' model already exists.", type="negative")
                self.use_builtin_auth.value = False
                return

            try:
                auth_user_model = ModelInput(
                    name="auth_user",
                    fields=[
                        FieldInput(
                            name="id",
                            type=FieldDataType.UUID,
                            primary_key=True,
                            nullable=False,
                            unique=True,
                            index=True,
                            foreign_key=False,
                        ),
                        FieldInput(
                            name="email",
                            type=FieldDataType.STRING,
                            primary_key=False,
                            nullable=False,
                            unique=True,
                            index=True,
                            foreign_key=False,
                        ),
                        FieldInput(
                            name="password",
                            type=FieldDataType.STRING,
                            primary_key=False,
                            nullable=False,
                            unique=False,
                            index=False,
                            foreign_key=False,
                        ),
                    ],
                )
            except ValidationError as e:
                notify_validation_error(e)
            self.model_panel.models.append(auth_user_model)
            self.model_panel._render_model_list()
            ui.notify("The 'auth_user' model has been created.", type="positive")
        else:
            self.model_panel.models = [
                model for model in self.model_panel.models if model.name != "auth_user"
            ]
            self.model_panel._render_model_list()
            ui.notify("The 'auth_user' model has been deleted.", type="positive")

    async def _create_project(self) -> None:
        self.create_button.classes("hidden")
        self.loading_spinner.classes(remove="hidden")

        ongoing_notification = ui.notification("Generating project...")

        try:
            models = generate_model_instances(self.model_panel.models)

            if not models:
                ui.notify("No models to generate!", type="negative")
                return

            project_spec = ProjectSpec(
                project_name=self.project_name.value,
                use_postgres=self.use_postgres.value,
                use_alembic=self.use_alembic.value,
                use_builtin_auth=self.use_builtin_auth.value,
                use_redis=self.use_redis.value,
                use_rabbitmq=self.use_rabbitmq.value,
                models=models,
            )
            await build_project(project_spec)

            ui.notify(
                "Project successfully generated at: "
                f"{os.path.join(os.getcwd(), project_spec.project_name)}",
                type="positive",
            )

        except ValidationError as e:
            notify_validation_error(e)
        except Exception as e:
            ui.notify(f"Error creating Project: {e}", type="negative")
        finally:
            self.create_button.classes(remove="hidden")
            self.loading_spinner.classes("hidden")
            ongoing_notification.dismiss()


async def _init_no_ui(project_path: Path) -> None:
    project_spec = ProjectLoader(
        project_path, generate_model_instances
    ).load_project_spec()
    await build_project(project_spec)


def setup_ui() -> None:
    ui.add_head_html(
        '<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />'
    )
    ui.button.default_props("round flat dense")
    ui.input.default_props("dense")
    Header()


def load_initial_project(
    path: Path,
) -> tuple[ProjectInput | None, list[ModelInput] | None]:
    initial_project = None
    initial_models = None
    if path:
        initial_project = ProjectLoader(
            project_path=path, model_generator_func=generate_model_instances
        ).load_project_input()
        initial_models = initial_project.models
    return initial_project, initial_models


def create_ui_components(
    initial_project: ProjectInput | None, initial_models: list[ModelInput] | None
) -> None:
    with ui.column().classes("w-full h-full items-center justify-center mt-4"):
        model_editor_card = ModelEditorCard().classes("no-shadow")

    model_panel = ModelPanel(
        initial_models=initial_models,
        on_select_model=model_editor_card.set_selected_model,
    )
    project_config_panel = ProjectConfigPanel(
        model_panel=model_panel,
        initial_project=initial_project,
    )

    model_panel.project_config_panel = project_config_panel


def run_ui(reload: bool) -> None:
    ui.run(
        reload=reload,
        title="FastAPI Forge",
        port=native.find_open_port(8777, 8999),
    )


def init(
    reload: bool = False,
    use_example: bool = False,
    no_ui: bool = False,
    yaml_path: Path | None = None,
) -> None:
    base_path = Path(__file__).parent / "example-projects"
    default_path = base_path / "dry-service.yaml"
    example_path = base_path / "trustpilot-api.yaml"

    path = example_path if use_example else yaml_path if yaml_path else default_path

    if no_ui:
        asyncio.run(_init_no_ui(path))
        return

    setup_ui()

    initial_project = None
    initial_models = None
    if use_example or yaml_path:
        initial_project, initial_models = load_initial_project(path)

    create_ui_components(initial_project, initial_models)
    run_ui(reload)


if __name__ in {"__main__", "__mp_main__"}:
    init(reload=True, use_example=True)
