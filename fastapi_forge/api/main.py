import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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


if __name__ == "__main__":
    start_forge_api()
