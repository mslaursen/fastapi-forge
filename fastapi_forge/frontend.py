from nicegui import ui
import json
from .forge import forge_project
from .dtos import ProjectSpec, Model, ModelField, ModelRelationship


def init() -> None:
    created_models: list[Model] = []
    selected_model: Model | None = None

    # Sidebar for displaying created models
    def update_sidebar() -> None:
        sidebar.clear()
        with sidebar:
            ui.label("Created Models")

            def select_model(model: Model) -> None:
                nonlocal selected_model
                selected_model = model

                print(json.dumps(selected_model.dict(), indent=2))

            def delete_model(model: Model) -> None:
                created_models.remove(model)
                update_sidebar()

            for model in created_models:
                with ui.row():
                    ui.label(model.name).classes(
                        "text-lg cursor-pointer hover:bg-blue-200"
                    ).on("click", lambda m=model: select_model(m))
                    ui.button(
                        icon="delete", on_click=lambda m=model: delete_model(m)
                    ).classes("ml-auto")

        # print(json.dumps(selected_model.dict(), indent=2) if selected_model else None)

    # Left sidebar for models
    with ui.left_drawer() as sidebar:
        update_sidebar()

    with ui.right_drawer():
        project_name = ui.input("Project name")
        use_postgres = ui.checkbox("Use Postgres")
        create_daos = ui.checkbox("Create DAOs")
        create_routes = ui.checkbox("Create routes")
        create_tests = ui.checkbox("Create tests")

        def create_project() -> None:
            project_spec = ProjectSpec(
                project_name=project_name.value,
                models=created_models,
                use_postgres=use_postgres.value,
                create_daos=create_daos.value,
                create_routes=create_routes.value,
                create_tests=create_tests.value,
            )
            print(json.dumps(project_spec.dict(), indent=2))
            # forge_project(project_spec)

        ui.button("Forge project", on_click=create_project)

    

    # Main content
    with ui.column():
        ui.label("FastAPI Forge")

        with ui.card():
            ui.label("Create a new model")

            model_name = ui.input("Model name")

            def create_model() -> None:
                ui.notify("Model created", duration=2)
                if not model_name.value:
                    return
                created_models.append(
                    Model(name=model_name.value, fields=[], relationships=[])
                )
                update_sidebar()

            ui.button("Create", on_click=create_model)

            name = ui.input("Field name")
            primary_key = ui.checkbox("Primary key")
            foreign_key = ui.checkbox("Foreign key")
            nullable = ui.checkbox("Nullable")

            type = ui.select(
                ["UUID", "String", "Integer", "Float", "Boolean"], value="UUID"
            )

            def add_field() -> None:
                

    ui.run(reload=True)
