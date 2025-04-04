from nicegui import ui

from fastapi_forge.dtos import Model
from fastapi_forge.frontend.state import state


class ModelRow(ui.row):
    def __init__(
        self,
        model: Model,
        color: str | None = None,
        icon: str | None = None,
    ):
        super().__init__(wrap=False)
        self.model = model
        self.is_selected_row = model == state.selected_model
        self.color = color
        self.icon = icon
        self.is_editing = False
        self._build()

    def _build(self) -> None:
        self.on("click", lambda: state.select_model(self.model))
        base_classes = "w-full flex items-center justify-between cursor-pointer p-2 rounded transition-all"
        if self.is_selected_row:
            base_classes += " bg-blue-100 dark:bg-blue-900 border-l-4 border-blue-500"
        else:
            base_classes += " hover:bg-gray-100 dark:hover:bg-gray-800"

        with self.classes(base_classes):
            with ui.row().classes("flex-nowrap gap-2 min-w-fit"):
                if self.icon:
                    ui.icon(self.icon, color="green", size="20px").classes(
                        "self-center"
                    )
                self.name_label = ui.label(text=self.model.name).classes("self-center")
            if self.color:
                self.name_label.classes(add=self.color)
            self.name_input = (
                ui.input(value=self.model.name)
                .classes("self-center")
                .bind_visibility_from(self, "is_editing")
            )
            self.name_label.bind_visibility_from(self, "is_editing", lambda x: not x)

            with ui.row().classes("flex-nowrap gap-2 min-w-fit"):
                self.edit_button = (
                    ui.button(
                        icon="edit",
                    )
                    .on("click.stop", self._toggle_edit)
                    .bind_visibility_from(self, "is_editing", lambda x: not x)
                    .classes("min-w-fit")
                )

                self.save_button = (
                    ui.button(
                        icon="save",
                    )
                    .on("click.stop", self._save_model)
                    .bind_visibility_from(self, "is_editing")
                    .classes("min-w-fit")
                )

                ui.button(
                    icon="delete",
                ).on("click.stop", lambda: state.delete_model(self.model)).classes(
                    "min-w-fit"
                )

    def _toggle_edit(self) -> None:
        self.is_editing = not self.is_editing

    def _save_model(self) -> None:
        new_name = self.name_input.value.strip()
        if new_name:
            state.update_model_name(self.model, new_name)
            self.is_editing = False
