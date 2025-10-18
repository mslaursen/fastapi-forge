import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi_forge.core.build import build_fastapi_project
from fastapi_forge.schemas import ProjectSpec

app = FastAPI()


def start_forge_api() -> None:
    app.mount(
        "/",
        StaticFiles(
            directory=Path(__file__).parent.parent / "static",
            html=True,
        ),
        name="frontend",
    )

    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000)


@app.post("/generate")
async def generate_project(project_spec: ProjectSpec) -> None:
    try:
        await build_fastapi_project(project_spec, dry_run=False)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    start_forge_api()
