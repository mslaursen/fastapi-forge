from nicegui import ui

from fastapi_forge.dtos import Model
from fastapi_forge.frontend.state import state


class ModelRow(ui.row):
    def __init__(
        self,
        model: Model,
        color: str | None = None,
    ):
        super().__init__(wrap=False)
        self.model = model
        self.is_editing = False
        self.color = color
        self._build()

    def _build(self) -> None:
        with self.classes("w-full flex items-center justify-between cursor-pointer"):
            self.name_label = ui.label(text=self.model.name).classes("self-center")
            if self.color:
                self.name_label.classes(add=self.color)
            self.name_input = (
                ui.input(value=self.model.name)
                .classes("self-center")
                .bind_visibility_from(self, "is_editing")
            )
            self.name_label.bind_visibility_from(self, "is_editing", lambda x: not x)

            self.on("click", lambda: state.select_model(self.model))

            with ui.row().classes("gap-2"):
                self.edit_button = ui.button(
                    icon="edit",
                    on_click=self._toggle_edit,
                ).bind_visibility_from(self, "is_editing", lambda x: not x)
                self.save_button = ui.button(
                    icon="save",
                    on_click=self._save_model,
                ).bind_visibility_from(self, "is_editing")
                ui.button(icon="delete", on_click=self._delete_model)

    def _toggle_edit(self) -> None:
        self.is_editing = not self.is_editing

    def _save_model(self) -> None:
        new_name = self.name_input.value.strip()
        if new_name:
            state.update_model_name(self.model, new_name)
            self.is_editing = False

    def _delete_model(self) -> None:
        state.delete_model(self.model)
