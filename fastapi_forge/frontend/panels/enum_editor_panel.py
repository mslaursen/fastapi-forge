from nicegui import ui

from fastapi_forge.dtos import CustomEnum
from fastapi_forge.frontend.constants import ENUM_COLUMNS
from fastapi_forge.frontend.state import state


class EnumEditorPanel(ui.card):
    def __init__(self):
        super().__init__()
        self.visible = False

        state.select_enum_fn = self.set_selected_enum
        # state.deselect_enum_fn = self.deselect_enum
        # state.render_enum_fn = self.refresh

        # self.add_value_modal = AddEnumValueModal(
        #     on_add_value=self._handle_modal_add_value
        # )
        # self.update_value_modal = UpdateEnumValueModal(
        #     on_update_value=self._handle_update_value
        # )

        self._build()

    def _show_code_preview(self) -> None:
        if state.selected_enum:
            with (
                ui.dialog() as modal,
                ui.card().classes("no-shadow border-[1px]"),
            ):
                code = state.selected_enum.class_definition
                ui.code(code).classes("w-full")
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

                with ui.button(icon="add").classes("self-end"), ui.menu():
                    ui.menu_item(
                        "Value",
                        # on_click=lambda: self.add_value_modal.open(),
                    )

            with ui.expansion("Values", value=True).classes("w-full"):
                self.table = ui.table(
                    columns=ENUM_COLUMNS,
                    rows=[],
                    row_key="name",
                    selection="single",
                    # on_select=lambda e: self._on_select_value(e.selection),
                ).classes("w-full no-shadow border-[1px]")

    def set_selected_enum(self, enum: CustomEnum) -> None:
        self.enum_name_display.text = enum.name
        self.visible = True
