from jinja2 import Template
from typing import Any

TYPE_MAPPING = {
    "Integer": "int",
    "String": "str",
    "UUID": "uuid.UUID",
    "DateTime": "datetime.datetime",
}

model_template = """
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import datetime

from src.db import Base

{% for model in models %}
class {{ model.name }}(Base):
    \"\"\"{{ model.name.title() }} model.\"\"\"

    __tablename__ = "{{ model.name.lower() }}"
    
    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {% if field.name.endswith('_id') %}
    {{ field.name }}: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), sa.ForeignKey("{{ field.foreign_key.lower() }}", ondelete="CASCADE"),
    )
    {% elif field.nullable %}
    {{ field.name }}: Mapped[{{ type_mapping[field.type] }} | None] = mapped_column(
        sa.{% if field.type == 'DateTime' %}DateTime(timezone=True){% else %}{{ field.type }}{% endif %}{% if field.type == 'UUID' %}(as_uuid=True){% endif %}, {% if field.unique == True %}unique=True,{% endif %}
    )
    {% else %}
    {{ field.name }}: Mapped[{{ type_mapping[field.type] }}] = mapped_column(
        sa.{% if field.type == 'DateTime' %}DateTime(timezone=True){% else %}{{ field.type }}{% endif %}{% if field.type == 'UUID' %}(as_uuid=True){% endif %}, {% if field.unique == True %}unique=True,{% endif %}
    )
    {% endif %}
    {% endif %}
    {% endfor %}

    {% for relation in model.relationships %}
        {% if relation.type == "ManyToOne" %}
    {{ relation.target.lower() }}: Mapped["{{ relation.target }}"] = relationship(
        "{{ relation.target }}",
        foreign_keys=[{{ relation.foreign_key.lower() }}],
        uselist=False,
    )
        {% endif %}
    {% endfor %}

{% endfor %}
"""


def render_models(models_data: list[dict[str, Any]]) -> str:
    return Template(model_template).render(
        models=models_data, type_mapping=TYPE_MAPPING
    )


if __name__ == "__main__":
    models_data = [
        {
            "name": "User",
            "fields": [
                {"name": "id", "type": "Integer", "primary_key": True},
                {"name": "birth_date", "type": "DateTime"},
                {"name": "name", "type": "String", "nullable": False},
                {"name": "nickname", "type": "String", "nullable": True},
                {"name": "email", "type": "String", "unique": True},
            ],
            "relationships": [
                {"type": "OneToMany", "target": "Post", "foreign_key": "user_id"}
            ],
        },
        {
            "name": "Post",
            "fields": [
                {"name": "id", "type": "UUID", "primary_key": True},
                {"name": "title", "type": "String", "nullable": False},
                {"name": "user_id", "type": "UUID", "foreign_key": "User.id"},
            ],
            "relationships": [
                {"type": "ManyToOne", "target": "User", "foreign_key": "user_id"}
            ],
        },
    ]
    print(render_models(models_data))
