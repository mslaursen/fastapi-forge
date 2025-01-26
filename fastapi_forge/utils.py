import webbrowser
from .dtos import Model
from .jinja import (
    render_model_to_dto,
    render_model_to_model,
    render_model_to_dao,
    render_model_to_routers,
    render_model_to_test,
)
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


def _create_path(project_name: str, path: str) -> str:
    """Create a path."""

    path = os.path.join(os.getcwd(), project_name, path)

    if not os.path.exists(path):
        os.mkdir(path)

    return path


def _write_dto(project_name: str, model: Model) -> None:
    """Write DTOs to file."""

    path = _create_path(project_name, "src/dtos")
    file = os.path.join(path, f"{model.name.lower()}_dtos.py")

    with open(file, "w") as file:
        file.write(render_model_to_dto(model))


def _write_model(project_name: str, model: Model) -> None:
    """Write models to file."""

    path = _create_path(project_name, "src/models")
    file = os.path.join(path, f"{model.name.lower()}_models.py")

    with open(file, "w") as file:
        file.write(render_model_to_model(model))


def _write_dao(project_name: str, model: Model) -> None:
    """Write DAOs to file."""

    path = _create_path(project_name, "src/daos")
    file = os.path.join(path, f"{model.name.lower()}_daos.py")

    with open(file, "w") as file:
        file.write(render_model_to_dao(model))


def _write_routers(project_name: str, model: Model) -> None:
    """Write routers to file."""

    path = _create_path(project_name, "src/routes")
    file = os.path.join(path, f"{model.name.lower()}_routes.py")

    with open(file, "w") as file:
        file.write(render_model_to_routers(model))


def _write_tests(project_name: str, model: Model) -> None:
    """Write tests to file."""

    path = _create_path(project_name, f"tests/endpoint_tests/{model.name.lower()}")

    methods = ["get", "post", "patch", "delete"]

    for method in methods:
        file = os.path.join(path, f"test_{method}_{model.name.lower()}.py")

        with open(file, "w") as file:
            file.write(render_model_to_test(model, method=method))


def build_project_artifacts(project_name: str, models: list[Model]) -> None:
    """Build project artifacts."""

    _init_proj_dirs(project_name)

    for model in models:
        _write_dto(project_name, model)
        _write_model(project_name, model)
        _write_dao(project_name, model)
        _write_routers(project_name, model)
        # _write_tests(project_name, model)
