from fastapi_forge.forge import build_project
from fastapi_forge import project_io as p
from fastapi_forge import dtos as m
from fastapi_forge.gui import (
    Header,
    ModelCreate,
    ModelRow,
    ModelPanel,
    ModelEditorPanel,
)
from pathlib import Path
from nicegui import ui, native
import asyncio


async def _init_no_ui(project_path: Path) -> None:
    project_spec = p.ProjectLoader(project_path).load_project_spec()
    await build_project(project_spec)


def setup_ui() -> None:
    ui.add_head_html(
        '<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />'
    )
    ui.button.default_props("round flat dense")
    ui.input.default_props("dense")
    Header()


def load_initial_project(
    path: Path,
) -> tuple[m.ProjectSpec | None, list[m.Model] | None]:
    initial_project = None
    initial_models = None
    if path:
        initial_project = p.ProjectLoader(project_path=path).load_project_input()
        initial_models = initial_project.models
    return initial_project, initial_models


def create_ui_components(
    initial_project: p.ProjectSpec | None,
    initial_models: list[p.Model] | None,
) -> None:

    with ui.column().classes("w-full h-full items-center justify-center mt-4"):
        ModelEditorPanel().classes("no-shadow min-w-[600px]")

    ModelPanel(
        initial_models=initial_models,
        # on_select_model=model_editor_card.set_selected_model,
    )
    # project_config_panel = ProjectConfigPanel(
    #    model_panel=model_panel,
    #    initial_project=initial_project,
    # )


#
# model_panel.project_config_panel = project_config_panel
# model_editor_card.model_panel = model_panel


def run_ui(reload: bool) -> None:
    ui.run(
        reload=reload,
        title="FastAPI Forge",
        port=native.find_open_port(8777, 8999),
    )


def init(
    reload: bool = False,
    use_example: bool = False,
    no_ui: bool = False,
    yaml_path: Path | None = None,
) -> None:
    base_path = Path(__file__).parent / "example-projects"
    default_path = base_path / "empty-service.yaml"
    example_path = base_path / "game_zone.yaml"

    path = example_path if use_example else yaml_path if yaml_path else default_path

    if no_ui:
        asyncio.run(_init_no_ui(path))
        return

    setup_ui()

    initial_project = None
    initial_models = None
    if use_example or yaml_path:
        initial_project, initial_models = load_initial_project(path)

    create_ui_components(initial_project, initial_models)
    run_ui(reload)


if __name__ in {"__main__", "__mp_main__"}:
    init(reload=True, use_example=False)
