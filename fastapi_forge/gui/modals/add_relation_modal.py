from pydantic import BaseModel, ValidationError
from fastapi_forge import dtos as m
from fastapi_forge.gui import notifications as n
from fastapi_forge.gui.state import state
from nicegui import ui

import typing as t


class AddRelationModal(ui.dialog):
    def __init__(
        self,
    ):
        super().__init__()
        self.on("hide", lambda: self._reset())
        self._build()

    def _build(self) -> None:
        with self, ui.card().classes("no-shadow border-[1px]"):
            ui.label("Add Relationship").classes("text-lg font-bold")
            with ui.row().classes("w-full gap-2"):
                self.field_name = ui.input(label="Field Name").classes("w-full")
                self.target_model = ui.select(
                    label="Target Model",
                    options=[],
                ).classes("w-full")

                self.nullable = ui.checkbox("Nullable").classes("w-full")
                self.index = ui.checkbox("Index").classes("w-full")
                self.unique = ui.checkbox("Unique").classes("w-full")

                self.back_populates = ui.input(label="Back Populates").classes("w-full")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Close", on_click=self.close)
                ui.button(
                    "Add Relation",
                    on_click=self._add_relation,
                )

    def _set_target_model_options(self, models: list[m.Model]) -> None:
        self.target_model.options = [model.name for model in models]
        self.target_model.value = models[0].name if models else None

    def _add_relation(self) -> None:
        state.rela
        self.on_add_relation(
            field_name=self.field_name.value,
            target_model=self.target_model.value,
            back_populates=self.back_populates.value or None,
            nullable=self.nullable.value,
            index=self.index.value,
            unique=self.unique.value,
        )
        self.close()

    def _reset(self) -> None:
        self.field_name.value = ""
        self.target_model.value = None
        self.back_populates.value = ""
        self.nullable.value = False
        self.index.value = False
        self.unique.value = False

    def open(self, models: list[m.Model]) -> None:
        self.target_model.options = [model.name for model in models]
        self.target_model.value = models[0].name if models else None
        super().open()
