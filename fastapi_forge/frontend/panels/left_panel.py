from pathlib import Path

from nicegui import ui
from pydantic import ValidationError

from fastapi_forge.frontend import EnumRow, ModelCreate, ModelRow
from fastapi_forge.frontend.components.item_create import EnumCreate
from fastapi_forge.frontend.constants import (
    SELECTED_ENUM_TEXT_COLOR,
    SELECTED_MODEL_TEXT_COLOR,
)
from fastapi_forge.frontend.notifications import notify_validation_error
from fastapi_forge.frontend.state import state
from fastapi_forge.project_io import ProjectExporter


class NavigationTabs(ui.row):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self) -> None:
        with self.classes("w-full bg-gray-100 dark:bg-gray-800 rounded-lg p-1"):
            ui.button(
                "Models",
                on_click=lambda: state.switch_show(show_models=True),
            ).classes("flex-grow transition-all duration-200 py-2").props(
                "unelevated"
            ).style("font-weight: 500; border-radius: 0.375rem;")
            ui.button(
                "Enums",
                on_click=lambda: state.switch_show(show_enums=True),
            ).classes("flex-grow transition-all duration-200 py-2").props(
                "unelevated"
            ).style("font-weight: 500; border-radius: 0.375rem;")


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
            project_input = state.get_project_spec()
            exporter = ProjectExporter(project_input)
            await exporter.export_project()
            ui.notify(
                "Project configuration exported to "
                f"{Path.cwd() / project_input.project_name}.yaml",
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

        state.render_models_fn = self._render_content
        state.render_enums_fn = self._render_content
        state.render_content_fn = self._render_content

        self._build()

    def _build(self) -> None:
        self.clear()
        with self, ui.column().classes("items-align content-start w-full"):
            NavigationTabs()

            with ui.column().bind_visibility_from(state, "show_models"):
                ModelCreate()
            with ui.column().bind_visibility_from(state, "show_enums"):
                EnumCreate()

            self._render_content()

            ExportButton()

    @ui.refreshable
    def _render_content(self) -> None:
        self.content_list = ui.column().classes("items-align content-start w-full")

        if state.show_models:
            self._render_models_list()
        elif state.show_enums:
            self._render_enums_list()

    def _render_models_list(self) -> None:
        print("model")
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
        print("enum")
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
