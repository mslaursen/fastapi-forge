from abc import ABC, abstractmethod
from collections.abc import Callable

from nicegui import ui
from pydantic import ValidationError

from fastapi_forge.enums import FieldDataTypeEnum
from fastapi_forge.frontend.notifications import (
    notify_validation_error,
    notify_value_error,
)
from fastapi_forge.frontend.state import state
from fastapi_forge.render.filters import JinjaFilters
from fastapi_forge.schemas import ModelField, ModelFieldMetadata


class BaseFieldModal(ui.dialog, ABC):
    title: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_kwargs = {}
        self.show_enum_selector: bool = False
        self.show_metadata: bool = False
        self.show_enum_defaults: bool = False
        self.on("hide", lambda: self.reset())
        self._build()

    @abstractmethod
    def _build_action_buttons(self) -> None:
        pass

    def _build(self) -> None:
        with self, ui.card().classes("w-full max-w-2xl no-shadow rounded-lg"):
            with ui.row().classes("w-full justify-between items-center p-4 border-b"):
                ui.label(self.title).classes("text-xl font-semibold")
                ui.button(
                    icon="visibility",
                    on_click=self._show_field_preview,
                ).props("flat dense").tooltip("Preview SQLAlchemy field code")

            with ui.column().classes("w-full p-6 space-y-4"):
                with ui.grid(columns=2).classes("w-full gap-4"):
                    self.field_name = ui.input(label="Field Name").props(
                        "outlined dense"
                    )
                    self.field_type = ui.select(
                        list(FieldDataTypeEnum),
                        label="Field Type",
                        on_change=self._handle_type_change,
                    ).props("outlined dense")
                    self.default_value_container = ui.column().classes("w-full")
                    with self.default_value_container:
                        self.default_value_input = (
                            ui.input(label="Default Value")
                            .props("outlined dense")
                            .classes("w-full")
                        )

                    self.enum_selector = (
                        ui.select(
                            [e.name for e in state.custom_enums],
                            label="Select Enum",
                            on_change=lambda: self._handle_type_change(),
                        )
                        .props("outlined dense")
                        .classes("w-full")
                        .bind_visibility_from(self, "show_enum_selector")
                    )

                with ui.row().classes("w-full justify-between gap-4"):
                    self.primary_key = ui.checkbox("Primary Key").props("dense")
                    self.nullable = ui.checkbox("Nullable").props("dense")
                    self.unique = ui.checkbox("Unique").props("dense")
                    self.index = ui.checkbox("Index").props("dense")

                self.metadata_card = (
                    ui.card()
                    .classes("w-full p-4 border rounded-lg")
                    .bind_visibility_from(self, "show_metadata")
                )
                with self.metadata_card:
                    with ui.row().classes("w-full justify-between items-center mb-2"):
                        ui.label("Field Metadata").classes("text-md font-medium")

                    with ui.row().classes("w-full gap-4"):
                        self.created_at = ui.checkbox("Created At Timestamp").props(
                            "dense"
                        )
                        self.updated_at = ui.checkbox("Updated At Timestamp").props(
                            "dense"
                        )

                with ui.card().classes("w-full p-4 border rounded-lg"):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("Extra Column Arguments").classes(
                            "text-md font-medium"
                        )
                        ui.button(
                            "Add Argument", icon="add", on_click=self._add_kwarg_row
                        )

                    self.kwargs_container = ui.column().classes("w-full gap-2 mt-2")

            with ui.row().classes("w-full justify-end p-4 border-t gap-2"):
                self._build_action_buttons()

    def _get_current_enum_values(self) -> list[str]:
        if not self.enum_selector.value:
            return []
        selected_enum = next(
            (e for e in state.custom_enums if e.name == self.enum_selector.value), None
        )
        return [v.name for v in selected_enum.values] if selected_enum else []

    def _handle_type_change(self) -> None:
        self.show_metadata = self.field_type.value == FieldDataTypeEnum.DATETIME
        self.show_enum_selector = self.field_type.value == FieldDataTypeEnum.ENUM
        self.show_enum_defaults = self.field_type.value == FieldDataTypeEnum.ENUM

        if self.show_enum_selector:
            self.enum_selector.options = [e.name for e in state.custom_enums]
            self.enum_selector.update()

        if self.show_enum_defaults:
            self.default_value_container.clear()
            with self.default_value_container:
                self.default_value_select = (
                    ui.select(
                        self._get_current_enum_values(),
                        label="Default Value",
                    )
                    .props("outlined dense")
                    .classes("w-full")
                )
        else:
            self.default_value_container.clear()
            with self.default_value_container:
                self.default_value_input = (
                    ui.input(label="Default Value")
                    .props("outlined dense")
                    .classes("w-full")
                )

    def _add_kwarg_row(self, key: str = "", value: str = "") -> None:
        with (
            self.kwargs_container,
            ui.row().classes("w-full items-center gap-2") as row,
        ):
            key_input = (
                ui.input(label="Key", value=key)
                .props("outlined dense")
                .classes("flex-1")
            )
            value_input = (
                ui.input(label="Value", value=value)
                .props("outlined dense")
                .classes("flex-1")
            )

            def update_kwargs():
                if key_input.value and value_input.value:
                    self.extra_kwargs[key_input.value] = value_input.value
                elif key_input.value in self.extra_kwargs:
                    del self.extra_kwargs[key_input.value]

            def remove_row():
                if key_input.value in self.extra_kwargs:
                    del self.extra_kwargs[key_input.value]
                row.delete()

            ui.button(icon="delete", on_click=remove_row)

            key_input.on("blur", update_kwargs)
            value_input.on("blur", update_kwargs)
            key_input.on("keydown.enter", update_kwargs)
            value_input.on("keydown.enter", update_kwargs)

    def _show_field_preview(self) -> None:
        if not self.field_name.value:
            ui.notify("Set a field name first", type="warning")
            return
        if not self.field_type.value:
            ui.notify("Select a field type first", type="warning")
            return
        try:
            default_value = (
                self.default_value_select.value
                if self.show_enum_defaults
                else self.default_value_input.value
            ) or None

            with ui.dialog() as modal, ui.card().classes("no-shadow border-[1px]"):
                preview_field = ModelField(
                    name=self.field_name.value,
                    type=self.field_type.value,
                    type_enum=self.enum_selector.value,
                    primary_key=self.primary_key.value,
                    nullable=self.nullable.value,
                    unique=self.unique.value,
                    index=self.index.value,
                    default_value=default_value,
                    extra_kwargs=self.extra_kwargs or None,
                    metadata=ModelFieldMetadata(
                        is_created_at_timestamp=(
                            self.created_at.value if self.show_metadata else False
                        ),
                        is_updated_at_timestamp=(
                            self.updated_at.value if self.show_metadata else False
                        ),
                        is_foreign_key=False,
                    ),
                )
                ui.code(JinjaFilters.generate_field(preview_field)).classes("w-full")
                modal.open()
        except ValidationError as exc:
            notify_validation_error(exc)

    def reset(self) -> None:
        self.field_name.value = ""
        self.field_type.value = None
        self.enum_selector.value = None
        self.primary_key.value = False
        self.nullable.value = False
        self.unique.value = False
        self.index.value = False
        if hasattr(self, "default_value_input"):
            self.default_value_input.value = ""
        if hasattr(self, "default_value_select"):
            self.default_value_select.value = None
        self.created_at.value = False
        self.updated_at.value = False
        self.show_metadata = False
        self.show_enum_selector = False
        self.show_enum_defaults = False
        self.extra_kwargs = {}
        self.kwargs_container.clear()


class AddFieldModal(BaseFieldModal):
    title = "Add Field"

    def __init__(self, on_add_field: Callable):
        super().__init__()
        self.on_add_field = on_add_field

    def _build_action_buttons(self) -> None:
        ui.button("Cancel", on_click=self.close)
        ui.button(
            self.title,
            on_click=lambda: self.on_add_field(
                name=self.field_name.value,
                type=self.field_type.value,
                type_enum=next(
                    (
                        e.name
                        for e in state.custom_enums
                        if e.name == self.enum_selector.value
                    ),
                    None,
                ),
                primary_key=self.primary_key.value,
                nullable=self.nullable.value,
                unique=self.unique.value,
                index=self.index.value,
                default_value=(
                    self.default_value_select.value
                    if self.show_enum_defaults
                    else self.default_value_input.value
                )
                or None,
                extra_kwargs=self.extra_kwargs or None,
                metadata=ModelFieldMetadata(
                    is_created_at_timestamp=(
                        self.created_at.value if self.show_metadata else False
                    ),
                    is_updated_at_timestamp=(
                        self.updated_at.value if self.show_metadata else False
                    ),
                    is_foreign_key=False,
                ),
            ),
        )


class UpdateFieldModal(BaseFieldModal):
    title = "Update Field"

    def __init__(self, on_update_field: Callable):
        super().__init__()
        self.on_update_field = on_update_field

    def _build_action_buttons(self) -> None:
        ui.button("Cancel", on_click=self.close)
        ui.button(
            self.title,
            on_click=self._handle_update,
        )

    def _handle_update(self) -> None:
        if not state.selected_field:
            return

        try:
            self.on_update_field(
                name=self.field_name.value,
                type=self.field_type.value,
                type_enum=(
                    next(
                        (
                            e.name
                            for e in state.custom_enums
                            if e.name == self.enum_selector.value
                        ),
                        None,
                    )
                    if self.show_enum_selector
                    else None
                ),
                primary_key=self.primary_key.value,
                nullable=self.nullable.value,
                unique=self.unique.value,
                index=self.index.value,
                default_value=(
                    self.default_value_select.value
                    if self.show_enum_defaults
                    else self.default_value_input.value
                )
                or None,
                extra_kwargs=self.extra_kwargs or None,
                metadata=ModelFieldMetadata(
                    is_created_at_timestamp=(
                        self.created_at.value if self.show_metadata else False
                    ),
                    is_updated_at_timestamp=(
                        self.updated_at.value if self.show_metadata else False
                    ),
                    is_foreign_key=False,
                ),
            )
            self.close()
        except ValueError as exc:
            notify_value_error(exc)
            return

    def _set_field(self, field: ModelField) -> None:
        state.selected_field = field
        if not field:
            return

        self.field_name.value = field.name
        self.field_type.value = field.type
        self.primary_key.value = field.primary_key
        self.nullable.value = field.nullable
        self.unique.value = field.unique
        self.index.value = field.index
        if field.type == FieldDataTypeEnum.ENUM and field.type_enum:
            self.enum_selector.value = field.type_enum
            self.enum_selector.update()
            if field.default_value:
                self.default_value_select.value = field.default_value
                self.default_value_select.update()
        elif field.default_value:
            self.default_value_input.value = field.default_value
            self.default_value_input.update()
        self.created_at.value = field.metadata.is_created_at_timestamp
        self.updated_at.value = field.metadata.is_updated_at_timestamp
        self.show_metadata = field.type == FieldDataTypeEnum.DATETIME
        self.show_enum_selector = field.type == FieldDataTypeEnum.ENUM
        self.extra_kwargs = field.extra_kwargs.copy() if field.extra_kwargs else {}
        self.kwargs_container.clear()

        if field.extra_kwargs:
            for key, value in field.extra_kwargs.items():
                self._add_kwarg_row(key, str(value))

        if field.type_enum and self.show_enum_selector:
            self.enum_selector.value = field.type_enum
            self.enum_selector.update()

    def open(self, field: ModelField | None = None) -> None:
        if field:
            self._set_field(field)
        super().open()
