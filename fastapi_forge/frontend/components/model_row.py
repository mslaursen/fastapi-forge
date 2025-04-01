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
        self.is_selected_row = model == state.selected_model
        self.color = color
        self.is_editing = False
        self._build()

    def _build(self) -> None:
        base_classes = "w-full flex items-center justify-between cursor-pointer p-2 rounded transition-all"
        if self.is_selected_row:
            base_classes += " bg-blue-100 dark:bg-blue-900 border-l-4 border-blue-500"
        else:
            base_classes += " hover:bg-gray-100 dark:hover:bg-gray-800"

        with self.classes(base_classes):
            self.name_label = (
                ui.label(text=self.model.name)
                .classes("self-center")
                .on("click", lambda: state.select_model(self.model))
            )
            if self.color:
                self.name_label.classes(add=self.color)
            self.name_input = (
                ui.input(value=self.model.name)
                .classes("self-center")
                .bind_visibility_from(self, "is_editing")
            )
            self.name_label.bind_visibility_from(self, "is_editing", lambda x: not x)

            # self.on("click", lambda: state.select_model(self.model))

            with ui.row().classes("gap-2"):
                self.edit_button = ui.button(
                    icon="edit",
                    on_click=self._toggle_edit,
                ).bind_visibility_from(self, "is_editing", lambda x: not x)
                self.save_button = ui.button(
                    icon="save",
                    on_click=self._save_model,
                ).bind_visibility_from(self, "is_editing")
                ui.button(
                    icon="delete", on_click=lambda _: state.delete_model(self.model)
                )

    def _toggle_edit(self) -> None:
        print("editing")
        self.is_editing = not self.is_editing

    def _save_model(self) -> None:
        new_name = self.name_input.value.strip()
        if new_name:
            state.update_model_name(self.model, new_name)
            self.is_editing = False
