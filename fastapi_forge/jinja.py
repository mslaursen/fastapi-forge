from typing import Any
from jinja2 import Environment
from fastapi_forge.dtos import Model, ModelField, ModelRelationship
from fastapi_forge.utils import camel_to_snake, camel_to_snake_hyphen
from fastapi_forge.enums import FieldDataType, RelationshipType


env = Environment()
env.filters["camel_to_snake"] = camel_to_snake
env.filters["camel_to_snake_hyphen"] = camel_to_snake_hyphen

model_template = """
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from datetime import datetime
{% for relation in model.relationships -%}
from src.models.{{ relation.target | camel_to_snake }}_models import {{ relation.target }}
{% endfor %}


from src.db import Base

class {{ model.name }}(Base):
    \"\"\"{{ model.name }} model.\"\"\"

    __tablename__ = "{{ model.name | camel_to_snake }}"
    
    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {% if field.name.endswith('_id') %}
    {{ field.name | camel_to_snake }}: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), sa.ForeignKey("{{ field.foreign_key | camel_to_snake }}", ondelete="CASCADE"),
    )
    {% elif field.nullable %}
    {{ field.name | camel_to_snake }}: Mapped[{{ type_mapping[field.type] }} | None] = mapped_column(
        sa.{% if field.type == 'DateTime' %}DateTime(timezone=True){% else %}{{ field.type }}{% endif %}{% if field.type == 'UUID' %}(as_uuid=True){% endif %}, {% if field.unique == True %}unique=True,{% endif %}
    )
    {% else %}
    {{ field.name | camel_to_snake }}: Mapped[{{ type_mapping[field.type] }}] = mapped_column(
        sa.{% if field.type == 'DateTime' %}DateTime(timezone=True){% else %}{{ field.type }}{% endif %}{% if field.type == 'UUID' %}(as_uuid=True){% endif %}, {% if field.unique == True %}unique=True,{% endif %}
    )
    {% endif %}
    {% endif %}
    {% endfor %}

    {% for relation in model.relationships %}
        {% if relation.type == "ManyToOne" %}
    {{ relation.target | camel_to_snake }}: Mapped[{{ relation.target }}] = relationship(
        "{{ relation.target }}",
        foreign_keys=[{{ relation.field_name }}],
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

from src.models.{{ model.name | camel_to_snake }}_models import {{ model.name }}
from src.dtos.{{ model.name | camel_to_snake }}_dtos import {{ model.name }}InputDTO, {{ model.name }}UpdateDTO


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
from src.dtos.{{ model.name | camel_to_snake  }}_dtos import {{ model.name }}InputDTO, {{ model.name }}DTO, {{ model.name }}UpdateDTO
from src.dtos import (
    DataResponse,
    Pagination,
    OffsetResults,
    CreatedResponse,
    EmptyResponse,
)
from uuid import UUID

router = APIRouter(prefix="/{{ model.name | camel_to_snake_hyphen }}s")


@router.post("/", status_code=201)
async def create_{{ model.name | camel_to_snake }}(
    input_dto: {{ model.name }}InputDTO,
    daos: GetDAOs,
) -> DataResponse[CreatedResponse]:
    \"\"\"Create a new {{ model.name }}.\"\"\"

    created_id = await daos.{{ model.name | camel_to_snake }}.create(input_dto)
    return DataResponse(
        data=CreatedResponse(id=created_id),
    )


@router.patch("/{ {{- model.name | camel_to_snake }}_id}")
async def update_{{ model.name | camel_to_snake }}(
    {{ model.name | camel_to_snake }}_id: UUID,
    update_dto: {{ model.name }}UpdateDTO,
    daos: GetDAOs,
) -> EmptyResponse:
    \"\"\"Update {{ model.name }}.\"\"\"

    await daos.{{ model.name | camel_to_snake }}.update({{ model.name | camel_to_snake }}_id, update_dto)
    return EmptyResponse()


@router.delete("/{ {{- model.name | camel_to_snake }}_id}")
async def delete_{{ model.name | camel_to_snake }}(
    {{ model.name | camel_to_snake }}_id: UUID,
    daos: GetDAOs,
) -> EmptyResponse:
    \"\"\"Delete a {{ model.name }} by id.\"\"\"

    await daos.{{ model.name | camel_to_snake }}.delete(id={{ model.name | camel_to_snake }}_id)
    return EmptyResponse()


@router.get("/")
async def get_{{ model.name | camel_to_snake }}_paginated(
    daos: GetDAOs,
    pagination: Pagination,
) -> OffsetResults[{{ model.name }}DTO]:
    \"\"\"Get all {{ model.name }}s paginated.\"\"\"

    return await daos.{{ model.name | camel_to_snake }}.get_offset_results(
        out_dto={{ model.name }}DTO,
        pagination=pagination,
    )


@router.get("/{ {{- model.name | camel_to_snake }}_id}")
async def get_{{ model.name | camel_to_snake }}(
    {{ model.name | camel_to_snake }}_id: UUID,
    daos: GetDAOs,
) -> DataResponse[{{ model.name }}DTO]:
    \"\"\"Get a {{ model.name }} by id.\"\"\"

    {{ model.name | camel_to_snake }} = await daos.{{ model.name | camel_to_snake }}.filter_first(id={{ model.name | camel_to_snake }}_id)
    return DataResponse(data={{ model.name }}DTO.model_validate({{ model.name | camel_to_snake }}))
"""

test_template_post = """
import pytest
from tests import factories
from src.daos import AllDAOs
from httpx import AsyncClient
from datetime import datetime, timezone
from uuid import UUID

URI = "/api/v1/{{ model.name | camel_to_snake_hyphen }}s/"

@pytest.mark.anyio
async def test_post_{{ model.name | camel_to_snake }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test create {{ model.name }}: 201.\"\"\"

    {%- for relation in model.relationships %}
    {% if relation.type == "ManyToOne" %}
    {{ relation.target | camel_to_snake }} = await factories.{{ relation.target }}Factory.create()
    {% endif %}
    {% endfor %}
    input_json = {
        {%- for field in model.fields -%}
        {%- if not field.primary_key and field.name.endswith('_id') -%}
        "{{ field.name }}": str({{ field.name | camel_to_snake | replace('_id', '.id') }}),
        {%- elif not field.primary_key %}
        {%- if field.type == "DateTime" %}
        "{{ field.name }}": {{ type_to_input_value_mapping[field.type] }}.isoformat(),
        {%- else %}
        "{{ field.name }}": {{ type_to_input_value_mapping[field.type] }},
        {%- endif %}
        {%- endif %}
        {%- endfor %}
    }

    response = await client.post(URI, json=input_json)
    assert response.status_code == 201

    response_data = response.json()["data"]
    db_{{ model.name | camel_to_snake }} = await daos.{{ model.name | camel_to_snake }}.filter_first(id=response_data["id"])

    assert db_{{ model.name | camel_to_snake }} is not None
    {%- for field in model.fields %}
    {%- if not field.primary_key and field.name.endswith('_id') %}
    assert db_{{ model.name | camel_to_snake }}.{{ field.name }} == UUID(input_json["{{ field.name }}"])
    {%- elif not field.primary_key %}
    {%- if field.type == "DateTime" %}
    assert db_{{ model.name | camel_to_snake }}.{{ field.name }}.isoformat() == input_json["{{ field.name }}"]
    {%- else %}
    assert db_{{ model.name | camel_to_snake }}.{{ field.name }} == input_json["{{ field.name }}"]
    {%- endif %}
    {%- endif %}
    {%- endfor %}
"""

test_template_get = """
import pytest
from tests import factories
from httpx import AsyncClient
from datetime import datetime
from uuid import UUID

URI = "/api/v1/{{ model.name | camel_to_snake_hyphen }}s/"

@pytest.mark.anyio
async def test_get_{{ model.name | camel_to_snake }}s(client: AsyncClient,) -> None:
    \"\"\"Test get {{ model.name | camel_to_snake }}: 200.\"\"\"

    {{ model.name | camel_to_snake }}s = await factories.{{ model.name }}Factory.create_batch(3)

    response = await client.get(URI)
    assert response.status_code == 200

    response_data = response.json()["data"]
    assert len(response_data) == 3

    for {{ model.name | camel_to_snake }} in {{ model.name | camel_to_snake }}s:
        assert any({{ model.name | camel_to_snake }}.id == UUID(item["id"]) for item in response_data)
"""

test_template_get_id = """
import pytest
from tests import factories
from httpx import AsyncClient
from datetime import datetime
from uuid import UUID

URI = "/api/v1/{{ model.name | camel_to_snake_hyphen }}s/{ {{- model.name | camel_to_snake -}}_id}"

@pytest.mark.anyio
async def test_get_{{ model.name | camel_to_snake }}_by_id(client: AsyncClient,) -> None:
    \"\"\"Test get {{ model.name | camel_to_snake }} by id: 200.\"\"\"

    {{ model.name | camel_to_snake }} = await factories.{{ model.name }}Factory.create()

    response = await client.get(URI.format({{ model.name | camel_to_snake }}_id={{ model.name | camel_to_snake }}.id))
    assert response.status_code == 200

    response_data = response.json()["data"]
    assert response_data["id"] == str({{ model.name | camel_to_snake }}.id)
    {%- for field in model.fields %}
    {%- if not field.primary_key and field.name.endswith('_id') %}
    assert response_data["{{ field.name }}"] == str({{ model.name | camel_to_snake }}.{{ field.name }})
    {%- elif not field.primary_key %}
    {%- if field.type == "DateTime" %}
    assert response_data["{{ field.name }}"] == {{ model.name | camel_to_snake }}.{{ field.name }}.isoformat()
    {%- else %}
    assert response_data["{{ field.name }}"] == {{ model.name | camel_to_snake }}.{{ field.name }}
    {%- endif %}
    {%- endif %}
    {%- endfor %}
"""

test_template_patch = """
import pytest
from tests import factories
from src.daos import AllDAOs
from httpx import AsyncClient
from datetime import datetime, timezone
from uuid import UUID

URI = "/api/v1/{{ model.name | camel_to_snake_hyphen }}s/{ {{- model.name | camel_to_snake -}}_id}"

@pytest.mark.anyio
async def test_patch_{{ model.name | camel_to_snake }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test patch {{ model.name | camel_to_snake }}: 200.\"\"\"

    {%- for relation in model.relationships %}
    {% if relation.type == "ManyToOne" %}
    {{ relation.target | camel_to_snake }} = await factories.{{ relation.target }}Factory.create()
    {% endif %}
    {% endfor %}
    {{ model.name | camel_to_snake }} = await factories.{{ model.name }}Factory.create()

    input_json = {
        {%- for field in model.fields -%}
        {%- if not field.primary_key and field.name.endswith('_id') -%}
        "{{ field.name }}": str({{ field.name | camel_to_snake | replace('_id', '.id') }}),
        {% elif not field.primary_key %}
        {%- if field.type == "DateTime" %}
        "{{ field.name }}": {{ type_to_input_value_mapping[field.type] }}.isoformat(),
        {%- else %}
        "{{ field.name }}": {{ type_to_input_value_mapping[field.type] }},
        {%- endif %}
        {%- endif %}
        {%- endfor %}
    }

    response = await client.patch(URI.format({{ model.name | camel_to_snake }}_id={{ model.name | camel_to_snake }}.id), json=input_json)
    assert response.status_code == 200

    db_{{ model.name | camel_to_snake }} = await daos.{{ model.name | camel_to_snake }}.filter_first(id={{ model.name | camel_to_snake }}.id)

    assert db_{{ model.name | camel_to_snake }} is not None
    {%- for field in model.fields %}
    {%- if not field.primary_key and field.name.endswith('_id') %}
    assert db_{{ model.name | camel_to_snake }}.{{ field.name }} == UUID(input_json["{{ field.name }}"])
    {%- elif not field.primary_key %}
    {%- if field.type == "DateTime" %}
    assert db_{{ model.name | camel_to_snake }}.{{ field.name }}.isoformat() == input_json["{{ field.name }}"]
    {%- else %}
    assert db_{{ model.name | camel_to_snake }}.{{ field.name }} == input_json["{{ field.name }}"]
    {%- endif %}
    {%- endif %}
    {%- endfor %}

"""

test_template_delete = """
import pytest
from tests import factories
from src.daos import AllDAOs
from httpx import AsyncClient
from datetime import datetime
from uuid import UUID

URI = "/api/v1/{{ model.name | camel_to_snake_hyphen }}s/{ {{- model.name | camel_to_snake -}}_id}"

@pytest.mark.anyio
async def test_delete_{{ model.name | camel_to_snake }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test delete {{ model.name | camel_to_snake }}: 200.\"\"\"

    {{ model.name | camel_to_snake }} = await factories.{{ model.name }}Factory.create()

    response = await client.delete(URI.format({{ model.name | camel_to_snake }}_id={{ model.name | camel_to_snake }}.id))
    assert response.status_code == 200

    db_{{ model.name | camel_to_snake }} = await daos.{{ model.name | camel_to_snake }}.filter_first(id={{ model.name | camel_to_snake }}.id)
    assert db_{{ model.name | camel_to_snake }} is None
"""

TYPE_MAPPING = {
    "Integer": "int",
    "String": "str",
    "UUID": "UUID",
    "DateTime": "datetime",
}

TYPE_TO_INPUT_VALUE_MAPPING = {
    "Integer": "1",
    "String": "'string'",
    "UUID": "UUID('00000000-0000-0000-0000-000000000000')",
    "DateTime": "datetime.now(timezone.utc)",
}


def _render(model: Model, template_name: str, **kwargs: Any) -> str:
    template = env.from_string(template_name)
    return template.render(
        model=model,
        **kwargs,
    )


def render_model_to_model(model: Model) -> str:
    return _render(model, model_template, type_mapping=TYPE_MAPPING)


def render_model_to_dto(model: Model) -> str:
    return _render(model, dto_template, type_mapping=TYPE_MAPPING)


def render_model_to_dao(model: Model) -> str:
    return _render(model, dao_template)


def render_model_to_routers(model: Model) -> str:
    return _render(model, routers_template)


def render_model_to_post_test(model: Model) -> str:
    return _render(
        model,
        test_template_post,
        type_to_input_value_mapping=TYPE_TO_INPUT_VALUE_MAPPING,
    )


def render_model_to_get_test(model: Model) -> str:
    return _render(
        model,
        test_template_get,
        type_to_input_value_mapping=TYPE_TO_INPUT_VALUE_MAPPING,
    )


def render_model_to_get_id_test(model: Model) -> str:
    return _render(
        model,
        test_template_get_id,
        type_to_input_value_mapping=TYPE_TO_INPUT_VALUE_MAPPING,
    )


def render_model_to_patch_test(model: Model) -> str:
    return _render(
        model,
        test_template_patch,
        type_to_input_value_mapping=TYPE_TO_INPUT_VALUE_MAPPING,
    )


def render_model_to_delete_test(model: Model) -> str:
    return _render(
        model,
        test_template_delete,
        type_to_input_value_mapping=TYPE_TO_INPUT_VALUE_MAPPING,
    )


if __name__ == "__main__":
    models = [
        Model(
            name="AppUser",
            fields=[
                ModelField(
                    name="id",
                    type=FieldDataType.UUID,
                    primary_key=True,
                    unique=True,
                ),
                ModelField(
                    name="email",
                    type=FieldDataType.STRING,
                    unique=True,
                    nullable=False,
                ),
                ModelField(
                    name="password",
                    type=FieldDataType.STRING,
                    nullable=False,
                ),
            ],
        ),
        Model(
            name="Reservation",
            fields=[
                ModelField(
                    name="id",
                    type=FieldDataType.UUID,
                    primary_key=True,
                    unique=True,
                ),
                ModelField(
                    name="reservation_date",
                    type=FieldDataType.DATETIME,
                    nullable=False,
                ),
                ModelField(
                    name="party_size",
                    type=FieldDataType.INTEGER,
                    nullable=False,
                ),
                ModelField(
                    name="notes",
                    type=FieldDataType.STRING,
                    nullable=True,
                ),
                ModelField(
                    name="app_user_id",
                    type=FieldDataType.UUID,
                    foreign_key="AppUser.id",
                    nullable=False,
                ),
            ],
            relationships=[
                ModelRelationship(
                    type=RelationshipType.MANY_TO_ONE,
                    target="AppUser",
                )
            ],
        ),
    ]

    render_funcs = [
        render_model_to_model,
        render_model_to_dto,
        render_model_to_dao,
        render_model_to_routers,
        render_model_to_post_test,
        render_model_to_get_test,
        render_model_to_get_id_test,
        render_model_to_patch_test,
        render_model_to_delete_test,
    ]

    for fn in render_funcs:
        print()
        print("=" * 80)
        print(fn.__name__)
        print("=" * 80)
        print()

        print(fn(models[0]))
