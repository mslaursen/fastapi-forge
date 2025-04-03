from nicegui import ui
from pydantic import ValidationError


def notify_validation_error(e: ValidationError) -> None:
    msg = e.errors()[0].get("msg", "Something went wrong.")
    ui.notify(msg, type="negative")


def notify_model_exists(model_name: str) -> None:
    ui.notify(
        f"Model '{model_name}' already exists.",
        type="negative",
    )


def notify_field_exists(field_name: str, model_name: str) -> None:
    ui.notify(
        f"Model' {model_name}' already has field '{field_name}'.",
        type="negative",
    )


def notify_something_went_wrong() -> None:
    ui.notify(
        "Something went wrong...",
        type="warning",
    )
