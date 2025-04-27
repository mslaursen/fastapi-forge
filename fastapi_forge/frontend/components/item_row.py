from collections.abc import Callable

from nicegui import ui
from pydantic import BaseModel

from fastapi_forge.frontend.constants import ITEM_ROW_TRUNCATE_LEN
from fastapi_forge.frontend.state import state
from fastapi_forge.schemas import CustomEnum, Model


class _ItemRow[T: BaseModel](ui.row):
    def __init__(
        self,
        item: T,
        color: str | None = None,
        icon: str | None = None,
        *,
        is_selected: bool,
        on_select: Callable[[T], None],
        on_delete: Callable[[T], None],
        on_update_name: Callable[[T, str], None],
        get_name: Callable[[T], str] = lambda x: x.name,  # type: ignore
    ):
        super().__init__(wrap=False)
        self.item = item
        self.is_selected_row = is_selected
        self.color = color
        self.icon = icon
        self.is_editing = False

        self.on_select = on_select
        self.on_delete = on_delete
        self.on_update_name = on_update_name
        self.get_name = get_name

        self._build()

    def _build(self) -> None:
        self.on("click", lambda: self.on_select(self.item))
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
                full_name = self.get_name(self.item)

                if len(full_name) > ITEM_ROW_TRUNCATE_LEN:
                    truncated_name = (
                        (full_name[:ITEM_ROW_TRUNCATE_LEN] + "...")
                        if len(full_name) > ITEM_ROW_TRUNCATE_LEN
                        else full_name
                    )
                    self.name_label = (
                        ui.label(text=truncated_name)
                        .classes("self-center truncate")
                        .tooltip(full_name)
                    )
                else:
                    self.name_label = ui.label(text=full_name).classes(
                        "self-center truncate"
                    )

                if self.color:
                    self.name_label.classes(add=self.color)

            self.name_input = (
                ui.input(value=self.get_name(self.item))
                .classes("self-center")
                .bind_visibility_from(self, "is_editing")
            )
            self.name_label.bind_visibility_from(self, "is_editing", lambda x: not x)

            with ui.row().classes("flex-nowrap gap-2 min-w-fit"):
                self.edit_button = (
                    ui.button(icon="edit")
                    .on("click.stop", self._toggle_edit)
                    .bind_visibility_from(self, "is_editing", lambda x: not x)
                    .classes("min-w-fit")
                )

                self.save_button = (
                    ui.button(icon="save")
                    .on("click.stop", self._save_item)
                    .bind_visibility_from(self, "is_editing")
                    .classes("min-w-fit")
                )

                ui.button(icon="delete").on(
                    "click.stop", lambda: self.on_delete(self.item)
                ).classes("min-w-fit")

    def _toggle_edit(self) -> None:
        self.is_editing = not self.is_editing

    def _save_item(self) -> None:
        new_name = self.name_input.value.strip()
        if new_name:
            self.on_update_name(self.item, new_name)
            self.is_editing = False


class ModelRow(_ItemRow):
    def __init__(
        self,
        model: Model,
        color: str | None = None,
        icon: str | None = None,
    ):
        super().__init__(
            item=model,
            color=color,
            icon=icon,
            is_selected=model == state.selected_model,
            on_select=state.select_model,
            on_delete=state.delete_model,
            on_update_name=state.update_model_name,
        )


class EnumRow(_ItemRow):
    def __init__(
        self,
        custom_enum: CustomEnum,
        color: str | None = None,
        icon: str | None = None,
    ):
        super().__init__(
            item=custom_enum,
            color=color,
            icon=icon,
            is_selected=custom_enum == state.selected_enum,
            on_select=state.select_enum,
            on_delete=state.delete_enum,
            on_update_name=state.update_enum_name,
        )
