import asyncio

from nicegui import native, ui

from fastapi_forge.dtos import (
    CustomEnum,
    CustomEnumValue,
    Model,
    ModelField,
    ProjectSpec,
)
from fastapi_forge.enums import FieldDataTypeEnum
from fastapi_forge.forge import build_project
from fastapi_forge.frontend import (
    Header,
    LeftPanel,
    ProjectConfigPanel,
)
from fastapi_forge.frontend.panels.item_editor_panel import ItemEditorPanel
from fastapi_forge.frontend.state import state


def setup_ui() -> None:
    """Setup basic UI configuration"""
    ui.add_head_html(
        '<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />',
    )
    ui.button.default_props("round flat dense")
    ui.input.default_props("dense")
    Header()


def create_ui_components() -> None:
    """Create all UI components"""
    ItemEditorPanel()

    LeftPanel().classes("shadow-xl dark:shadow-none")
    ProjectConfigPanel().classes("shadow-xl dark:shadow-none")


def run_ui(reload: bool) -> None:
    """Run the NiceGUI application"""
    ui.run(
        reload=reload,
        title="FastAPI Forge",
        port=native.find_open_port(8777, 8999),
    )


def init(
    *,
    reload: bool = False,
    no_ui: bool = False,
    project_spec: ProjectSpec | None = None,
) -> None:
    if project_spec:
        if no_ui:
            asyncio.run(build_project(project_spec))
            return

        state.initialize_from_project(project_spec)

    setup_ui()
    create_ui_components()
    run_ui(reload)


if __name__ in {"__main__", "__mp_main__"}:
    project_spec = ProjectSpec(
        project_name="reload",
        models=[
            Model(
                name="test_model",
                fields=[
                    ModelField(
                        name="id",
                        primary_key=True,
                        type=FieldDataTypeEnum.UUID,
                    ),
                ],
            ),
        ],
        custom_enums=[
            CustomEnum(
                name="MyEnum",
                values=[
                    CustomEnumValue(
                        name="FOO",
                        value="auto()",
                    ),
                ],
            )
        ],
    )
    init(reload=True, project_spec=project_spec)
