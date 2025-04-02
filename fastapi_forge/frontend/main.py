import asyncio
from pathlib import Path

from nicegui import native, ui

from fastapi_forge import project_io as p
from fastapi_forge.forge import build_project
from fastapi_forge.frontend import (
    Header,
    ModelEditorPanel,
    ModelPanel,
    ProjectConfigPanel,
)
from fastapi_forge.frontend.state import state


async def _init_no_ui(project_path: Path) -> None:
    """Initialize project without UI"""
    project_spec = p.ProjectLoader(project_path).load_project_spec()
    await build_project(project_spec)


def setup_ui() -> None:
    """Setup basic UI configuration"""
    ui.add_head_html(
        '<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />',
    )
    ui.button.default_props("round flat dense")
    ui.input.default_props("dense")
    Header()


def load_initial_project(path: Path) -> p.ProjectSpec:
    """Load project specification from file"""
    return p.ProjectLoader(project_path=path).load_project_input()


def create_ui_components() -> None:
    """Create all UI components"""
    with ui.column().classes("w-full h-full items-center justify-center mt-4"):
        ModelEditorPanel().classes(
            "shadow-2xl dark:shadow-none min-w-[700px] max-w-[800px]"
        )

    ModelPanel().classes("shadow-xl dark:shadow-none")
    ProjectConfigPanel().classes("shadow-xl dark:shadow-none")


def run_ui(reload: bool) -> None:
    """Run the NiceGUI application"""
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
    """Main initialization function"""
    base_path = Path(__file__).parent.parent / "example-projects"
    default_path = base_path / "empty-service.yaml"
    example_path = base_path / "game_zone.yaml"

    path = example_path if use_example else yaml_path if yaml_path else default_path

    if no_ui:
        asyncio.run(_init_no_ui(path))
        return

    setup_ui()

    if use_example or yaml_path:
        initial_project = load_initial_project(path)
        state.initialize_from_project(initial_project)

    create_ui_components()
    run_ui(reload)


if __name__ in {"__main__", "__mp_main__"}:
    init(reload=True, use_example=False)
