from pydantic import BaseModel, ValidationError
from fastapi_forge import dtos as m
from nicegui import ui


def notify_validation_error(e: ValidationError) -> None:
    msg = e.errors()[0].get("msg", "Something went wrong.")
    ui.notify(msg, type="negative")


def notify_model_exists(model_name: str) -> None:
    ui.notify(f"Model '{model_name}' already exists.", type="negative")


def notify_something_went_wrong() -> None:
    ui.notify("Something went wrong...", type="warning")
