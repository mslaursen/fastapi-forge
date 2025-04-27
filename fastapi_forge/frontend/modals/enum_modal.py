from abc import ABC, abstractmethod
from collections.abc import Callable

from nicegui import ui

from fastapi_forge.frontend.notifications import notify_value_error
from fastapi_forge.frontend.state import state
from fastapi_forge.schemas import CustomEnumValue


class BaseEnumValueModal(ui.dialog, ABC):
    title: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()

    @abstractmethod
    def _build_action_buttons(self) -> None:
        pass

    def _build(self) -> None:
        with self, ui.card().classes("w-full max-w-md no-shadow rounded-lg"):
            with ui.row().classes("w-full justify-between items-center p-4 border-b"):
                ui.label(self.title).classes("text-xl font-semibold")

            with (
                ui.column().classes("w-full p-6 space-y-4"),
                ui.grid(columns=2).classes("w-full gap-4"),
            ):
                self.value_name = (
                    ui.input(label="Name").props("outlined dense").classes("w-full")
                )
                self.value_value = (
                    ui.input(label="Value").props("outlined dense").classes("w-full")
                ).tooltip(
                    "Set to auto(), or any string value without including quotes."
                )

            with ui.row().classes("w-full justify-end p-4 border-t gap-2"):
                self._build_action_buttons()

    def reset(self) -> None:
        self.value_name.value = ""
        self.value_value.value = ""


class AddEnumValueModal(BaseEnumValueModal):
    title = "Add Enum Value"

    def __init__(self, on_add_value: Callable):
        super().__init__()
        self.on_add_value = on_add_value

    def _build_action_buttons(self) -> None:
        ui.button("Cancel", on_click=self.close)
        ui.button(
            self.title,
            on_click=self._handle_add,
        )

    def _handle_add(self) -> None:
        try:
            self.on_add_value(
                name=self.value_name.value,
                value=self.value_value.value,
            )
            self.close()
        except ValueError as exc:
            notify_value_error(exc)
            return


class UpdateEnumValueModal(BaseEnumValueModal):
    title = "Update Enum Value"

    def __init__(self, on_update_value: Callable):
        super().__init__()
        self.on_update_value = on_update_value

    def _build_action_buttons(self) -> None:
        ui.button("Cancel", on_click=self.close)
        ui.button(
            self.title,
            on_click=self._handle_update,
        )

    def _handle_update(self) -> None:
        if not state.selected_enum_value:
            return
        try:
            self.on_update_value(
                name=self.value_name.value,
                value=self.value_value.value,
            )
            self.close()
        except ValueError as exc:
            notify_value_error(exc)
            return

    def _set_value(self, enum_value: CustomEnumValue) -> None:
        state.selected_enum_value = enum_value
        if enum_value:
            self.value_name.value = enum_value.name
            self.value_value.value = enum_value.value

    def open(self, enum_value: CustomEnumValue | None = None) -> None:
        if enum_value:
            self._set_value(enum_value)
        super().open()
