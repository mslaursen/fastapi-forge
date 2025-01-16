import webbrowser
from .dtos import Model
from .jinja import render_models_to_dtos, render_models_to_models
import os


def open_browser(url: str) -> None:
    """Opens a web browser to the specified URL."""
    webbrowser.open(url)


def generate_extra(project_name: str, models: list[Model]) -> None:
    """Generates extra files for the project."""

    file_to_func = {
        "models.py": render_models_to_models,
        "dtos.py": render_models_to_dtos,
    }

    for file, func in file_to_func.items():
        file = os.path.join(os.getcwd(), project_name, "src", file)

        with open(file, "w") as file:
            file.write(func(models))
