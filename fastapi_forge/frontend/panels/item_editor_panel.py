from nicegui import ui

from fastapi_forge.frontend.panels.enum_editor_panel import EnumEditorPanel
from fastapi_forge.frontend.panels.model_editor_panel import ModelEditorPanel
from fastapi_forge.frontend.state import state


class ItemEditorPanel:
    def __init__(self):
        self._build()
        state.display_item_editor_fn = self._display_item_editor_panel

    def _build(self) -> None:
        self._display_item_editor_panel()

    @ui.refreshable
    def _display_item_editor_panel(self) -> None:
        with ui.column().classes("w-full h-full items-center justify-center mt-4"):
            if state.show_models:
                ModelEditorPanel().classes(
                    "shadow-2xl dark:shadow-none min-w-[700px] max-w-[800px]"
                )
            if state.show_enums:
                EnumEditorPanel().classes(
                    "shadow-2xl dark:shadow-none min-w-[500px] max-w-[600px]"
                )
