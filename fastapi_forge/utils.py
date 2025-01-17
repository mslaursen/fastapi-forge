import webbrowser
from .dtos import Model
from .jinja import render_models_to_dtos, render_models_to_models
import os


def open_browser(url: str) -> None:
    """Opens a web browser to the specified URL."""
    webbrowser.open(url)


def _init_proj_dirs(project_name: str) -> None:
    """Create project directories."""

    project_dir = os.path.join(os.getcwd(), project_name)

    if not os.path.exists(project_dir):
        os.mkdir(project_dir)

    src_dir = os.path.join(project_dir, "src")

    if not os.path.exists(src_dir):
        os.mkdir(src_dir)


def generate_for_sqlalchemy(project_name: str, models: list[Model]) -> None:
    """Generate SQLAlchemy extras for the specified project name."""

    file_to_func = {
        "models.py": render_models_to_models,
        "dtos.py": render_models_to_dtos,
    }

    _init_proj_dirs(project_name)

    for file, func in file_to_func.items():
        file = os.path.join(os.getcwd(), project_name, "src", file)

        with open(file, "w") as file:
            file.write(func(models))
