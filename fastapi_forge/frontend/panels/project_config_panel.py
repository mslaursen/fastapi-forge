from pathlib import Path

from nicegui import ui
from nicegui.events import ValueChangeEventArguments
from pydantic import ValidationError

from fastapi_forge.dtos import (
    Model,
    ModelField,
    ModelFieldMetadata,
    ModelMetadata,
)
from fastapi_forge.enums import FieldDataTypeEnum
from fastapi_forge.forge import build_project
from fastapi_forge.frontend.constants import DEFAULT_AUTH_USER_FIELDS
from fastapi_forge.frontend.notifications import notify_validation_error
from fastapi_forge.frontend.state import state


class ProjectConfigPanel(ui.right_drawer):
    def __init__(self):
        super().__init__(value=True, elevated=False, bottom_corner=True)
        self._build()
        self._bind_state_to_ui()
        self._update_taskiq_state()

    def _build(self) -> None:
        with (
            self,
            ui.column().classes(
                "items-align content-start w-full gap-4",
            ) as self.column,
        ):
            with ui.column().classes("w-full gap-2"):
                ui.label("Project Name").classes("text-lg font-bold")
                self.project_name = ui.input(
                    placeholder="Project Name",
                    value=state.project_name,
                ).classes("w-full")

            with ui.column().classes("w-full gap-2"):
                ui.label("Database").classes("text-lg font-bold")
                self.use_postgres = ui.checkbox(
                    "Postgres",
                    value=state.use_postgres,
                ).classes("w-full")

                self.use_mysql = (
                    ui.checkbox("MySQL")
                    .classes("w-full")
                    .tooltip("Coming soon!")
                    .set_enabled(False)
                )

            with ui.column().classes("w-full gap-2"):
                ui.label("Migrations").classes("text-lg font-bold")
                self.use_alembic = (
                    ui.checkbox("Alembic", value=state.use_alembic)
                    .classes("w-full")
                    .bind_enabled_from(self.use_postgres, "value")
                )

            with ui.column().classes("w-full gap-2"):
                ui.label("Authentication").classes("text-lg font-bold")
                self.use_builtin_auth = (
                    ui.checkbox(
                        "JWT Auth",
                        value=state.use_builtin_auth,
                        on_change=self._handle_builtin_auth_change,
                    )
                    .tooltip(
                        "Authentication is built in the API itself, using JWT.",
                    )
                    .classes("w-full")
                    .bind_enabled_from(self.use_postgres, "value")
                )

            with ui.column().classes("w-full gap-2"):
                ui.label("Messaging").classes("text-lg font-bold")
                self.use_rabbitmq = ui.checkbox(
                    "RabbitMQ",
                    value=state.use_rabbitmq,
                    on_change=self._update_taskiq_state,
                ).classes("w-full")

            with ui.column().classes("w-full gap-2"):
                ui.label("Task Queues").classes("text-lg font-bold")
                self.use_taskiq = ui.checkbox(
                    "Taskiq",
                    value=state.use_taskiq,
                    on_change=self._update_taskiq_state,
                ).classes("w-full")
                self.use_celery = (
                    ui.checkbox("Celery")
                    .classes("w-full")
                    .tooltip("Coming soon!")
                    .set_enabled(False)
                )

            with ui.column().classes("w-full gap-2"):
                ui.label("Caching").classes("text-lg font-bold")
                self.use_redis = ui.checkbox(
                    "Redis",
                    value=state.use_redis,
                    on_change=self._update_taskiq_state,
                ).classes("w-full")

            with ui.column().classes("w-full gap-2"):
                ui.label("Metrics").classes("text-lg font-bold")
                self.use_prometheus = (
                    ui.checkbox("Prometheus")
                    .classes("w-full")
                    .tooltip("Coming soon!")
                    .set_enabled(False)
                )

            with ui.column().classes("w-full gap-2"):
                ui.label("Object Storage").classes("text-lg font-bold")
                self.use_elasticsearch = (
                    ui.checkbox("S3")
                    .classes("w-full")
                    .tooltip("Coming soon!")
                    .set_enabled(False)
                )

            with ui.column().classes("w-full gap-2"):
                self.loading_spinner = ui.spinner(size="lg").classes(
                    "hidden mt-4 self-center",
                )
                self.create_button = ui.button(
                    "Generate",
                    icon="rocket",
                    on_click=self._create_project,
                ).classes("w-full py-3 text-lg font-bold mt-4")

    def _bind_state_to_ui(self) -> None:
        """Bind UI elements to state variables"""
        self.project_name.bind_value_to(state, "project_name")
        self.use_postgres.bind_value_to(state, "use_postgres")
        self.use_alembic.bind_value_to(state, "use_alembic")
        self.use_builtin_auth.bind_value_to(state, "use_builtin_auth")
        self.use_rabbitmq.bind_value_to(state, "use_rabbitmq").on(
            "change", self._update_taskiq_state
        )
        self.use_redis.bind_value_to(state, "use_redis").on(
            "change", self._update_taskiq_state
        )
        self.use_taskiq.bind_value_to(state, "use_taskiq")

    def _update_taskiq_state(self, *_) -> None:
        """Enable or disable Taskiq based on Redis and RabbitMQ."""
        self.use_taskiq.set_enabled(self.use_redis.value and self.use_rabbitmq.value)
        if (
            not (self.use_redis.value and self.use_rabbitmq.value)
            and self.use_taskiq.value
        ):
            self.use_taskiq.value = False
            state.use_taskiq = False

    def _handle_builtin_auth_change(self, event: ValueChangeEventArguments) -> None:
        """Handle JWT Auth checkbox changes"""
        enabled = event.value
        state.use_builtin_auth = enabled

        if enabled:
            if any(model.name == "auth_user" for model in state.models):
                ui.notify("The 'auth_user' model already exists.", type="negative")
                self.use_builtin_auth.value = False
                state.use_builtin_auth = False
                return

            try:
                auth_user_model = Model(
                    name="auth_user",
                    metadata=ModelMetadata(is_auth_model=True),
                    fields=[
                        ModelField(
                            name="id",
                            type=FieldDataTypeEnum.UUID,
                            primary_key=True,
                            unique=True,
                            index=True,
                        ),
                        *DEFAULT_AUTH_USER_FIELDS,
                        ModelField(
                            name="created_at",
                            type=FieldDataTypeEnum.DATETIME,
                            default_value="datetime.now(timezone.utc)",
                            metadata=ModelFieldMetadata(is_created_at_timestamp=True),
                        ),
                        ModelField(
                            name="updated_at",
                            type=FieldDataTypeEnum.DATETIME,
                            default_value="datetime.now(timezone.utc)",
                            extra_kwargs={"onupdate": "datetime.now(timezone.utc)"},
                            metadata=ModelFieldMetadata(is_updated_at_timestamp=True),
                        ),
                    ],
                )
                state.models.append(auth_user_model)
                if state.render_models_fn:
                    state.render_models_fn()
                ui.notify("The 'auth_user' model has been created.", type="positive")
            except ValidationError as exc:
                notify_validation_error(exc)
        else:
            state.models = [
                model for model in state.models if model.name != "auth_user"
            ]
            if state.render_models_fn:
                state.render_models_fn()
            ui.notify("The 'auth_user' model has been deleted.", type="positive")

    async def _warn_overwrite(self) -> bool:
        """Show a confirmation dialog if the project already exists."""
        dialog = ui.dialog()
        with dialog, ui.card().classes("w-full max-w-md p-6 text-center"):
            ui.icon("warning", color="orange-500").classes("text-4xl self-center")
            ui.markdown(
                f"Project '{state.project_name}' already exists!\n\n"
                "This will **permanently overwrite** the existing project directory.\n"
                "Are you sure you want to continue?"
            ).classes("text-center")

            with ui.row().classes("w-full justify-center gap-4 mt-4"):
                ui.button("Cancel", color="primary", on_click=dialog.close)
                ui.button(
                    "Overwrite", color="negative", on_click=lambda: dialog.submit(True)
                )

        return await dialog

    async def _create_project(self) -> None:
        """Generate the project based on the current state."""
        project_path = Path(state.project_name)

        if project_path.exists():
            try:
                overwrite = await self._warn_overwrite()
                if not overwrite:
                    ui.notify("Project generation cancelled.", type="warning")
                    return
            except Exception as e:
                ui.notify(f"Error displaying confirmation: {e}", type="negative")
                return

        self.create_button.classes("hidden")
        self.loading_spinner.classes(remove="hidden")
        ongoing_notification = ui.notification("Generating project...")

        try:
            if not state.models:
                ui.notify("No models to generate!", type="negative")
                return

            state.project_name = self.project_name.value
            state.use_postgres = self.use_postgres.value
            state.use_alembic = self.use_alembic.value
            state.use_builtin_auth = self.use_builtin_auth.value
            state.use_redis = self.use_redis.value
            state.use_rabbitmq = self.use_rabbitmq.value
            state.use_taskiq = self.use_taskiq.value

            project_spec = state.get_project_spec()
            await build_project(project_spec)

            ui.notify(
                "Project successfully generated at: "
                f"{Path.cwd() / project_spec.project_name}",
                type="positive",
            )

        except ValidationError as exc:
            notify_validation_error(exc)
        except Exception as exc:
            ui.notify(f"Error creating Project: {exc}", type="negative")
        finally:
            self.create_button.classes(remove="hidden")
            self.loading_spinner.classes("hidden")
            ongoing_notification.dismiss()
