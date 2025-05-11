MODEL_TEMPLATE = """
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
import uuid
from typing import Any, Annotated
from datetime import datetime, timezone,  timedelta
from {{ project_name }} import enums


{% set unique_relationships = model.relationships | unique(attribute='target') %}
{% for relation in unique_relationships if relation.target != model.name_cc -%}
from {{ project_name }}.models.{{ relation.target_model }}_models import {{ relation.target }}
{% endfor %}


from {{ project_name }}.db import Base

class {{ model.name_cc }}(Base):
    \"\"\"{{ model.name_cc }} model.\"\"\"

    __tablename__ = "{{ model.name }}"

    {% for field in model.fields_sorted -%}
    {{ field | generate_field(model.relationships if field.metadata.is_foreign_key else None) }}
    {% endfor %}

    {% for relation in model.relationships -%}
    {{ relation | generate_relationship(model.name_cc == relation.target) }}
    {% endfor %}

    {{ model.table_args }}
"""
