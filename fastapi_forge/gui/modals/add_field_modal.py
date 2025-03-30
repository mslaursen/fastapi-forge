from pydantic import BaseModel, ValidationError
from fastapi_forge import dtos as m
from fastapi_forge.gui import notifications as n
from nicegui import ui
from fastapi_forge.enums import FieldDataType
import typing as t


class AddFieldModal(ui.dialog):
    def __init__(self):
        super().__init__()
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
