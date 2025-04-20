from nicegui import ui
from pydantic import ValidationError


def notify_validation_error(e: ValidationError) -> None:
    msg = e.errors()[0].get("msg", "Something went wrong.")
    ui.notify(msg, type="negative")


def notify_value_error(e: ValueError) -> None:
    ui.notify(str(e), type="negative")


def notify_model_exists(model_name: str) -> None:
    ui.notify(
        f"Model '{model_name}' already exists.",
        type="negative",
    )


def notify_enum_exists(enum_name: str) -> None:
    ui.notify(
        f"Enum '{enum_name}' already exists.",
        type="negative",
    )


def notify_field_exists(field_name: str, model_name: str) -> None:
    ui.notify(
        f"Model' {model_name}' already has field '{field_name}'.",
        type="negative",
    )


def notify_enum_value_exists(value_name: str, enum_name: str) -> None:
    ui.notify(
        f"Enum' {enum_name}' already has value '{value_name}'.",
        type="negative",
    )


def notify_something_went_wrong() -> None:
    ui.notify(
        "Something went wrong...",
        type="warning",
    )
