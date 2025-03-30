from nicegui import ui

from fastapi_forge.frontend.state import state


class ModelCreate(ui.row):
    def __init__(self):
        super().__init__(wrap=False)
        self._build()

    def _build(self) -> None:
        with self.classes("w-full flex items-center justify-between"):
            self.model_input = (
                ui.input(placeholder="Model name")
                .classes("self-center")
                .tooltip(
                    "Model names should be singular (e.g., 'user' instead of 'users').",
                )
            )
            self.add_button = (
                ui.button(icon="add", on_click=self._add_model)
                .classes("self-center")
                .tooltip("Add Model")
            )

    def _add_model(self) -> None:
        if not self.model_input.value:
            return
        value: str = self.model_input.value
        model_name = value.strip()
        if model_name:
            state.add_model(model_name)
            self.model_input.value = ""
