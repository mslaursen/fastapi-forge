from nicegui import ui
import json
import os
from .forge import forge_project
from .dtos import ProjectSpec, Model


def init() -> None:
    ui.label("FastAPI Forge")

    path = os.path.join(
        os.getcwd(),
        "fastapi_forge",
        "default_project_models.json",
    )

    with open(path) as file:
        default_project_config = json.load(file)

    with ui.card().classes("w-96"):
        ui.label("Create a New Project").classes("text-2xl")
        project_name = ui.input(
            "Project Name", placeholder="Enter project name", value="restaurant_service"
        ).classes("w-full")
        use_postgres = ui.checkbox("Use PostgreSQL", value=True)
        create_daos = ui.checkbox("Create DAOs", value=True)
        create_routes = ui.checkbox("Create Routes", value=True)
        create_tests = ui.checkbox("Create Tests", value=True)

        models = ui.textarea(
            "Models (JSON)",
            placeholder="Enter models as JSON",
            value=json.dumps(default_project_config, indent=4),
        ).classes("w-full")

    def on_submit() -> None:
        ui.notify(models.value)

        spec = ProjectSpec(
            project_name=project_name.value,
            use_postgres=use_postgres.value,
            create_daos=create_daos.value,
            create_routes=create_routes.value,
            create_tests=create_tests.value,
            models=[Model(**model) for model in json.loads(models.value)],
        )

        forge_project(spec)

    ui.button("Submit", on_click=on_submit).classes("mt-4")

    ui.run()
