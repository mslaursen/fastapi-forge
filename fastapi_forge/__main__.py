import click
from fastapi_forge.frontend import init
from pathlib import Path
import os


@click.group()
def main() -> None:
    """FastAPI Forge CLI."""


@main.command()
@click.option(
    "--use-example",
    is_flag=True,
    help="Generate a new project using a prebuilt example provided by FastAPI Forge. "
    "This option is ideal for quickly getting started with a standard template.",
)
@click.option(
    "--no-ui",
    is_flag=True,
    help="Generate the project directly in the terminal without launching the UI. "
    "Use this option for headless environments or when you prefer a CLI-only workflow.",
)
@click.option(
    "--from-yaml",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Generate a project using a custom configuration from a YAML file. "
    "Provide the path to the YAML file (supports relative or absolute paths, and '~' for home directory). "
    "Use '--no-ui' to generate the project immediately, otherwise the configuration will be loaded into the UI for further customization.",
)
def start(use_example: bool, no_ui: bool, from_yaml: str | None = None) -> None:
    """Start the FastAPI Forge server and generate a new project."""
    if use_example and from_yaml:
        raise click.UsageError(
            "Cannot use '--use-example' and '--from-yaml' together.",
        )

    yaml_path = None
    if from_yaml:
        expanded_yaml_path = os.path.expanduser(from_yaml)
        yaml_path = Path(expanded_yaml_path).resolve()

        if not yaml_path.exists():
            raise click.FileError(f"YAML file not found: {yaml_path}")
        if not yaml_path.is_file():
            raise click.FileError(f"Path is not a file: {yaml_path}")

    init(
        use_example=use_example,
        no_ui=no_ui,
        yaml_path=yaml_path,
    )


@main.command()
def version() -> None:
    """Print the version of FastAPI Forge."""
    from importlib.metadata import version

    click.echo(f"FastAPI Forge v{version('fastapi-forge')}.")


if __name__ in {"__main__", "__mp_main__"}:
    main()
