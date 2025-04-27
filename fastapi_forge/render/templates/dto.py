DTO_TEMPLATE = """
from datetime import datetime, timezone,  timedelta


from pydantic import BaseModel, ConfigDict, Field
from fastapi import Depends
from uuid import UUID
from typing import Annotated, Any
from {{ project_name }}.dtos import BaseOrmModel
from {{ project_name }} import enums


class {{ model.name_cc }}DTO(BaseOrmModel):
    \"\"\"{{ model.name_cc }} DTO.\"\"\"

    id: UUID
    {% for field in model.fields_sorted if not field.primary_key -%}
    {{ field.name }}: {{ field.type_info.python_type }}{% if field.nullable %} | None{% endif %}
    {% endfor %}



class {{ model.name_cc }}InputDTO(BaseModel):
    \"\"\"{{ model.name_cc }} input DTO.\"\"\"

    {% for field in model.fields_sorted if not (field.metadata.is_created_at_timestamp or field.metadata.is_updated_at_timestamp or field.primary_key) -%}
    {{ field.name }}: {{ field.type_info.python_type }}{% if field.nullable %} | None{% endif %}
    {% endfor %}


class {{ model.name_cc }}UpdateDTO(BaseModel):
    \"\"\"{{ model.name_cc }} update DTO.\"\"\"

    {% for field in model.fields_sorted if not (field.metadata.is_created_at_timestamp or field.metadata.is_updated_at_timestamp or field.primary_key) -%}
    {{ field.name }}: {{ field.type_info.python_type }} | None = None
    {% endfor %}
"""
