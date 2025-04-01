from pathlib import Path

from nicegui import ui
from pydantic import ValidationError

from fastapi_forge.frontend import ModelCreate, ModelRow
from fastapi_forge.frontend.constants import SELECTED_MODEL_TEXT_COLOR
from fastapi_forge.frontend.notifications import notify_validation_error
from fastapi_forge.frontend.state import state
from fastapi_forge.project_io import ProjectExporter


class ModelPanel(ui.left_drawer):
    def __init__(self):
        super().__init__(value=True, elevated=False, bottom_corner=True)

        state.render_models_fn = self._render_models

        self._build()

    def _build(self) -> None:
        self.clear()
        with self, ui.column().classes("items-align content-start w-full"):
            ModelCreate()
            self._render_models()

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

    def _render_models(self) -> None:
        if hasattr(self, "model_list"):
            self.model_list.clear()
        else:
            self.model_list = ui.column().classes("items-align content-start w-full")

        with self.model_list:
            for model in state.models:
                ModelRow(
                    model,
                    color=(
                        SELECTED_MODEL_TEXT_COLOR
                        if model == state.selected_model
                        else None
                    ),
                )
