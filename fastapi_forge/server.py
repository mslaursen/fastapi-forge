from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from cookiecutter.main import cookiecutter
from .dtos import ForgeProjectRequestDTO
import threading
import os
from .utils import build_project_artifacts


app = FastAPI()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if not os.path.exists(STATIC_DIR):
    raise RuntimeError(f"Static directory not found: {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_ui() -> HTMLResponse:
    """Serves the UI."""

    path = os.path.join(STATIC_DIR, "index.html")

    with open(path, "r") as file:
        content = file.read()

    return HTMLResponse(content)


@app.post("/forge")
async def forge_project(request: ForgeProjectRequestDTO) -> None:
    """Creates a new project using the provided template."""

    print("Creating project...")

    template_path = os.path.join(os.path.dirname(__file__), "template")

    if not os.path.exists(template_path):
        raise RuntimeError(f"Template directory not found: {template_path}")

    if request.use_postgres:
        build_project_artifacts(request.project_name, request.models)

    cookiecutter(
        template_path,
        output_dir=os.getcwd(),
        no_input=True,
        overwrite_if_exists=True,
        extra_context={
            "project_name": request.project_name,
            "use_postgres": request.use_postgres,
            "create_daos": request.create_daos,
            "create_routes": request.create_routes,
            "models": {
                "models": [model.model_dump() for model in request.models],
            },
        },
    )

    print("Project created successfully.")


@app.post("/shutdown")
def shutdown() -> None:
    """Shuts down the program."""
    os._exit(0)


class FastAPIServer:
    """FastAPI server."""

    def __init__(self, host: str, port: int, app: FastAPI):
        self.host = host
        self.port = port
        self.app = app
        self.server_thread: threading.Thread | None = None

    def start(self) -> None:
        """Starts the server in a separate thread."""
        from uvicorn import Config, Server

        config = Config(
            app=self.app,
            host=self.host,
            port=self.port,
            reload=True,
        )
        server = Server(config)

        def _run_server():
            server.run()

        self.server_thread = threading.Thread(target=_run_server, daemon=True)
        self.server_thread.start()

    def is_running(self) -> bool:
        """Checks if the server is active."""
        return self.server_thread is not None and self.server_thread.is_alive()

    def wait_for_shutdown(self) -> None:
        """Waits for the server to shut down."""
        try:
            while self.is_running():
                pass
        except KeyboardInterrupt:
            pass
