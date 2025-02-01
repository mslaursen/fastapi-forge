import click
from fastapi_forge.frontend import init


@click.group()
def main() -> None:
    """FastAPI Forge CLI."""


@main.command()
def start() -> None:
    """Start the server, and open the browser."""

    init()


@main.command()
def version() -> None:
    """Print the version of FastAPI Forge."""
    from importlib.metadata import version

    click.echo(f"FastAPI Forge v{version('fastapi-forge')}.")


if __name__ in {"__main__", "__mp_main__"}:
    main()
