from pathlib import Path

import click

from fastapi_forge.frontend import init
from fastapi_forge.project_io import ProjectLoader


@click.group()
def main() -> None:
    """FastAPI Forge CLI."""


@main.command()
@click.option(
    "--use-example",
    is_flag=True,
    help="Generate a new project using a prebuilt example provided by FastAPI Forge.",
)
@click.option(
    "--no-ui",
    is_flag=True,
    help="Generate the project directly in the terminal without launching the UI.",
)
@click.option(
    "--from-yaml",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Generate a project using a custom configuration from a YAML file.",
)
@click.option(
    "--db-url",
    help="PostgreSQL connection URL (e.g., postgresql://user:password@host:port/dbname)",
)
def start(
    use_example: bool = False,
    no_ui: bool = False,
    from_yaml: str | None = None,
    db_url: str | None = None,
) -> None:
    """Start the FastAPI Forge server and generate a new project."""
    option_count = sum([use_example, bool(from_yaml), bool(db_url)])
    if option_count > 1:
        msg = "Only one of '--use-example', '--from-yaml', or '--db-url' can be used."
        raise click.UsageError(msg)

    if no_ui and option_count < 1:
        msg = "Option '--no-ui' requires one of '--use-example', '--from-yaml', or '--db-url' to be set."
        raise click.UsageError(msg)

    project_spec = None

    if from_yaml:
        yaml_path = Path(from_yaml).expanduser().resolve()
        if not yaml_path.is_file():
            raise click.FileError(f"YAML file not found: {yaml_path}")
        project_spec = ProjectLoader(project_path=yaml_path).load_project()
    elif db_url:
        project_spec = ProjectLoader.load_project_from_db(
            connection_string=db_url,
        )
    elif use_example:
        base_path = Path(__file__).parent / "example-projects"
        path = base_path / "game_zone.yaml"

        project_spec = ProjectLoader(project_path=path).load_project()

    init(project_spec=project_spec, no_ui=no_ui)


@main.command()
def version() -> None:
    """Print the version of FastAPI Forge."""
    from importlib.metadata import version

    click.echo(f"FastAPI Forge v{version('fastapi-forge')}.")


if __name__ in {"__main__", "__mp_main__"}:
    main()
