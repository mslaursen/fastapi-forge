from nicegui import ui


class Header(ui.header):
    def __init__(self):
        super().__init__()
        self.dark_mode = ui.dark_mode(value=True)
        self._build()

    def _build(self) -> None:
        with self:
            ui.button(
                icon="eva-github",
                color="white",
                on_click=lambda: ui.navigate.to(
                    "https://github.com/mslaursen/fastapi-forge",
                ),
            ).classes("self-center", remove="bg-white").tooltip(
                "Drop a ⭐️ if you like FastAPI Forge!",
            )

            ui.label(text="FastAPI Forge").classes(
                "font-bold ml-auto self-center text-2xl",
            )

            ui.button(
                icon="dark_mode",
                color="white",
                on_click=lambda: self.dark_mode.toggle(),
            ).classes("ml-auto", remove="bg-white")
