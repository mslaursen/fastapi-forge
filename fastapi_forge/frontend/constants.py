from typing import Any

SELECTED_MODEL_TEXT_COLOR = "text-black-500 dark:text-amber-300"

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
        "name": "back_populates",
        "label": "Back Populates",
        "field": "back_populates",
        "align": "left",
    },
    {"name": "nullable", "label": "Nullable", "field": "nullable", "align": "center"},
    {"name": "index", "label": "Index", "field": "index", "align": "center"},
    {"name": "unique", "label": "Unique", "field": "unique", "align": "center"},
]
