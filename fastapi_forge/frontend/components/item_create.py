from collections.abc import Callable

from nicegui import ui

from fastapi_forge.frontend.state import state


class _RowCreate(ui.row):
    def __init__(
        self,
        *,
        input_placeholder: str,
        input_tooltip: str,
        button_tooltip: str,
        on_add_item: Callable[[str], None],
    ):
        super().__init__(wrap=False)
        self.input_placeholder = input_placeholder
        self.input_tooltip = input_tooltip
        self.button_tooltip = button_tooltip
        self.on_add_item = on_add_item

        self._build()

    def _build(self) -> None:
        with self.classes("w-full flex items-center justify-between"):
            self.item_input = (
                ui.input(placeholder=self.input_placeholder)
                .classes("self-center")
                .tooltip(
                    self.input_tooltip,
                )
            )
            self.add_button = (
                ui.button(icon="add", on_click=self._add_item)
                .classes("self-center")
                .tooltip(self.button_tooltip)
            )

    def _add_item(self) -> None:
        if not self.item_input.value:
            return
        value: str = self.item_input.value
        item_name = value.strip()
        if item_name:
            self.on_add_item(item_name)
            self.item_input.value = ""


class ModelCreate(_RowCreate):
    def __init__(self):
        super().__init__(
            input_placeholder="Model name",
            input_tooltip="Model names should be singular and snake_case (e.g. 'auth_user').",
            button_tooltip="Add Model",
            on_add_item=state.add_model,
        )


class EnumCreate(_RowCreate):
    def __init__(self):
        super().__init__(
            input_placeholder="Enum name",
            input_tooltip="Enums can be used as data types for model fields.",
            button_tooltip="Add Enum",
            on_add_item=state.add_enum,
        )
