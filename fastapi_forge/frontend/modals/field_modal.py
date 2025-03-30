from nicegui import ui
from fastapi_forge.enums import FieldDataType
from fastapi_forge.dtos import ModelField
from typing import Callable
from fastapi_forge.frontend.state import state


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


class UpdateFieldModal(ui.dialog):
    def __init__(
        self,
        on_update_field: Callable,
    ):
        super().__init__()
        self.on_update_field = on_update_field
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
        if not state.selected_field:
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
        state.selected_field = field
        if field:
            self.field_name.value = field.name
            self.field_type.value = field.type
            self.primary_key.value = field.primary_key
            self.nullable.value = field.nullable
            self.unique.value = field.unique
            self.index.value = field.index

    def _reset(self) -> None:
        state.selected_field = None
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
