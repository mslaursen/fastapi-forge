from nicegui import ui
import json
from fastapi_forge.forge import build_project
from fastapi_forge.dtos import ProjectSpec, Model
from fastapi_forge.enums import FieldDataType, RelationshipType


test_models = [
    {
        "name": "AppUser",
        "fields": [
            {
                "name": "id",
                "type": FieldDataType.UUID,
                "primary_key": True,
                "unique": True,
            },
            {
                "name": "email",
                "type": FieldDataType.STRING,
                "unique": True,
                "nullable": False,
            },
            {
                "name": "password",
                "type": FieldDataType.STRING,
                "nullable": False,
            },
        ],
        "relationships": [],
    },
    {
        "name": "Restaurant",
        "fields": [
            {
                "name": "id",
                "type": FieldDataType.UUID,
                "primary_key": True,
                "unique": True,
            },
            {
                "name": "name",
                "type": FieldDataType.STRING,
                "nullable": False,
            },
            {
                "name": "address",
                "type": FieldDataType.STRING,
                "nullable": False,
            },
            {
                "name": "phone_number",
                "type": FieldDataType.STRING,
                "nullable": True,
            },
        ],
        "relationships": [],
    },
    {
        "name": "Table",
        "fields": [
            {
                "name": "id",
                "type": FieldDataType.UUID,
                "primary_key": True,
                "unique": True,
            },
            {
                "name": "number",
                "type": FieldDataType.INTEGER,
                "nullable": False,
            },
            {
                "name": "seats",
                "type": FieldDataType.INTEGER,
                "nullable": False,
            },
            {
                "name": "restaurant_id",
                "type": FieldDataType.UUID,
                "foreign_key": "Restaurant.id",
                "nullable": False,
            },
        ],
        "relationships": [
            {
                "type": RelationshipType.MANY_TO_ONE,
                "target": "Restaurant",
            }
        ],
    },
    {
        "name": "Reservation",
        "fields": [
            {
                "name": "id",
                "type": FieldDataType.UUID,
                "primary_key": True,
                "unique": True,  # Added missing unique constraint
            },
            {
                "name": "app_user_id",
                "type": FieldDataType.UUID,
                "foreign_key": "AppUser.id",
                "nullable": False,
            },
            {
                "name": "restaurant_id",
                "type": FieldDataType.UUID,
                "foreign_key": "Restaurant.id",
                "nullable": False,
            },
            {
                "name": "table_id",
                "type": FieldDataType.UUID,
                "foreign_key": "Table.id",
                "nullable": False,
            },
            {
                "name": "reservation_time",
                "type": FieldDataType.DATETIME,
                "nullable": False,
            },
        ],
        "relationships": [
            {
                "type": RelationshipType.MANY_TO_ONE,
                "target": "AppUser",
            },
            {
                "type": RelationshipType.MANY_TO_ONE,
                "target": "Restaurant",
            },
            {
                "type": RelationshipType.MANY_TO_ONE,
                "target": "Table",
            },
        ],
    },
]


def init(reload: bool = False) -> None:
    ui.label("FastAPI Forge")

    with ui.card().classes("w-96"):
        ui.label("Create a New Project").classes("text-2xl")
        project_name = ui.input(
            "Project Name",
            placeholder="Enter project name",
            value="restaurant_service",
        ).classes("w-full")
        use_postgres = ui.checkbox("Use PostgreSQL", value=True)
        use_alembic = ui.checkbox("Use Alembic", value=True)
        use_builtin_auth = ui.checkbox("Use Builtin Auth", value=True)
        builtin_jwt_token_expire = ui.input(
            "Builtin JWT Token Expire",
            placeholder="Enter JWT Token Expiration",
            value=15,
        ).classes("w-full")
        create_routes = ui.checkbox("Create Routes", value=True)
        create_tests = ui.checkbox("Create Tests", value=True)

        models = ui.textarea(
            "Models (JSON)",
            placeholder="Enter models as JSON",
            value=json.dumps(test_models, indent=4),
        ).classes("w-full")

    def on_submit() -> None:
        ui.notify("Creating project...")

        spec = ProjectSpec(
            project_name=project_name.value,
            use_postgres=use_postgres.value,
            use_alembic=use_alembic.value,
            use_builtin_auth=use_builtin_auth.value,
            builtin_jwt_token_expire=builtin_jwt_token_expire.value,
            create_routes=create_routes.value,
            create_tests=create_tests.value,
            models=[Model(**model) for model in json.loads(models.value)],
        )

        try:
            build_project(spec)
        except Exception:
            ui.notify(f"Failed to create project: {spec.project_name}")
            return

        ui.notify(f"Project created: {spec.project_name}")

    ui.button("Submit", on_click=on_submit).classes("mt-4")

    ui.run(reload=reload)


if __name__ in {"__main__", "__mp_main__"}:
    init(reload=True)
