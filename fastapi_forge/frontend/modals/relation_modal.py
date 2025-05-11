from abc import ABC, abstractmethod
from collections.abc import Callable

from nicegui import ui

from fastapi_forge.enums import OnDeleteEnum
from fastapi_forge.frontend.notifications import notify_value_error
from fastapi_forge.schemas import Model, ModelRelationship


class BaseRelationModal(ui.dialog, ABC):
    title: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build_common_ui()

    def _build_common_ui(self) -> None:
        with self, ui.card().classes("w-full max-w-2xl shadow-lg rounded-lg"):
            with ui.row().classes("w-full justify-between items-center p-4 border-b"):
                ui.label(self.title).classes("text-xl font-semibold")

            with ui.column().classes("w-full p-6 space-y-4"):
                with ui.grid(columns=2).classes("w-full gap-4"):
                    self.field_name = ui.input(label="Field Name").props(
                        "outlined dense"
                    )
                    self.target_model = ui.select(
                        label="Target Model",
                        options=[],
                    ).props("outlined dense")
                    self.on_delete = ui.select(
                        label="On Delete",
                        options=list(OnDeleteEnum),
                        value=OnDeleteEnum.CASCADE,
                    ).props("outlined dense")
                    self.back_populates = ui.input(label="Back Populates").props(
                        "outlined dense"
                    )

                with ui.row().classes("w-full justify-between gap-4"):
                    self.nullable = ui.checkbox("Nullable").props("dense")
                    self.index = ui.checkbox("Index").props("dense")
                    self.unique = ui.checkbox("Unique").props("dense")

            with ui.row().classes("w-full justify-end p-4 border-t gap-2"):
                self._build_action_buttons()

    @abstractmethod
    def _build_action_buttons(self) -> None:
        pass

    def _reset(self) -> None:
        self.field_name.value = ""
        self.target_model.value = None
        self.back_populates.value = ""
        self.on_delete.value = None
        self.nullable.value = False
        self.index.value = False
        self.unique.value = False


class AddRelationModal(BaseRelationModal):
    title = "Add Relationship"

    def __init__(self, on_add_relation: Callable):
        super().__init__()
        self.on_add_relation = on_add_relation

    def _build_action_buttons(self) -> None:
        ui.button("Cancel", on_click=self.close)
        ui.button(
            "Add Relation",
            on_click=self._add_relation,
        )

    def _add_relation(self) -> None:
        try:
            self.on_add_relation(
                field_name=self.field_name.value,
                target_model=self.target_model.value,
                back_populates=self.back_populates.value or None,
                nullable=self.nullable.value,
                index=self.index.value,
                unique=self.unique.value,
                on_delete=self.on_delete.value,
            )
            self.close()
        except ValueError as exc:
            notify_value_error(exc)

    def open(self, models: list[Model]) -> None:
        self.target_model.options = [model.name for model in models]
        self.target_model.value = models[0].name if models else None
        super().open()


class UpdateRelationModal(BaseRelationModal):
    title = "Update Relationship"

    def __init__(self, on_update_relation: Callable):
        super().__init__()
        self.on_update_relation = on_update_relation
        self.selected_relation: ModelRelationship | None = None

    def _build_action_buttons(self) -> None:
        ui.button("Cancel", on_click=self.close)
        ui.button(
            "Update Relation",
            on_click=self._update_relation,
        )

    def _update_relation(self) -> None:
        if not self.selected_relation:
            return

        try:
            self.on_update_relation(
                field_name=self.field_name.value,
                target_model=self.target_model.value,
                back_populates=self.back_populates.value,
                nullable=self.nullable.value,
                index=self.index.value,
                unique=self.unique.value,
                on_delete=self.on_delete.value,
            )
            self.close()
        except ValueError as exc:
            notify_value_error(exc)

    def _set_relation(self, relation: ModelRelationship) -> None:
        self.selected_relation = relation
        if relation:
            self.field_name.value = relation.field_name
            self.target_model.value = relation.target_model
            self.nullable.value = relation.nullable
            self.index.value = relation.index
            self.unique.value = relation.unique
            self.back_populates.value = relation.back_populates
            self.on_delete.value = relation.on_delete

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
