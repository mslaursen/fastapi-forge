import click
from .frontend import init


@click.group()
def main() -> None:
    """CLI for managing the server."""
    pass


@main.command()
def start() -> None:
    """Starts the FastAPI server with NiceGUI UI."""

    init()


if __name__ in {"__main__", "__mp_main__"}:
    main()
