from jinja2 import Template
from .dtos import Model, ModelField, ModelRelationship

model_template = """
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from datetime import datetime
{% for relation in model.relationships -%}
from src.models.{{ relation.target.lower() }}_models import {{ relation.target }}
{% endfor %}


from src.models import Base

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
    {{ relation.target.lower() }}: Mapped[{{ relation.target }}] = relationship(
        "{{ relation.target }}",
        foreign_keys=[{{ relation.foreign_key.lower() }}],
        uselist=False,
    )
        {% endif %}
    {% endfor %}
"""

dto_template = """
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from fastapi import Depends
from uuid import UUID
from typing import Annotated
from src.dtos import BaseOrmModel


class {{ model.name }}DTO(BaseOrmModel):
    \"\"\"{{ model.name }} DTO.\"\"\"

    id: UUID
    {%- for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }}{% if field.nullable %} | None{% endif %}
    {%- endif %}
    {% endfor %}
    created_at: datetime
    updated_at: datetime


class {{ model.name }}InputDTO(BaseModel):
    \"\"\"{{ model.name }} input DTO.\"\"\"

    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }}{% if field.nullable %} | None{% endif %}
    {%- endif %}
    {% endfor %}


class {{ model.name }}UpdateDTO(BaseModel):
    \"\"\"{{ model.name }} update DTO.\"\"\"

    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }} | None = None
    {%- endif %}
    {% endfor %}
"""

dao_template = """
from src.daos import BaseDAO

from src.models.{{ model.name.lower() }}_models import {{ model.name }}
from src.dtos.{{ model.name.lower() }}_dtos import {{ model.name }}InputDTO, {{ model.name }}UpdateDTO


class {{ model.name }}DAO(
    BaseDAO[
        {{ model.name }},
        {{ model.name }}InputDTO,
        {{ model.name }}UpdateDTO,
    ]
):
    \"\"\"{{ model.name }} DAO.\"\"\"
"""

routers_template = """
from fastapi import APIRouter
from src.daos import GetDAOs
from src.dtos.{{ model.name.lower() }}_dtos import {{ model.name }}InputDTO, {{ model.name }}DTO, {{ model.name }}UpdateDTO
from src.dtos import (
    DataResponse,
    Pagination,
    OffsetResults,
    CreatedResponse,
    EmptyResponse,
)
from uuid import UUID

router = APIRouter(prefix="/{{ model.name.lower() }}s")


@router.post("/", status_code=201)
async def create_{{ model.name.lower() }}(
    input_dto: {{ model.name }}InputDTO,
    daos: GetDAOs,
) -> DataResponse[CreatedResponse]:
    \"\"\"Create a new {{ model.name.lower() }}.\"\"\"

    created_id = await daos.{{ model.name.lower() }}.create(input_dto)
    return DataResponse(
        data=CreatedResponse(id=created_id),
    )


@router.patch("/{ {{- model.name.lower() }}_id}")
async def update_{{ model.name.lower() }}(
    {{ model.name.lower() }}_id: UUID,
    update_dto: {{ model.name }}UpdateDTO,
    daos: GetDAOs,
) -> EmptyResponse:
    \"\"\"Update {{ model.name.lower() }}.\"\"\"

    await daos.{{ model.name.lower() }}.update({{ model.name.lower() }}_id, update_dto)
    return EmptyResponse()


@router.delete("/{ {{- model.name.lower() }}_id}")
async def delete_{{ model.name.lower() }}(
    {{ model.name.lower() }}_id: UUID,
    daos: GetDAOs,
) -> EmptyResponse:
    \"\"\"Delete a {{ model.name.lower() }} by id.\"\"\"

    await daos.{{ model.name.lower() }}.delete({{ model.name.lower() }}_id)
    return EmptyResponse()


@router.get("/")
async def get_{{ model.name.lower() }}_paginated(
    daos: GetDAOs,
    pagination: Pagination,
) -> OffsetResults[{{ model.name }}DTO]:
    \"\"\"Get all {{ model.name.lower() }}s paginated.\"\"\"

    return await daos.{{ model.name.lower() }}.get_offset_results(
        out_dto={{ model.name }}DTO,
        pagination=pagination,
    )


@router.get("/{ {{- model.name.lower() }}_id}")
async def get_{{ model.name.lower() }}(
    {{ model.name.lower() }}_id: UUID,
    daos: GetDAOs,
) -> DataResponse[{{ model.name }}DTO]:
    \"\"\"Get a {{ model.name.lower() }} by id.\"\"\"

    {{ model.name.lower() }} = await daos.{{ model.name.lower() }}.filter_first(id={{ model.name.lower() }}_id)
    return DataResponse(data={{ model.name }}DTO.model_validate({{ model.name.lower() }}))
"""

tests_template = """
import pytest
from tests import factories
from src.daos import AllDAOs
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_{{ model.name.lower() }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test create {{ model.name.lower() }}: 201.\"\"\"
"""

TYPE_MAPPING = {
    "Integer": "int",
    "String": "str",
    "UUID": "UUID",
    "DateTime": "datetime",
}


def render_model_to_model(model: Model) -> str:
    return Template(model_template).render(
        model=model,
        type_mapping=TYPE_MAPPING,
    )


def render_model_to_dto(model: Model) -> str:
    return Template(dto_template).render(
        model=model,
        type_mapping=TYPE_MAPPING,
    )


def render_model_to_dao(model: Model) -> str:
    return Template(dao_template).render(
        model=model,
    )


def render_model_to_routers(model: Model) -> str:
    return Template(routers_template).render(
        model=model,
    )


def render_model_to_test(model: Model) -> str:
    return Template(tests_template).render(
        model=model,
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

    print(render_model_to_routers(models[1]))
