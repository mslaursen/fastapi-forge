from collections.abc import Callable
from pathlib import Path
from time import perf_counter

import click

from fastapi_forge.logger import logger
from fastapi_forge.project_io import ArtifactBuilder, create_fastapi_artifact_builder
from fastapi_forge.schemas import ProjectSpec

from .cookiecutter_adapter import (
    CookiecutterAdapter,
    DryRunCookiecutterAdapter,
    OverwriteCookiecutterAdapter,
)
from .project_validators import ProjectNameValidator, ProjectValidator
from .template_processors import DefaultTemplateProcessor, TemplateProcessor


class ProjectBuildDirector:
    def __init__(
        self,
        builder: ArtifactBuilder,
        template_processor: TemplateProcessor,
        template_generator: CookiecutterAdapter,
        template_resolver: Callable[[], Path],
        project_validator: ProjectValidator | None = None,
    ):
        self.builder = builder
        self.validator = project_validator
        self.template_processor = template_processor
        self.template_generator = template_generator
        self.template_resolver = template_resolver

    async def build(self, spec: ProjectSpec) -> None:
        if self.validator:
            self.validator.validate(spec)
        await self.builder.build_artifacts()

        context = self.template_processor.process(spec)
        template_path = self.template_resolver()

        self.template_generator.generate(
            template_path=template_path,
            output_dir=Path.cwd().resolve(),
            extra_context=context,
        )


def _get_template_path() -> Path:
    template_path = Path(__file__).resolve().parent.parent / "template"
    if not template_path.exists():
        raise RuntimeError(f"Template directory not found: {template_path}")
    if not template_path.is_dir():
        raise RuntimeError(f"Template path is not a directory: {template_path}")
    return template_path


async def build_fastapi_project(
    spec: ProjectSpec,
    dry_run: bool = False,
) -> None:
    start_time = perf_counter()

    template_generator = (
        OverwriteCookiecutterAdapter() if not dry_run else DryRunCookiecutterAdapter()
    )

    try:
        director = ProjectBuildDirector(
            builder=create_fastapi_artifact_builder(spec, dry_run=dry_run),
            project_validator=ProjectNameValidator(),
            template_processor=DefaultTemplateProcessor(),
            template_generator=template_generator,
            template_resolver=_get_template_path,
        )

        await director.build(spec)

        build_time = perf_counter() - start_time
        logger.info(f"Project build completed in {build_time:.2f} seconds")

        click.secho("\n🎉 Project generated successfully !", fg="green", bold=True)
        click.echo("\n🚀 Next steps to get started:\n")

        steps = [
            ("Navigate to your project directory", "cd your_project_name"),
            ("Start the development environment", "make up  # or docker-compose up"),
            ("(Optional) Run tests", "make test"),
            ("Access the API documentation", "http://localhost:8000/docs"),
        ]

        for i, (desc, cmd) in enumerate(steps, 1):
            click.echo(f"{i}. {desc}:")
            click.secho(f"   {cmd}", fg="cyan")

        click.echo("\n💡 Pro tip: Run 'make help' to see all available commands")
        click.secho("\n✨ Happy coding with your new FastAPI project!", fg="magenta")

    except Exception as error:
        logger.error(f"Project build failed: {error}")
        raise
