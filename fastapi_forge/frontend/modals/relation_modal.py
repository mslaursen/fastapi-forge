from collections.abc import Callable

from nicegui import ui

from fastapi_forge.dtos import Model, ModelRelationship


class AddRelationModal(ui.dialog):
    def __init__(self, on_add_relation: Callable):
        super().__init__()
        self.on_add_relation = on_add_relation
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

    def _set_target_model_options(self, models: list[Model]) -> None:
        self.target_model.options = [model.name for model in models]
        self.target_model.value = models[0].name if models else None

    def _add_relation(self) -> None:
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

    def open(self, models: list[Model]) -> None:
        self.target_model.options = [model.name for model in models]
        self.target_model.value = models[0].name if models else None
        super().open()


class UpdateRelationModal(ui.dialog):
    def __init__(self, on_update_relation: Callable):
        super().__init__()
        self.on_update_relation = on_update_relation
        self.selected_relation: ModelRelationship | None = None

        self.on("hide", lambda: self._reset())
        self._build()

    def _build(self) -> None:
        with self, ui.card().classes("no-shadow border-[1px]"):
            ui.label("Update Relationship").classes("text-lg font-bold")
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
                    "Update Relation",
                    on_click=self._update_relation,
                )

    def _update_relation(self) -> None:
        if not self.selected_relation:
            return

        self.on_update_relation(
            field_name=self.field_name.value,
            target_model=self.target_model.value,
            back_populates=self.back_populates.value,
            nullable=self.nullable.value,
            index=self.index.value,
            unique=self.unique.value,
        )
        self.close()

    def _set_relation(self, relation: ModelRelationship) -> None:
        self.selected_relation = relation
        if relation:
            self.field_name.value = relation.field_name
            self.target_model.value = relation.target_model
            self.nullable.value = relation.nullable
            self.index.value = relation.index
            self.unique.value = relation.unique
            self.back_populates.value = relation.back_populates

    def _reset(self) -> None:
        self.selected_relation = None
        self.field_name.value = ""
        self.target_model.value = None
        self.back_populates.value = ""
        self.nullable.value = False
        self.index.value = False
        self.unique.value = False

    def open(
        self,
        relation: ModelRelationship | None = None,
        models: list[Model] | None = None,
    ) -> None:
        if relation and models:
            self._set_relation(relation)
            self.target_model.options = [model.name for model in models]
            default_target_model = next(
                (model for model in models if model.name == relation.target_model),
                None,
            )
            if default_target_model:
                self.target_model.value = default_target_model.name
            self.target_model.options = [model.name for model in models]

        super().open()
