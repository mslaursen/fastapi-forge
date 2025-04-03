import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any

import aiofiles
import yaml

from fastapi_forge.dtos import Model, ModelField, ModelFieldMetadata, ProjectSpec
from fastapi_forge.enums import FieldDataType, HTTPMethod
from fastapi_forge.jinja import (
    render_model_to_dao,
    render_model_to_delete_test,
    render_model_to_dto,
    render_model_to_get_id_test,
    render_model_to_get_test,
    render_model_to_model,
    render_model_to_patch_test,
    render_model_to_post_test,
    render_model_to_routers,
)
from fastapi_forge.logger import logger
from fastapi_forge.string_utils import camel_to_snake


async def _write_file(path: Path, content: str) -> None:
    try:
        async with aiofiles.open(path, "w") as file:
            await file.write(content)
        logger.info(f"Created file: {path}")
    except OSError as exc:
        logger.error(f"Failed to write file {path}: {exc}")
        raise


class ProjectLoader:
    """Load project from YAML file."""

    def __init__(
        self,
        project_path: Path,
    ) -> None:
        self.project_path = project_path
        logger.info(f"Loading project from: {project_path}")

    def _load_project_to_dict(self) -> dict[str, Any]:
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project config file not found: {self.project_path}",
            )

        with self.project_path.open() as stream:
            try:
                return yaml.safe_load(stream)["project"]
            except Exception as exc:
                raise exc

    def load_project_spec(self) -> ProjectSpec:
        project_dict = self._load_project_to_dict()
        models = [Model(**model) for model in project_dict.get("models", []) or []]
        project_dict.pop("models")
        return ProjectSpec(**project_dict, models=models)

    def load_project_input(self) -> ProjectSpec:
        return ProjectSpec(**self._load_project_to_dict())


class ProjectExporter:
    """Export project to YAML file."""

    def __init__(self, project_input: ProjectSpec) -> None:
        self.project_input = project_input

    async def export_project(self) -> None:
        yaml_structure = {
            "project": self.project_input.model_dump(
                round_trip=True,  # exclude computed fields
            ),
        }
        file_path = Path.cwd() / f"{self.project_input.project_name}.yaml"
        await _write_file(
            file_path,
            yaml.dump(yaml_structure, default_flow_style=False, sort_keys=False),
        )


TEST_RENDERERS: dict[HTTPMethod, Callable[[Model], str]] = {
    HTTPMethod.GET: render_model_to_get_test,
    HTTPMethod.GET_ID: render_model_to_get_id_test,
    HTTPMethod.POST: render_model_to_post_test,
    HTTPMethod.PATCH: render_model_to_patch_test,
    HTTPMethod.DELETE: render_model_to_delete_test,
}


class ProjectBuilder:
    def __init__(
        self,
        project_spec: ProjectSpec,
        base_path: Path | None = None,
    ) -> None:
        self.project_spec = project_spec
        self.project_name = project_spec.project_name
        self.base_path = base_path or Path.cwd()
        self.project_dir = self.base_path / self.project_name
        self.src_dir = self.project_dir / "src"
        self._insert_relation_fields()

    def _insert_relation_fields(self) -> None:
        """Adds ModelFields to a model, based its relationships."""
        for model in self.project_spec.models:
            field_names_set = {field.name for field in model.fields}
            for relation in model.relationships:
                if relation.field_name in field_names_set:
                    continue
                model.fields.append(
                    ModelField(
                        name=relation.field_name,
                        type=FieldDataType.UUID,
                        primary_key=False,
                        nullable=relation.nullable,
                        unique=relation.unique,
                        index=relation.index,
                        metadata=ModelFieldMetadata(is_foreign_key=True),
                    ),
                )

    async def _create_directory(self, path: Path) -> None:
        if not path.exists():
            path.mkdir(parents=True)
            logger.info(f"Created directory: {path}")

    async def _init_project_directories(self) -> None:
        await self._create_directory(self.project_dir)
        await self._create_directory(self.src_dir)

    async def _create_module_path(self, module: str) -> Path:
        path = self.src_dir / module
        await self._create_directory(path)
        return path

    async def _write_artifact(
        self,
        module: str,
        model: Model,
        render_func: Callable[[Model], str],
    ) -> None:
        path = await self._create_module_path(module)
        file_name = f"{camel_to_snake(model.name)}_{module}.py"
        await _write_file(path / file_name, render_func(model))

    async def _write_tests(self, model: Model) -> None:
        test_dir = (
            self.project_dir / "tests" / "endpoint_tests" / camel_to_snake(model.name)
        )
        await self._create_directory(test_dir)
        await _write_file(
            test_dir / "__init__.py",
            "# Automatically generated by FastAPI Forge\n",
        )

        tasks = []
        for method, render_func in TEST_RENDERERS.items():
            method_suffix = "id" if method == HTTPMethod.GET_ID else ""
            file_name = (
                f"test_{method.value.replace('_id', '')}"
                f"_{camel_to_snake(model.name)}"
                f"{f'_{method_suffix}' if method_suffix else ''}"
                ".py"
            )
            tasks.append(_write_file(test_dir / file_name, render_func(model)))

        await asyncio.gather(*tasks)

    async def build_artifacts(self) -> None:
        await self._init_project_directories()

        tasks = []
        for model in self.project_spec.models:
            tasks.append(self._write_artifact("models", model, render_model_to_model))

            metadata = model.metadata
            if metadata.create_dtos:
                tasks.append(self._write_artifact("dtos", model, render_model_to_dto))
            if metadata.create_daos:
                tasks.append(self._write_artifact("daos", model, render_model_to_dao))
            if metadata.create_endpoints:
                tasks.append(
                    self._write_artifact("routes", model, render_model_to_routers),
                )
            if metadata.create_tests:
                tasks.append(self._write_tests(model))

        await asyncio.gather(*tasks)
