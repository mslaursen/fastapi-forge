from typing import Any

from nicegui import ui
from pydantic import ValidationError

from fastapi_forge.frontend import validation
from fastapi_forge.frontend.constants import ENUM_COLUMNS
from fastapi_forge.frontend.modals import (
    AddEnumValueModal,
    UpdateEnumValueModal,
)
from fastapi_forge.frontend.notifications import (
    notify_enum_value_exists,
    notify_validation_error,
)
from fastapi_forge.frontend.state import state
from fastapi_forge.schemas import CustomEnum, CustomEnumValue


class EnumEditorPanel(ui.card):
    def __init__(self):
        super().__init__()
        self.visible = False

        state.select_enum_fn = self.set_selected_enum
        state.deselect_enum_fn = self._handle_deselect_enum

        self.add_value_modal = AddEnumValueModal(
            on_add_value=self._handle_modal_add_value
        )
        self.update_value_modal = UpdateEnumValueModal(
            on_update_value=self._handle_update_value
        )

        self._build()

    def _show_code_preview(self) -> None:
        if state.selected_enum:
            with (
                ui.dialog() as modal,
                ui.card().classes("no-shadow border-[1px]"),
            ):
                ui.code(state.selected_enum.class_definition).classes("w-full")
                modal.open()

    def _build(self) -> None:
        with self:
            with ui.row().classes("w-full justify-between items-center"):
                with ui.row().classes("gap-4 items-center"):
                    self.enum_name_display = ui.label().classes("text-lg font-bold")
                    ui.button(
                        icon="visibility",
                        on_click=self._show_code_preview,
                    ).tooltip("Preview Python enum code")

                ui.button(
                    icon="add", on_click=lambda: self.add_value_modal.open()
                ).classes("self-end").tooltip("Add Value")

            with ui.expansion("Values", value=True).classes("w-full"):
                self.table = ui.table(
                    columns=ENUM_COLUMNS,
                    rows=[],
                    row_key="name",
                    selection="single",
                    on_select=lambda e: self._on_select_value(e.selection),
                ).classes("w-full no-shadow border-[1px]")

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button(
                        icon="edit",
                        on_click=lambda: self.update_value_modal.open(
                            state.selected_enum_value,
                        ),
                    ).bind_visibility_from(state, "selected_enum_value")
                    ui.button(
                        icon="delete", on_click=self._handle_delete_enum_value
                    ).bind_visibility_from(state, "selected_enum_value")

    def refresh(self) -> None:
        if state.selected_enum is None:
            return
        self.table.rows = [value.model_dump() for value in state.selected_enum.values]
        self.add_value_modal.close()

    def set_selected_enum(self, enum: CustomEnum) -> None:
        self.refresh()
        self.enum_name_display.text = enum.name
        self.visible = True

    def _on_select_value(self, selection: list[dict[str, Any]]) -> None:
        if not state.selected_enum or not selection:
            return

        name = selection[0].get("name")
        state.selected_enum_value = next(
            (
                enum_value
                for enum_value in state.selected_enum.values
                if enum_value.name == name
            ),
            None,
        )

    def _handle_delete_enum_value(self) -> None:
        if state.selected_enum is None or state.selected_enum_value is None:
            return
        state.selected_enum.values.remove(state.selected_enum_value)
        self.refresh()

    def _enum_value_exists(self, value_name: str) -> bool:
        return any(
            enum_value.name == value_name for enum_value in state.selected_enum.values
        )

    def _handle_modal_add_value(self, *, name: str, value: str) -> None:
        if state.selected_enum is None:
            return

        try:
            validation.raise_if_missing_fields([("Name", name), ("Value", value)])
        except ValueError as exc:
            raise exc

        if self._enum_value_exists(name):
            notify_enum_value_exists(name, state.selected_enum.name)
            return

        try:
            enum_value_input = CustomEnumValue(
                name=name,
                value=value,
            )

            state.selected_enum.values.append(enum_value_input)
            self.refresh()
        except ValidationError as exc:
            notify_validation_error(exc)

    def _handle_update_value(self, *, name: str, value: str) -> None:
        if state.selected_enum is None or state.selected_enum_value is None:
            return

        try:
            validation.raise_if_missing_fields([("Name", name), ("Value", value)])
        except ValueError as exc:
            raise exc

        if self._enum_value_exists(name):
            notify_enum_value_exists(name, state.selected_enum.name)
            return

        try:
            enum_value_input = CustomEnumValue(
                name=name,
                value=value,
            )

            enum_index = state.selected_enum.values.index(state.selected_enum_value)
            state.selected_enum.values[enum_index] = enum_value_input
            self.refresh()
        except ValidationError as exc:
            notify_validation_error(exc)

    def _handle_deselect_enum(self) -> None:
        self.visible = False
