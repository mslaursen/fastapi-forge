from nicegui import ui
from fastapi_forge import dtos as m
from fastapi_forge.gui.state import state
import typing as t
from fastapi_forge.gui import ModelCreate, ModelRow
from fastapi_forge import project_io as p
import os
from pydantic import ValidationError
from fastapi_forge.gui.notifications import notify_validation_error


class ModelPanel(ui.left_drawer):

    def __init__(
        self,
        initial_models: list[m.Model] | None = None,
    ):
        super().__init__(value=True, elevated=False, bottom_corner=True)
        self.classes("border-right[1px]")

        state.render_models_fn = self._render_models

        self._build()

    def _build(self) -> None:
        self.clear()
        with self:
            with ui.column().classes("items-align content-start w-full"):
                ModelCreate()
                self._render_models()

                ui.button(
                    "Export",
                    on_click=self._export_project,
                    icon="file_download",
                ).classes("w-full py-3 text-lg font-bold").tooltip(
                    "Generates a YAML file containing the project configuration."
                )

    async def _export_project(self) -> None:
        """Export the project configuration to a YAML file."""
        try:
            project_input = state.get_project_spec()
            exporter = p.ProjectExporter(project_input)
            await exporter.export_project()
            ui.notify(
                "Project configuration exported to "
                f"{os.path.join(os.getcwd(), project_input.project_name)}.yaml",
                type="positive",
            )
        except ValidationError as e:
            notify_validation_error(e)
        except FileNotFoundError as e:
            ui.notify(f"File not found: {e}", type="negative")
        except Exception as e:
            ui.notify(f"An unexpected error occurred: {e}", type="negative")

    def _render_models(self) -> None:
        if hasattr(self, "model_list"):
            self.model_list.clear()
        else:
            self.model_list = ui.column().classes("items-align content-start w-full")

        with self.model_list:
            for model in state.models:
                is_auth_user = model.name == "auth_user"
                color = "text-green-500" if is_auth_user else None
                ModelRow(
                    model,
                    color=color,
                )
