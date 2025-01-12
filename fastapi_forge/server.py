from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from cookiecutter.main import cookiecutter
from fastapi_forge.dtos import ForgeProjectRequestDTO
import threading
import uvicorn
import os


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
    project_name = request.project_name
    print(f"Creating project: {project_name}")


class FastAPIServer:
    """FastAPI server wrapper."""

    def __init__(self, host: str, port: int, app: FastAPI):
        self.host = host
        self.port = port
        self.app = app
        self.server_thread: threading.Thread | None = None

    def start(self) -> None:
        """Starts the server in a separate thread."""
        self.server_thread = threading.Thread(
            target=uvicorn.run,
            args=(self.app,),
            kwargs={"host": self.host, "port": self.port},
            daemon=True,
        )
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
