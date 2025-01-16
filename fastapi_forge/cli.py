import click


from .config import FastAPIServerConfig
from .server import app, FastAPIServer
from .utils import open_browser


@click.group()
def main() -> None:
    """CLI for managing the server."""
    pass


@main.command()
@click.option("--host", default=FastAPIServerConfig.host, help="Server host.")
@click.option("--port", default=FastAPIServerConfig.port, type=int, help="Server port.")
def start(host: str, port: int) -> None:
    """Starts the server and opens the UI in a browser."""
    click.echo("Starting the FastAPI server...")

    server = FastAPIServer(host, port, app)
    server.start()

    open_browser(f"http://{host}:{port}")

    server.wait_for_shutdown()

    click.echo("Server stopped.")


if __name__ == "__main__":
    main()
