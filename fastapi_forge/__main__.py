import sys
from pathlib import Path

import click

from fastapi_forge.frontend.main import init
from fastapi_forge.project_io import (
    YamlProjectLoader,
    create_postgres_project_loader,
)


def confirm_uv_installed() -> bool:
    """Show UV requirement warning and get confirmation."""
    click.secho(
        "\n⚠️  Important Requirement (use the '--yes' option to skip)",
        fg="yellow",
        bold=True,
    )
    click.echo("Generated projects require UV to be installed.")
    click.secho(
        "GitHub: https://docs.astral.sh/uv/getting-started/installation",
        fg="blue",
        underline=True,
    )

    if not click.confirm(
        "\nDo you have UV installed and ready to use?",
        default=True,
    ):
        click.secho(
            "\n❌ Please install UV first and restart this command.",
            fg="red",
        )
        click.echo("Verify with: uv --version")
        return False
    return True


@click.group(
    help="FastAPI Forge CLI - A tool for generating FastAPI projects.",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(package_name="fastapi-forge")
@click.option("-v", "--verbose", count=True, help="Increase verbosity level.")
@click.pass_context
def main(ctx: click.Context, verbose: int) -> None:
    """FastAPI Forge CLI entry point."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@main.command(
    help="Start FastAPI Forge - Generate a new FastAPI project.",
)
@click.option(
    "--use-example",
    is_flag=True,
    help="Generate a new project using a prebuilt example provided by FastAPI Forge.",
)
@click.option(
    "--no-ui",
    is_flag=True,
    help="Generate the project directly in the terminal without launching the UI (default: False).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run without generating any files (requires --no-ui).",
)
@click.option(
    "--from-yaml",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
        path_type=Path,
    ),
    help="Generate a project using a custom configuration from a YAML file.",
)
@click.option(
    "--yes",
    is_flag=True,
    help="Automatically confirm all prompts (use with caution).",
)
@click.option(
    "--conn-string",
    help="Generate a project from a PostgreSQL connection string "
    "(e.g., postgresql://user:password@host:port/dbname)",
)
@click.pass_context
def start(
    _: click.Context,
    use_example: bool = False,
    no_ui: bool = False,
    dry_run: bool = False,
    yes: bool = False,
    from_yaml: Path | None = None,
    conn_string: str | None = None,
) -> None:
    """Start FastAPI Forge."""
    if not yes and not confirm_uv_installed():
        sys.exit(1)

    option_count = sum([use_example, bool(from_yaml), bool(conn_string)])
    if option_count > 1:
        raise click.UsageError(
            "Only one of '--use-example', '--from-yaml', or '--conn-string' can be used."
        )

    if no_ui and option_count < 1:
        raise click.UsageError(
            "Option '--no-ui' requires one of '--use-example', '--from-yaml', or '--conn-string'."
        )

    if dry_run and not no_ui:
        raise click.UsageError("Option '--dry-run' requires '--no-ui' to be set.")

    project_spec = None

    if from_yaml:
        project_spec = YamlProjectLoader(project_path=from_yaml).load()
    elif conn_string:
        project_spec = create_postgres_project_loader(conn_string).load()
    elif use_example:
        base_path = Path(__file__).parent / "example-projects"
        path = base_path / "game_zone.yaml"
        project_spec = YamlProjectLoader(project_path=path).load()

    init(project_spec=project_spec, no_ui=no_ui, dry_run=dry_run)


if __name__ in {"__main__", "__mp_main__"}:
    main()
