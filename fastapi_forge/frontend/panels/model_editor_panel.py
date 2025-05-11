from typing import Any

from nicegui import ui
from pydantic import ValidationError

from fastapi_forge.enums import FieldDataTypeEnum, OnDeleteEnum
from fastapi_forge.frontend import validation
from fastapi_forge.frontend.constants import (
    DEFAULT_AUTH_USER_FIELDS,
    FIELD_COLUMNS,
    RELATIONSHIP_COLUMNS,
)
from fastapi_forge.frontend.modals import (
    AddFieldModal,
    AddRelationModal,
    UpdateFieldModal,
    UpdateRelationModal,
)
from fastapi_forge.frontend.notifications import (
    notify_field_exists,
    notify_validation_error,
    notify_value_error,
)
from fastapi_forge.frontend.state import state
from fastapi_forge.schemas import (
    Model,
    ModelField,
    ModelFieldMetadata,
    ModelRelationship,
)


class ModelEditorPanel(ui.card):
    def __init__(self):
        super().__init__()
        self.visible = False

        state.select_model_fn = self.set_selected_model
        state.deselect_model_fn = self.deselect_model
        state.render_model_editor_fn = self.refresh
        state.render_actions_fn = self._render_action_group

        self.add_field_modal: AddFieldModal = AddFieldModal(
            on_add_field=self._handle_modal_add_field,
        )
        self.add_relation_modal: AddRelationModal = AddRelationModal(
            on_add_relation=self._handle_modal_add_relation,
        )
        self.update_field_modal: UpdateFieldModal = UpdateFieldModal(
            on_update_field=self._handle_update_field,
        )
        self.update_relation_modal: UpdateRelationModal = UpdateRelationModal(
            on_update_relation=self._handle_update_relation,
        )

        self._build()

    def _show_code_preview(self) -> None:
        if state.selected_model:
            with (
                ui.dialog() as modal,
                ui.card().classes("no-shadow border-[1px]"),
            ):
                model_renderer = state.get_render_manager().get_renderer("model")
                code = model_renderer.render(state.selected_model.get_preview())
                code = code.split("class ")[1]
                code = f"# ID is inherited from the `Base` class\nclass {code}"
                ui.code(code).classes("w-full")
                modal.open()

    def _toggle_auth_model(self) -> None:
        if not state.selected_model or not state.use_builtin_auth:
            return

        if not state.selected_model.metadata.is_auth_model and any(
            m.metadata.is_auth_model for m in state.models
        ):
            ui.notify(
                "Cannot have more than one authentication model.", type="negative"
            )
            return

        model = state.selected_model
        model.metadata.is_auth_model = not model.metadata.is_auth_model

        if not model.metadata.is_auth_model:
            self._remove_auth_fields(model)
            if state.render_model_editor_fn:
                state.render_model_editor_fn()

        if state.render_content_fn:
            state.render_content_fn.refresh()

        self._render_action_group.refresh()

        if model.metadata.is_auth_model:
            self._setup_auth_model_fields(model)

    def _remove_auth_fields(self, model: Model) -> None:
        for field_name in ("email", "password"):
            if field := next((f for f in model.fields if f.name == field_name), None):
                model.fields.remove(field)

    def _setup_auth_model_fields(self, model: Model) -> None:
        self._remove_auth_fields(model)
        id_index = 0
        insert_position = id_index + 1 if id_index >= 0 else 0
        for field in reversed(DEFAULT_AUTH_USER_FIELDS):
            model.fields.insert(insert_position, field)

        self._refresh_table(model.fields)

    @ui.refreshable
    def _render_action_group(self) -> None:
        ui.button(
            icon="security",
            on_click=self._toggle_auth_model,
            color=(
                "green"
                if state.use_builtin_auth
                and state.selected_model
                and state.selected_model.metadata.is_auth_model
                else "grey"
            ),
        ).tooltip("Authentication model").bind_visibility_from(
            state, "use_builtin_auth"
        )

    def _build(self) -> None:
        with self:
            with ui.row().classes("w-full justify-between items-center"):
                with ui.row().classes("gap-4 items-center"):
                    self.model_name_display = ui.label().classes("text-lg font-bold")
                    ui.button(
                        icon="visibility",
                        on_click=self._show_code_preview,
                    ).tooltip("Preview SQLAlchemy model code")

                with ui.row().classes("gap-2 items-center"):
                    self._render_action_group()
                    with (
                        ui.button(icon="menu").tooltip("Generate"),
                        ui.menu(),
                        ui.column().classes("gap-0 p-2"),
                    ):
                        self.create_endpoints_switch = ui.switch(
                            "Endpoints",
                            value=True,
                            on_change=lambda v: setattr(
                                state.selected_model.metadata,
                                "create_endpoints",
                                v.value,
                            ),
                        )
                        self.create_tests_switch = ui.switch(
                            "Tests",
                            value=True,
                            on_change=lambda v: setattr(
                                state.selected_model.metadata,
                                "create_tests",
                                v.value,
                            ),
                        )
                        self.create_daos_switch = ui.switch(
                            "DAOs",
                            value=True,
                            on_change=lambda v: setattr(
                                state.selected_model.metadata,
                                "create_daos",
                                v.value,
                            ),
                        )
                        self.create_dtos_switch = ui.switch(
                            "DTOs",
                            value=True,
                            on_change=lambda v: setattr(
                                state.selected_model.metadata,
                                "create_dtos",
                                v.value,
                            ),
                        )

                    with (
                        ui.button(icon="bolt", color="amber")
                        .classes("self-end")
                        .tooltip("Quick-Add"),
                        ui.menu(),
                    ):
                        self.primary_key_item = ui.menu_item(
                            "Primary Key",
                            on_click=lambda: self._toggle_quick_add(
                                "id",
                                is_primary_key=True,
                            ),
                        )
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

                    with ui.button(icon="add").classes("self-end"), ui.menu():
                        ui.menu_item(
                            "Field",
                            on_click=lambda: self.add_field_modal.open(),
                        )
                        ui.menu_item(
                            "Relationship",
                            on_click=lambda: self.add_relation_modal.open(
                                models=state.models,
                            ),
                        )

            with ui.expansion("Fields", value=True).classes("w-full"):
                self.table = ui.table(
                    columns=FIELD_COLUMNS,
                    rows=[],
                    row_key="name",
                    selection="single",
                    on_select=lambda e: self._on_select_field(e.selection),
                ).classes("w-full no-shadow border-[1px]")

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button(
                        icon="edit",
                        on_click=lambda: self.update_field_modal.open(
                            state.selected_field,
                        ),
                    ).bind_visibility_from(state, "selected_field")
                    ui.button(
                        icon="delete",
                        on_click=self._delete_field,
                    ).bind_visibility_from(state, "selected_field")

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
                            state.selected_relation,
                            state.models,
                        ),
                    ).bind_visibility_from(state, "selected_relation")
                    ui.button(
                        icon="delete",
                        on_click=self._delete_relation,
                    ).bind_visibility_from(state, "selected_relation")

    def _toggle_quick_add(
        self,
        name: str,
        is_primary_key: bool = False,
        is_created_at_timestamp: bool = False,
        is_updated_at_timestamp: bool = False,
    ) -> None:
        if not state.selected_model:
            return

        if is_primary_key:
            existing_pk = next(
                (field for field in state.selected_model.fields if field.primary_key),
                None,
            )
            if existing_pk:
                self._delete(existing_pk)
                return

            self._add_field(
                name=name,
                type="UUID",
                primary_key=True,
                nullable=False,
                unique=True,
                index=True,
            )
            return

        attr = (
            "is_created_at_timestamp"
            if is_created_at_timestamp
            else "is_updated_at_timestamp"
        )

        existing_quick_add = next(
            (
                field
                for field in state.selected_model.fields
                if getattr(field.metadata, attr) is True
            ),
            None,
        )

        if existing_quick_add:
            self._delete(existing_quick_add)
            return

        self._add_field(
            name=name,
            type="DateTime",
            primary_key=False,
            nullable=False,
            unique=False,
            index=False,
            default_value="datetime.now(timezone.utc)",
            extra_kwargs=(
                {"onupdate": "datetime.now(timezone.utc)"}
                if is_updated_at_timestamp
                else None
            ),
            metadata=ModelFieldMetadata(
                is_created_at_timestamp=is_created_at_timestamp,
                is_updated_at_timestamp=is_updated_at_timestamp,
            ),
        )

    def _handle_modal_add_field(
        self,
        **kwargs,
    ) -> None:
        try:
            self._add_field(**kwargs)
            self.add_field_modal.close()
        except ValueError as exc:
            notify_value_error(exc)

    def _handle_modal_add_relation(
        self,
        field_name: str,
        target_model: str,
        on_delete: OnDeleteEnum,
        nullable: bool,
        index: bool,
        unique: bool,
        back_populates: str | None = None,
    ) -> None:
        if not state.selected_model:
            return

        try:
            validation.raise_if_missing_fields(
                [
                    ("Field Name", field_name),
                    ("Target Model", target_model),
                    ("On Delete", on_delete),
                ]
            )
        except ValueError as exc:
            raise exc

        target_model_instance = next(
            (model for model in state.models if model.name == target_model),
            None,
        )
        if not target_model_instance:
            ui.notify(f"Model '{target_model}' not found.", type="negative")
            return

        if field_name in [field.name for field in state.selected_model.fields]:
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
                on_delete=on_delete,
            )
        except ValidationError as exc:
            notify_validation_error(exc)
            return

        state.selected_model.relationships.append(relationship)

        self._refresh_relationship_table(state.selected_model.relationships)

    def refresh(self) -> None:
        if state.selected_model is None:
            return
        self._refresh_table(state.selected_model.fields)
        self._refresh_relationship_table(state.selected_model.relationships)

    def _refresh_table(self, fields: list[ModelField]) -> None:
        if state.selected_model is None:
            return
        self.table.rows = [field.model_dump() for field in fields]

        quick_add_primary_key_enabled = any(field.primary_key for field in fields)
        quick_add_created_at_enabled = any(
            field.metadata.is_created_at_timestamp for field in fields
        )
        quick_add_updated_at_enabled = any(
            field.metadata.is_updated_at_timestamp for field in fields
        )

        self.primary_key_item.enabled = not quick_add_primary_key_enabled
        self.created_at_item.enabled = not quick_add_created_at_enabled
        self.updated_at_item.enabled = not quick_add_updated_at_enabled

        self._deselect_field()

    def _refresh_relationship_table(
        self,
        relationships: list[ModelRelationship],
    ) -> None:
        if state.selected_model is None:
            return
        self.relationship_table.rows = [
            relationship.model_dump() for relationship in relationships
        ]
        self._deselect_relation()

    def _field_name_exists(self, field_name: str) -> bool:
        return any(field.name == field_name for field in state.selected_model.fields)

    def _add_field(
        self,
        *,
        name: str,
        type: str,
        primary_key: bool,
        nullable: bool,
        unique: bool,
        index: bool,
        type_enum: str | None = None,
        default_value: str | None = None,
        extra_kwargs: dict[str, Any] | None = None,
        metadata: ModelFieldMetadata | None = None,
    ) -> None:
        if state.selected_model is None:
            return

        try:
            validation.raise_if_missing_fields(
                [("Field Name", name), ("Field Type", type)]
            )
        except ValueError as exc:
            raise exc

        if self._field_name_exists(name):
            notify_field_exists(name, state.selected_model.name)
            return

        field_type = FieldDataTypeEnum(type)
        if type_enum and field_type != FieldDataTypeEnum.ENUM:
            type_enum = None

        try:
            field_input = ModelField(
                name=name,
                type=field_type,
                type_enum=type_enum,
                primary_key=primary_key,
                nullable=nullable,
                unique=unique,
                index=index,
                default_value=default_value,
                extra_kwargs=extra_kwargs,
            )

            if metadata:
                field_input.metadata = metadata

            state.selected_model.fields.append(field_input)
            self._refresh_table(state.selected_model.fields)

        except ValidationError as exc:
            notify_validation_error(exc)

    def _deselect_field(self) -> None:
        state.selected_field = None
        self.table.selected = []

    def _deselect_relation(self) -> None:
        state.selected_relation = None
        self.relationship_table.selected = []

    def _on_select_field(self, selection: list[dict[str, Any]]) -> None:
        if not state.selected_model or not selection:
            self._deselect_field()
            return

        name = selection[0].get("name")

        if (
            state.selected_model.metadata.is_auth_model
            and state.use_builtin_auth
            and name in ("password", "email")
        ):
            ui.notify(
                f"Cannot edit {name} field in authentication model.",
                type="warning",
            )
            self._deselect_field()
            return

        state.selected_field = next(
            (field for field in state.selected_model.fields if field.name == name), None
        )

    def _on_select_relation(self, selection: list[dict[str, Any]]) -> None:
        if not state.selected_model:
            return
        if not selection:
            self._deselect_relation()
            return
        state.selected_relation = next(
            (
                relation
                for relation in state.selected_model.relationships
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
        metadata: ModelFieldMetadata,
        type_enum: str | None = None,
        default_value: str | None = None,
        extra_kwargs: dict[str, Any] | None = None,
    ) -> None:
        if not state.selected_model or not state.selected_field:
            return

        if (
            state.selected_model
            and state.selected_model.metadata.is_auth_model
            and state.use_builtin_auth
        ):
            return

        try:
            validation.raise_if_missing_fields(
                [("Field Name", name), ("Field Type", type)]
            )
        except ValueError as exc:
            raise exc

        if state.selected_field.name != name and self._field_name_exists(name):
            notify_field_exists(name, state.selected_model.name)
            return

        field_type = FieldDataTypeEnum(type)
        if type_enum and field_type != FieldDataTypeEnum.ENUM:
            type_enum = None

        try:
            field_input = ModelField(
                name=name,
                type=field_type,
                type_enum=type_enum,
                primary_key=primary_key,
                nullable=nullable,
                unique=unique,
                index=index,
                default_value=default_value,
                extra_kwargs=extra_kwargs,
                metadata=metadata,
            )

            model_index = state.selected_model.fields.index(state.selected_field)
            state.selected_model.fields[model_index] = field_input
            self._refresh_table(state.selected_model.fields)

        except ValidationError as exc:
            notify_validation_error(exc)

    def _handle_update_relation(
        self,
        field_name: str,
        target_model: str,
        nullable: bool = False,
        index: bool = False,
        unique: bool = False,
        on_delete: OnDeleteEnum = OnDeleteEnum.CASCADE,
        back_populates: str | None = None,
    ) -> None:
        if not state.selected_model or not state.selected_relation:
            return

        try:
            validation.raise_if_missing_fields(
                [
                    ("Field Name", field_name),
                    ("Target Model", target_model),
                    ("On Delete", on_delete),
                ]
            )
        except ValueError as exc:
            raise exc

        target_model_instance = next(
            (model for model in state.models if model.name == target_model),
            None,
        )
        if not target_model_instance:
            ui.notify(f"Model '{target_model}' not found.", type="negative")
            return

        if (
            field_name in [field.name for field in state.selected_model.fields]
            and field_name != state.selected_relation.field_name
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
                on_delete=on_delete,
            )
        except ValidationError as exc:
            notify_validation_error(exc)
            return

        model_index = state.selected_model.relationships.index(state.selected_relation)
        state.selected_model.relationships[model_index] = relationship
        self._refresh_relationship_table(state.selected_model.relationships)

    def _delete(self, field: ModelField) -> None:
        if not state.selected_model:
            ui.notify("No model selected.", type="negative")
            return
        state.selected_model.fields.remove(field)
        self._refresh_table(state.selected_model.fields)

    def _delete_relation(self) -> None:
        if state.selected_model and state.selected_relation:
            state.selected_model.relationships.remove(state.selected_relation)
            self._refresh_relationship_table(state.selected_model.relationships)

    def _delete_field(self) -> None:
        if state.selected_model and state.selected_field:
            self._delete(state.selected_field)

    def set_selected_model(self, model: Model) -> None:
        self.model_name_display.text = model.name
        metadata = model.metadata

        self.create_endpoints_switch.value = metadata.create_endpoints
        self.create_tests_switch.value = metadata.create_tests
        self.create_dtos_switch.value = metadata.create_dtos
        self.create_daos_switch.value = metadata.create_daos

        self._refresh_table(model.fields)
        self._refresh_relationship_table(model.relationships)
        self.visible = True

    def deselect_model(self) -> None:
        self.visible = False
