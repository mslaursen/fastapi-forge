from jinja2 import Template
from .dtos import Model, ModelField, ModelRelationship

model_template = """
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from datetime import datetime

from src.db import Base

{% for model in models %}
class {{ model.name }}(Base):
    \"\"\"{{ model.name.title() }} model.\"\"\"

    __tablename__ = "{{ model.name.lower() }}"
    
    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {% if field.name.endswith('_id') %}
    {{ field.name }}: Mapped[UUID] = mapped_column(
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

dto_template = """
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID


#############
# Base DTOs #
#############

class BaseOrmModel(BaseModel):
    \"\"\"Base ORM model.\"\"\"

    model_config = ConfigDict(from_attributes=True)

    
######################
# Data Response DTOs #
######################

class DataResponse[T: BaseModel](BaseModel):
    \"\"\"Model for response data.\"\"\"

    data: T | None = None


class CreatedResponse(BaseModel):
    \"\"\"Model for created objects, returning the id.\"\"\"

    id: UUID


#############
# Core DTOs #
#############


{% for model in models %}
class {{ model.name }}DTO(BaseOrmModel):
    \"\"\"{{ model.name }} DTO.\"\"\"

    id: UUID
    {%- for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }}{% if field.nullable %} | None{% endif %}
    {%- endif %}
    {% endfor %}


class {{ model.name }}InputDTO(BaseOrmModel):
    \"\"\"{{ model.name }} input DTO.\"\"\"

    
    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }}{% if field.nullable %} | None{% endif %}
    {%- endif %}
    {% endfor %}


class {{ model.name }}UpdateDTO(BaseOrmModel):
    \"\"\"{{ model.name }} update DTO.\"\"\"

    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }} | None
    {%- endif %}
    {% endfor %}
{% endfor %}

"""

TYPE_MAPPING = {
    "Integer": "int",
    "String": "str",
    "UUID": "UUID",
    "DateTime": "datetime",
}


def render_models_to_models(models: list[Model]) -> str:
    return Template(model_template).render(
        models=models,
        type_mapping=TYPE_MAPPING,
    )


def render_models_to_dtos(models: list[Model]) -> str:
    return Template(dto_template).render(
        models=models,
        type_mapping=TYPE_MAPPING,
    )


if __name__ == "__main__":
    models = [
        Model(
            name="User",
            fields=[
                ModelField(name="id", type="UUID", primary_key=True),
                ModelField(name="name", type="String", nullable=False),
                ModelField(name="email", type="String", unique=True),
                ModelField(name="birth_date", type="DateTime"),
            ],
            relationships=[
                ModelRelationship(
                    type="OneToMany", target="Post", foreign_key="user_id"
                )
            ],
        ),
        Model(
            name="Post",
            fields=[
                ModelField(name="id", type="UUID", primary_key=True),
                ModelField(name="title", type="String", nullable=False),
                ModelField(name="user_id", type="UUID", foreign_key="User.id"),
            ],
            relationships=[
                ModelRelationship(
                    type="ManyToOne", target="User", foreign_key="user_id"
                )
            ],
        ),
    ]

    print(render_models_to_models(models))
