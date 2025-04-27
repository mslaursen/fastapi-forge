from typing import Any

from fastapi_forge.enums import FieldDataTypeEnum
from fastapi_forge.schemas import ModelField

SELECTED_MODEL_TEXT_COLOR = "text-black-500 dark:text-amber-300"
SELECTED_ENUM_TEXT_COLOR = "text-black-500 dark:text-amber-300"
ITEM_ROW_TRUNCATE_LEN = 17

FIELD_COLUMNS: list[dict[str, Any]] = [
    {
        "name": "name",
        "label": "Name",
        "field": "name",
        "required": True,
        "align": "left",
    },
    {"name": "type", "label": "Type", "field": "type", "align": "left"},
    {
        "name": "primary_key",
        "label": "Primary Key",
        "field": "primary_key",
        "align": "center",
    },
    {"name": "nullable", "label": "Nullable", "field": "nullable", "align": "center"},
    {"name": "unique", "label": "Unique", "field": "unique", "align": "center"},
    {"name": "index", "label": "Index", "field": "index", "align": "center"},
]

ENUM_COLUMNS: list[dict[str, Any]] = [
    {
        "name": "name",
        "label": "Name",
        "field": "name",
        "required": True,
        "align": "left",
    },
    {
        "name": "value",
        "label": "Value",
        "field": "value",
        "required": True,
        "align": "left",
    },
]

RELATIONSHIP_COLUMNS: list[dict[str, Any]] = [
    {
        "name": "field_name",
        "label": "Field Name",
        "field": "field_name",
        "required": True,
        "align": "left",
    },
    {
        "name": "target_model",
        "label": "Target Model",
        "field": "target_model",
        "align": "left",
    },
    {
        "name": "on_delete",
        "label": "On Delete",
        "field": "on_delete",
        "align": "left",
    },
    {"name": "nullable", "label": "Nullable", "field": "nullable", "align": "center"},
    {"name": "index", "label": "Index", "field": "index", "align": "center"},
    {"name": "unique", "label": "Unique", "field": "unique", "align": "center"},
]


DEFAULT_AUTH_USER_FIELDS: list[ModelField] = [
    ModelField(
        name="email",
        type=FieldDataTypeEnum.STRING,
        unique=True,
        index=True,
    ),
    ModelField(
        name="password",
        type=FieldDataTypeEnum.STRING,
    ),
]
DEFAULT_AUTH_USER_ROLE_ENUM_NAME = "UserRole"
