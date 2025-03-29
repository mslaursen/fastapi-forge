import asyncio
from nicegui import ui, native
from typing import Callable, Any
from pydantic import ValidationError
from fastapi_forge.enums import FieldDataType
from fastapi_forge.jinja import render_model_to_model
from fastapi_forge.dtos import (
    Model,
    ModelField,
    ModelRelationship,
    ProjectSpec,
    ModelFieldMetadata,
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
    {"name": "nullable", "label": "Nullable", "field": "nullable", "align": "center"},
    {"name": "unique", "label": "Unique", "field": "unique", "align": "center"},
    {"name": "index", "label": "Index", "field": "index", "align": "center"},
]

RELATIONSHIP_COLUMNS: list[dict[str, Any]] = [
    {
        "name": "field_name",
        "label": "Field Name",
        "field": "field_name",
        "required": True,
        "align": "left",
    },
    {
        "name": "target_model",
        "label": "Target Model",
        "field": "target_model",
        "align": "left",
    },
    {
        "name": "back_populates",
        "label": "Back Populates",
        "field": "back_populates",
        "align": "left",
    },
    {"name": "nullable", "label": "Nullable", "field": "nullable", "align": "center"},
    {"name": "index", "label": "Index", "field": "index", "align": "center"},
    {"name": "unique", "label": "Unique", "field": "unique", "align": "center"},
]


def notify_validation_error(e: ValidationError) -> None:
    msg = e.errors()[0].get("msg", "Something went wrong.")
    ui.notify(msg, type="negative")


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
        model: Model,
        on_delete: Callable[[Model], None],
        on_edit: Callable[[Model, str], None],
        on_select: Callable[[Model], None],
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
        on_select_model: Callable[[Model | None], None],
        project_config_panel: "ProjectConfigPanel | None" = None,
        initial_models: list[Model] | None = None,
    ):
        super().__init__(value=True, elevated=False, bottom_corner=True)
        self.classes("border-right[1px]")
        self.models = initial_models or []
        self.selected_model: Model | None = None
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
            project_input = ProjectSpec(
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
            self._render_model_list()
        except ValidationError as e:
            notify_validation_error(e)

    def _cleanup_relationships_for_deleted_model(self, deleted_model_name: str) -> None:
        for model in self.models:
            model.relationships = [
                rel
                for rel in model.relationships
                if rel.target_model != deleted_model_name
            ]

    def _on_delete_model(self, model: Model) -> None:
        self._cleanup_relationships_for_deleted_model(model.name)
        self.models.remove(model)
        if self.selected_model == model:
            self.selected_model = None
            self.on_select_model(None)
        self._render_model_list()

    def _update_relationships_for_rename(self, old_name: str, new_name: str) -> None:
        """Update all relationships that reference the renamed model."""
        for model in self.models:
            for relationship in model.relationships:
                if relationship.target_model == old_name:
                    relationship.target_model = new_name

    def _on_edit_model(self, model: Model, new_name: str) -> None:
        if any(m.name == new_name for m in self.models if m != model):
            ui.notify(f"Model '{new_name}' already exists.", type="negative")
            return

        old_name = model.name
        model.name = new_name
        self._update_relationships_for_rename(old_name, new_name)

        if self.selected_model == model:
            self.on_select_model(model)
        self._render_model_list()

    def _on_select_model(self, model: Model) -> None:
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


class AddFieldModal(ui.dialog):
    def __init__(self, on_add_field: Callable):
        super().__init__()
        self.on_add_field = on_add_field
        self.on("hide", lambda: self.reset())
        self._build()

    def _build(self) -> None:
        with self, ui.card().classes("no-shadow border-[1px]"):
            ui.label("Add New Field").classes("text-lg font-bold")
            with ui.row().classes("w-full gap-2"):
                self.field_name = ui.input(label="Field Name").classes("w-full")
                self.field_type = ui.select(
                    list(FieldDataType), label="Field Type"
                ).classes("w-full")
                self.primary_key = ui.checkbox("Primary Key").classes("w-full")
                self.nullable = ui.checkbox("Nullable").classes("w-full")
                self.unique = ui.checkbox("Unique").classes("w-full")
                self.index = ui.checkbox("Index").classes("w-full")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Close", on_click=self.close)
                ui.button(
                    "Add Field",
                    on_click=lambda: self.on_add_field(
                        name=self.field_name.value,
                        type=self.field_type.value,
                        primary_key=self.primary_key.value,
                        nullable=self.nullable.value,
                        unique=self.unique.value,
                        index=self.index.value,
                    ),
                )

    def reset(self) -> None:
        """Reset the modal fields to their default values."""
        self.field_name.value = ""
        self.field_type.value = None
        self.primary_key.value = False
        self.nullable.value = False
        self.unique.value = False
        self.index.value = False


class AddRelationModal(ui.dialog):
    def __init__(self, on_add_relation: Callable):
        super().__init__()
        self.on_add_relation = on_add_relation
        self.on("hide", lambda: self._reset())
        self._build()

    def _build(self) -> None:
        with self, ui.card().classes("no-shadow border-[1px]"):
            ui.label("Add Relationship").classes("text-lg font-bold")
            with ui.row().classes("w-full gap-2"):
                self.field_name = ui.input(label="Field Name").classes("w-full")
                self.target_model = ui.select(
                    label="Target Model",
                    options=[],
                ).classes("w-full")

                self.nullable = ui.checkbox("Nullable").classes("w-full")
                self.index = ui.checkbox("Index").classes("w-full")
                self.unique = ui.checkbox("Unique").classes("w-full")

                self.back_populates = ui.input(label="Back Populates").classes("w-full")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Close", on_click=self.close)
                ui.button(
                    "Add Relation",
                    on_click=self._add_relation,
                )

    def _set_target_model_options(self, models: list[Model]) -> None:
        self.target_model.options = [model.name for model in models]
        self.target_model.value = models[0].name if models else None

    def _add_relation(self) -> None:
        self.on_add_relation(
            field_name=self.field_name.value,
            target_model=self.target_model.value,
            back_populates=self.back_populates.value or None,
            nullable=self.nullable.value,
            index=self.index.value,
            unique=self.unique.value,
        )
        self.close()

    def _reset(self) -> None:
        self.field_name.value = ""
        self.target_model.value = None
        self.back_populates.value = ""
        self.nullable.value = False
        self.index.value = False
        self.unique.value = False

    def open(self, models: list[Model]) -> None:
        self.target_model.options = [model.name for model in models]
        self.target_model.value = models[0].name if models else None
        super().open()


class UpdateFieldModal(ui.dialog):
    def __init__(
        self,
        on_update_field: Callable,
    ):
        super().__init__()
        self.on_update_field = on_update_field
        self.selected_field: ModelField | None = None
        self.on("hide", lambda: self._reset())
        self._build()

    def _build(self) -> None:
        with self, ui.card().classes("no-shadow border-[1px]"):
            ui.label("Update Field").classes("text-lg font-bold")
            with ui.row().classes("w-full gap-2"):
                self.field_name = ui.input(label="Field Name", value="").classes(
                    "w-full"
                )
                self.field_type = ui.select(
                    list(FieldDataType),
                    label="Field Type",
                    value=None,
                ).classes("w-full")
                self.primary_key = ui.checkbox("Primary Key", value=False).classes(
                    "w-full"
                )
                self.nullable = ui.checkbox("Nullable", value=False).classes("w-full")
                self.unique = ui.checkbox("Unique", value=False).classes("w-full")
                self.index = ui.checkbox("Index", value=False).classes("w-full")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Close", on_click=self.close)
                ui.button(
                    "Update Field",
                    on_click=self._handle_update,
                )

    def _handle_update(self) -> None:
        if not self.selected_field:
            return

        self.on_update_field(
            self.field_name.value,
            self.field_type.value,
            self.primary_key.value,
            self.nullable.value,
            self.unique.value,
            self.index.value,
        )
        self.close()

    def _set_field(self, field: ModelField) -> None:
        self.selected_field = field
        if field:
            self.field_name.value = field.name
            self.field_type.value = field.type
            self.primary_key.value = field.primary_key
            self.nullable.value = field.nullable
            self.unique.value = field.unique
            self.index.value = field.index

    def _reset(self) -> None:
        self.selected_field = None
        self.field_name.value = ""
        self.field_type.value = None
        self.primary_key.value = False
        self.nullable.value = False
        self.unique.value = False
        self.index.value = False

    def open(self, field: ModelField | None = None) -> None:
        if field:
            self._set_field(field)
        super().open()


class UpdateRelationModal(ui.dialog):
    def __init__(self, on_update_relation: Callable):
        super().__init__()
        self.on_update_relation = on_update_relation
        self.selected_relation: ModelRelationship | None = None

        self.on("hide", lambda: self._reset())
        self._build()

    def _build(self) -> None:
        with self, ui.card().classes("no-shadow border-[1px]"):
            ui.label("Update Relationship").classes("text-lg font-bold")
            with ui.row().classes("w-full gap-2"):
                self.field_name = ui.input(label="Field Name").classes("w-full")
                self.target_model = ui.select(
                    label="Target Model",
                    options=[],
                ).classes("w-full")

                self.nullable = ui.checkbox("Nullable").classes("w-full")
                self.index = ui.checkbox("Index").classes("w-full")
                self.unique = ui.checkbox("Unique").classes("w-full")

                self.back_populates = ui.input(label="Back Populates").classes("w-full")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Close", on_click=self.close)
                ui.button(
                    "Update Relation",
                    on_click=self._update_relation,
                )

    def _update_relation(self) -> None:
        if not self.selected_relation:
            return

        self.on_update_relation(
            field_name=self.field_name.value,
            target_model=self.target_model.value,
            back_populates=self.back_populates.value,
            nullable=self.nullable.value,
            index=self.index.value,
            unique=self.unique.value,
        )
        self.close()

    def _set_relation(self, relation: ModelRelationship) -> None:
        self.selected_relation = relation
        if relation:
            self.field_name.value = relation.field_name
            self.target_model.value = relation.target_model
            self.nullable.value = relation.nullable
            self.index.value = relation.index
            self.unique.value = relation.unique
            self.back_populates.value = relation.back_populates

    def _reset(self) -> None:
        self.selected_relation = None
        self.field_name.value = ""
        self.target_model.value = None
        self.back_populates.value = ""
        self.nullable.value = False
        self.index.value = False
        self.unique.value = False

    def open(
        self,
        relation: ModelRelationship | None = None,
        models: list[Model] | None = None,
    ) -> None:
        if relation and models:
            self._set_relation(relation)
            self.target_model.options = [model.name for model in models]
            default_target_model = next(
                (model for model in models if model.name == relation.target_model),
                None,
            )
            if default_target_model:
                self.target_model.value = default_target_model.name
            self.target_model.options = [model.name for model in models]

        super().open()


class ModelEditorCard(ui.card):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.selected_field: ModelField | None = None
        self.selected_relation: ModelRelationship | None = None
        self.selected_model: Model | None = None
        self.model_panel: ModelPanel | None = None

        self.add_field_modal: AddFieldModal = AddFieldModal(
            on_add_field=self._handle_modal_add_field
        )
        self.add_relation_modal: AddRelationModal = AddRelationModal(
            on_add_relation=self._handle_modal_add_relation
        )
        self.update_field_modal: UpdateFieldModal = UpdateFieldModal(
            on_update_field=self._handle_update_field
        )
        self.update_relation_modal: UpdateRelationModal = UpdateRelationModal(
            on_update_relation=self._handle_update_relation
        )

        self._build()

    def _show_code_preview(self) -> None:
        if self.selected_model:
            self.selected_model.get_preview()
            with (
                ui.dialog() as modal,
                ui.card().classes("no-shadow border-[1px]"),
            ):
                code = render_model_to_model(self.selected_model.get_preview())
                code = code.split("class ")[1]
                code = f"# ID is inherited from the `Base` class\nclass {code}"
                ui.code(code).classes("w-full")
                modal.open()

    def _build(self) -> None:
        with self:
            with ui.row().classes("w-full justify-between items-center"):
                with ui.row().classes("gap-4 items-center"):
                    self.model_name_display = ui.label().classes("text-lg font-bold")
                    ui.button(
                        icon="visibility", on_click=self._show_code_preview
                    ).tooltip("Preview SQLAlchemy model code")

                with ui.row().classes("gap-2 items-center"):
                    with ui.button(icon="menu").tooltip("Generate"):
                        with ui.menu(), ui.column().classes("gap-0 p-2"):
                            self.create_endpoints_switch = ui.switch(
                                "Endpoints",
                                value=True,
                                on_change=lambda v: setattr(
                                    self.selected_model.metadata,
                                    "create_endpoints",
                                    v.value,
                                ),
                            )
                            self.create_tests_switch = ui.switch(
                                "Tests",
                                value=True,
                                on_change=lambda v: setattr(
                                    self.selected_model.metadata,
                                    "create_tests",
                                    v.value,
                                ),
                            )
                            self.create_daos_switch = ui.switch(
                                "DAOs",
                                value=True,
                                on_change=lambda v: setattr(
                                    self.selected_model.metadata,
                                    "create_daos",
                                    v.value,
                                ),
                            )
                            self.create_dtos_switch = ui.switch(
                                "DTOs",
                                value=True,
                                on_change=lambda v: setattr(
                                    self.selected_model.metadata,
                                    "create_dtos",
                                    v.value,
                                ),
                            )

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

                    with ui.button(icon="add").classes("self-end"):
                        with ui.menu():
                            ui.menu_item(
                                "Field",
                                on_click=lambda: self.add_field_modal.open(),
                            )
                            ui.menu_item(
                                "Relationship",
                                on_click=lambda: self.add_relation_modal.open(
                                    models=(
                                        self.model_panel.models
                                        if self.model_panel
                                        else []
                                    ),
                                ),
                            )

            with ui.expansion("Fields", value=True).classes("w-full"):
                self.table = ui.table(
                    columns=COLUMNS,
                    rows=[],
                    row_key="name",
                    selection="single",
                    on_select=lambda e: self._on_select_field(e.selection),
                ).classes("w-full no-shadow border-[1px]")

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button(
                        icon="edit",
                        on_click=lambda: self.update_field_modal.open(
                            self.selected_field
                        ),
                    ).bind_visibility_from(self, "selected_field")
                    ui.button(
                        icon="delete", on_click=self._delete_field
                    ).bind_visibility_from(self, "selected_field")

            with ui.expansion("Relationships", value=True).classes("w-full"):
                self.relationship_table = ui.table(
                    columns=RELATIONSHIP_COLUMNS,
                    rows=[],
                    row_key="field_name",
                    selection="single",
                    on_select=lambda e: self._on_select_relation(e.selection),
                ).classes("w-full no-shadow border-[1px]")

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button(
                        icon="edit",
                        on_click=lambda: self.update_relation_modal.open(
                            self.selected_relation,
                            self.model_panel.models if self.model_panel else [],
                        ),
                    ).bind_visibility_from(self, "selected_relation")
                    ui.button(
                        icon="delete", on_click=self._delete_relation
                    ).bind_visibility_from(self, "selected_relation")

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
                if getattr(field.metadata, attr) is True
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
            is_created_at_timestamp,
            is_updated_at_timestamp,
        )

    def _handle_modal_add_field(
        self,
        **kwargs,
    ) -> None:
        try:
            self._add_field(**kwargs)
            self.add_field_modal.close()
        except ValueError as e:
            ui.notify(str(e), type="negative")

    def _handle_modal_add_relation(
        self,
        field_name: str,
        target_model: str,
        nullable: bool,
        index: bool,
        unique: bool,
        back_populates: str | None = None,
    ) -> None:
        if not self.selected_model:
            return

        target_model_instance = next(
            (model for model in self.model_panel.models if model.name == target_model),
            None,
        )
        if not target_model_instance:
            ui.notify(f"Model '{target_model}' not found.", type="negative")
            return

        if field_name in [field.name for field in self.selected_model.fields]:
            ui.notify(f"Field '{field_name}' already exists.", type="negative")
            return

        try:
            relationship = ModelRelationship(
                field_name=field_name,
                target_model=target_model_instance.name,
                back_populates=back_populates,
                nullable=nullable,
                index=index,
                unique=unique,
            )
        except ValidationError as e:
            notify_validation_error(e)
            return

        self.selected_model.relationships.append(relationship)

        self._refresh_relationship_table(self.selected_model.relationships)

    def _validate_field_input(
        self,
        field_input: ModelField,
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

    def _refresh_table(self, fields: list[ModelField]) -> None:
        if self.selected_model is None:
            return
        self.table.rows = [field.model_dump() for field in fields]

        quick_add_created_at_enabled = any(
            field.metadata.is_created_at_timestamp for field in fields
        )
        quick_add_updated_at_enabled = any(
            field.metadata.is_updated_at_timestamp for field in fields
        )

        self.created_at_item.enabled = not quick_add_created_at_enabled
        self.updated_at_item.enabled = not quick_add_updated_at_enabled

        self._deselect_field()

    def _refresh_relationship_table(
        self, relationships: list[ModelRelationship]
    ) -> None:
        if self.selected_model is None:
            return
        self.relationship_table.rows = [
            relationship.model_dump() for relationship in relationships
        ]
        self._deselect_relation()

    def _add_field(
        self,
        name: str,
        type: str,
        primary_key: bool,
        nullable: bool,
        unique: bool,
        index: bool,
        is_created_at_timestamp: bool = False,
        is_updated_at_timestamp: bool = False,
    ) -> None:
        try:
            field_input = ModelField(
                name=name,
                type=FieldDataType(type),
                primary_key=primary_key,
                nullable=nullable,
                unique=unique,
                index=index,
                metadata=ModelFieldMetadata(
                    is_created_at_timestamp=is_created_at_timestamp,
                    is_updated_at_timestamp=is_updated_at_timestamp,
                ),
            )
            if not self._validate_field_input(field_input):
                return
            if self.selected_model is None:
                return

            self.selected_model.fields.append(field_input)
            self._refresh_table(self.selected_model.fields)

        except ValidationError as e:
            notify_validation_error(e)

    def _deselect_field(self) -> None:
        self.selected_field = None
        self.table.selected = []

    def _deselect_relation(self) -> None:
        self.selected_relation = None
        self.relationship_table.selected = []

    def _on_select_field(self, selection: list[dict[str, Any]]) -> None:
        if not self.selected_model:
            return
        if not selection:
            self._deselect_field()
            return
        if selection[0].get("name") == "id":
            self._deselect_field()
        else:
            self.selected_field = next(
                (
                    field
                    for field in self.selected_model.fields
                    if field.name == selection[0]["name"]
                ),
                None,
            )

    def _on_select_relation(self, selection: list[dict[str, Any]]) -> None:
        if not self.selected_model:
            return
        if not selection:
            self._deselect_relation()
            return
        self.selected_relation = next(
            (
                relation
                for relation in self.selected_model.relationships
                if relation.field_name == selection[0]["field_name"]
            ),
            None,
        )

    def _handle_update_field(
        self,
        name: str,
        type: str,
        primary_key: bool,
        nullable: bool,
        unique: bool,
        index: bool,
    ) -> None:
        if (
            not self.selected_model
            or not self.selected_field
            or self.selected_field.name == "id"
        ):
            return

        try:
            field_input = ModelField(
                name=name,
                type=FieldDataType(type),
                primary_key=primary_key,
                nullable=nullable,
                unique=unique,
                index=index,
                metadata=self.selected_field.metadata,
            )
            if not self._validate_field_input(field_input):
                return

            model_index = self.selected_model.fields.index(self.selected_field)
            self.selected_model.fields[model_index] = field_input
            self._refresh_table(self.selected_model.fields)

        except ValidationError as e:
            notify_validation_error(e)

    def _handle_update_relation(
        self,
        field_name: str,
        target_model: str,
        nullable: bool = False,
        index: bool = False,
        unique: bool = False,
        back_populates: str | None = None,
    ) -> None:
        if not self.selected_model or not self.selected_relation:
            return

        target_model_instance = next(
            (model for model in self.model_panel.models if model.name == target_model),
            None,
        )
        if not target_model_instance:
            ui.notify(f"Model '{target_model}' not found.", type="negative")
            return

        if (
            field_name in [field.name for field in self.selected_model.fields]
            and field_name != self.selected_relation.field_name
        ):
            ui.notify(f"Field '{field_name}' already exists.", type="negative")
            return
        try:
            relationship = ModelRelationship(
                field_name=field_name,
                target_model=target_model_instance.name,
                back_populates=back_populates or None,
                nullable=nullable,
                index=index,
                unique=unique,
            )
        except ValidationError as e:
            notify_validation_error(e)
            return

        model_index = self.selected_model.relationships.index(self.selected_relation)
        self.selected_model.relationships[model_index] = relationship
        self._refresh_relationship_table(self.selected_model.relationships)

    def _delete(self, field: ModelField) -> None:
        if not self.selected_model:
            ui.notify("No model selected.", type="negative")
            return
        self.selected_model.fields.remove(field)
        self._refresh_table(self.selected_model.fields)

    def _delete_relation(self) -> None:
        if self.selected_model and self.selected_relation:
            self.selected_model.relationships.remove(self.selected_relation)
            self._refresh_relationship_table(self.selected_model.relationships)

    def _delete_field(self) -> None:
        if (
            self.selected_model
            and self.selected_field
            and self.selected_field.name != "id"
        ):
            self._delete(self.selected_field)

    def set_selected_model(self, model: Model | None) -> None:
        self.selected_model = model
        if model:
            self.model_name_display.text = model.name
            metadata = model.metadata

            self.create_endpoints_switch.value = metadata.create_endpoints
            self.create_tests_switch.value = metadata.create_tests
            self.create_dtos_switch.value = metadata.create_dtos
            self.create_daos_switch.value = metadata.create_daos

            self._refresh_table(model.fields)
            self._refresh_relationship_table(model.relationships)
            self.visible = True
        else:
            self.visible = False


class ProjectConfigPanel(ui.right_drawer):
    def __init__(
        self,
        model_panel: ModelPanel,
        initial_project: ProjectSpec | None = None,
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
                auth_user_model = Model(
                    name="auth_user",
                    fields=[
                        ModelField(
                            name="id",
                            type=FieldDataType.UUID,
                            primary_key=True,
                            unique=True,
                            index=True,
                        ),
                        ModelField(
                            name="email",
                            type=FieldDataType.STRING,
                            unique=True,
                            index=True,
                        ),
                        ModelField(
                            name="password",
                            type=FieldDataType.STRING,
                        ),
                        ModelField(
                            name="created_at",
                            type=FieldDataType.DATETIME,
                            metadata=ModelFieldMetadata(is_created_at_timestamp=True),
                        ),
                        ModelField(
                            name="updated_at",
                            type=FieldDataType.DATETIME,
                            metadata=ModelFieldMetadata(is_updated_at_timestamp=True),
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
            models = self.model_panel.models

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
    project_spec = ProjectLoader(project_path).load_project_spec()
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
) -> tuple[ProjectSpec | None, list[Model] | None]:
    initial_project = None
    initial_models = None
    if path:
        initial_project = ProjectLoader(project_path=path).load_project_input()
        initial_models = initial_project.models
    return initial_project, initial_models


def create_ui_components(
    initial_project: ProjectSpec | None, initial_models: list[Model] | None
) -> None:
    with ui.column().classes("w-full h-full items-center justify-center mt-4"):
        model_editor_card = ModelEditorCard().classes("no-shadow min-w-[600px]")

    model_panel = ModelPanel(
        initial_models=initial_models,
        on_select_model=model_editor_card.set_selected_model,
    )
    project_config_panel = ProjectConfigPanel(
        model_panel=model_panel,
        initial_project=initial_project,
    )

    model_panel.project_config_panel = project_config_panel
    model_editor_card.model_panel = model_panel


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
    default_path = base_path / "empty-service.yaml"
    example_path = base_path / "game_zone.yaml"

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
