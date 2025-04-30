from pathlib import Path

from nicegui import ui
from pydantic import ValidationError

from fastapi_forge.frontend.components.item_create import EnumCreate, ModelCreate
from fastapi_forge.frontend.components.item_row import EnumRow, ModelRow
from fastapi_forge.frontend.constants import (
    SELECTED_ENUM_TEXT_COLOR,
    SELECTED_MODEL_TEXT_COLOR,
)
from fastapi_forge.frontend.notifications import notify_validation_error
from fastapi_forge.frontend.state import state
from fastapi_forge.project_io import create_yaml_project_exporter


class NavigationTabs(ui.row):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self) -> None:
        with self.classes("w-full"):
            self.toggle = (
                ui.toggle(
                    {"models": "Models", "enums": "Enums"},
                    value="models",
                    on_change=self._on_toggle_change,
                )
                .props("rounded spread")
                .classes("w-full")
            )

    def _on_toggle_change(self) -> None:
        if self.toggle.value == "models":
            state.switch_item_editor(show_models=True)
        else:
            state.switch_item_editor(show_enums=True)


class ExportButton:
    def __init__(self):
        self._build()

    def _build(self) -> None:
        ui.button(
            "Export",
            on_click=self._export_project,
            icon="file_download",
        ).classes("w-full py-3 text-lg font-bold").tooltip(
            "Generates a YAML file containing the project configuration.",
        )

    async def _export_project(self) -> None:
        """Export the project configuration to a YAML file."""
        try:
            spec = state.get_project_spec()
            exporter = create_yaml_project_exporter()
            await exporter.export_project(spec)
            ui.notify(
                "Project configuration exported to "
                f"{Path.cwd() / spec.project_name}.yaml",
                type="positive",
            )
        except ValidationError as exc:
            notify_validation_error(exc)
        except FileNotFoundError as exc:
            ui.notify(f"File not found: {exc}", type="negative")
        except Exception as exc:
            ui.notify(f"An unexpected error occurred: {exc}", type="negative")


class LeftPanel(ui.left_drawer):
    def __init__(self):
        super().__init__(value=True, elevated=False, bottom_corner=True)

        state.render_content_fn = self._render_content

        self._build()

    def _build(self) -> None:
        self.clear()
        with self, ui.column().classes("items-align content-start w-full"):
            NavigationTabs()

            self._render_content()

            ExportButton()

    @ui.refreshable
    def _render_content(self) -> None:
        with ui.column():
            EnumCreate() if state.show_enums else ModelCreate()

        self.content_list = ui.column().classes("items-align content-start w-full")

        if state.show_models:
            self._render_models_list()
        elif state.show_enums:
            self._render_enums_list()

    def _render_models_list(self) -> None:
        with self.content_list:
            for model in state.models:
                ModelRow(
                    model,
                    color=(
                        SELECTED_MODEL_TEXT_COLOR
                        if model == state.selected_model
                        else None
                    ),
                    icon="security" if model.metadata.is_auth_model else None,
                )

    def _render_enums_list(self) -> None:
        with self.content_list:
            for custom_enum in state.custom_enums:
                EnumRow(
                    custom_enum,
                    color=(
                        SELECTED_ENUM_TEXT_COLOR
                        if custom_enum == state.selected_enum
                        else None
                    ),
                )
