from typing import Any
from jinja2 import Environment
from fastapi_forge.dtos import Model, ModelField, ModelRelationship
from fastapi_forge.enums import FieldDataType
from fastapi_forge.jinja_utils import generate_relationship, generate_field


env = Environment()
env.filters["generate_relationship"] = generate_relationship
env.filters["generate_field"] = generate_field

model_template = """
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from typing import Any, Annotated
from datetime import datetime
{% for relation in model.relationships -%}
from src.models.{{ relation.field_name_no_id }}_models import {{ relation.target }}
{% endfor %}


from src.db import Base

class {{ model.name_cc }}(Base):
    \"\"\"{{ model.name_cc }} model.\"\"\"

    __tablename__ = "{{ model.name }}"
    
    {% for field in model.fields -%}
    {{ field | generate_field }}
    {% endfor %}

    {% for relation in model.relationships %}
    {{ relation | generate_relationship }}
    {% endfor %}
"""

dto_template = """
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from fastapi import Depends
from uuid import UUID
from typing import Annotated, Any
from src.dtos import BaseOrmModel


class {{ model.name_cc }}DTO(BaseOrmModel):
    \"\"\"{{ model.name_cc }} DTO.\"\"\"

    id: UUID
    {%- for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }}{% if field.nullable %} | None{% endif %}
    {%- endif %}
    {% endfor %}
    created_at: datetime
    updated_at: datetime


class {{ model.name_cc }}InputDTO(BaseModel):
    \"\"\"{{ model.name_cc }} input DTO.\"\"\"

    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }}{% if field.nullable %} | None{% endif %}
    {%- endif %}
    {% endfor %}


class {{ model.name_cc }}UpdateDTO(BaseModel):
    \"\"\"{{ model.name_cc }} update DTO.\"\"\"

    {% for field in model.fields -%}
    {% if not field.primary_key -%}
    {{ field.name }}: {{ type_mapping[field.type] }} | None = None
    {%- endif %}
    {% endfor %}
"""

dao_template = """
from src.daos import BaseDAO

from src.models.{{ model.name }}_models import {{ model.name_cc }}
from src.dtos.{{ model.name }}_dtos import {{ model.name_cc }}InputDTO, {{ model.name_cc }}UpdateDTO


class {{ model.name_cc }}DAO(
    BaseDAO[
        {{ model.name_cc }},
        {{ model.name_cc }}InputDTO,
        {{ model.name_cc }}UpdateDTO,
    ]
):
    \"\"\"{{ model.name_cc }} DAO.\"\"\"
"""

routers_template = """
from fastapi import APIRouter
from src.daos import GetDAOs
from src.dtos.{{ model.name  }}_dtos import {{ model.name_cc }}InputDTO, {{ model.name_cc }}DTO, {{ model.name_cc }}UpdateDTO
from src.dtos import (
    DataResponse,
    Pagination,
    OffsetResults,
    CreatedResponse,
    EmptyResponse,
)
from uuid import UUID

router = APIRouter(prefix="/{{ model.name_hyphen }}s")


@router.post("/", status_code=201)
async def create_{{ model.name }}(
    input_dto: {{ model.name_cc }}InputDTO,
    daos: GetDAOs,
) -> DataResponse[CreatedResponse]:
    \"\"\"Create a new {{ model.name_cc }}.\"\"\"

    created_id = await daos.{{ model.name }}.create(input_dto)
    return DataResponse(
        data=CreatedResponse(id=created_id),
    )


@router.patch("/{ {{- model.name }}_id}")
async def update_{{ model.name }}(
    {{ model.name }}_id: UUID,
    update_dto: {{ model.name_cc }}UpdateDTO,
    daos: GetDAOs,
) -> EmptyResponse:
    \"\"\"Update {{ model.name_cc }}.\"\"\"

    await daos.{{ model.name }}.update({{ model.name }}_id, update_dto)
    return EmptyResponse()


@router.delete("/{ {{- model.name }}_id}")
async def delete_{{ model.name }}(
    {{ model.name }}_id: UUID,
    daos: GetDAOs,
) -> EmptyResponse:
    \"\"\"Delete a {{ model.name_cc }} by id.\"\"\"

    await daos.{{ model.name }}.delete(id={{ model.name }}_id)
    return EmptyResponse()


@router.get("/")
async def get_{{ model.name }}_paginated(
    daos: GetDAOs,
    pagination: Pagination,
) -> OffsetResults[{{ model.name_cc }}DTO]:
    \"\"\"Get all {{ model.name_cc }}s paginated.\"\"\"

    return await daos.{{ model.name }}.get_offset_results(
        out_dto={{ model.name_cc }}DTO,
        pagination=pagination,
    )


@router.get("/{ {{- model.name }}_id}")
async def get_{{ model.name }}(
    {{ model.name }}_id: UUID,
    daos: GetDAOs,
) -> DataResponse[{{ model.name_cc }}DTO]:
    \"\"\"Get a {{ model.name_cc }} by id.\"\"\"

    {{ model.name }} = await daos.{{ model.name }}.filter_first(id={{ model.name }}_id)
    return DataResponse(data={{ model.name_cc }}DTO.model_validate({{ model.name }}))
"""

test_template_post = """
import pytest
from tests import factories
from src.daos import AllDAOs
from httpx import AsyncClient
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

URI = "/api/v1/{{ model.name_hyphen }}s/"

@pytest.mark.anyio
async def test_post_{{ model.name }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test create {{ model.name_cc }}: 201.\"\"\"

    {%- for relation in model.relationships %}
    {{ relation.field_name_no_id }} = await factories.{{ relation.target }}Factory.create()
    {% endfor %}
    input_json = {
        {%- for field in model.fields -%}
        {%- if not field.primary_key and field.name.endswith('_id') -%}
        "{{ field.name }}": str({{ field.name | replace('_id', '.id') }}),
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
    db_{{ model.name }} = await daos.{{ model.name }}.filter_first(id=response_data["id"])

    assert db_{{ model.name }} is not None
    {%- for field in model.fields %}
    {%- if not field.primary_key and field.name.endswith('_id') %}
    assert db_{{ model.name }}.{{ field.name }} == UUID(input_json["{{ field.name }}"])
    {%- elif not field.primary_key %}
    {%- if field.type == "DateTime" %}
    assert db_{{ model.name }}.{{ field.name }}.isoformat() == input_json["{{ field.name }}"]
    {%- else %}
    assert db_{{ model.name }}.{{ field.name }} == input_json["{{ field.name }}"]
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

URI = "/api/v1/{{ model.name_hyphen }}s/"

@pytest.mark.anyio
async def test_get_{{ model.name }}s(client: AsyncClient,) -> None:
    \"\"\"Test get {{ model.name_cc }}: 200.\"\"\"

    {{ model.name }}s = await factories.{{ model.name_cc }}Factory.create_batch(3)

    response = await client.get(URI)
    assert response.status_code == 200

    response_data = response.json()["data"]
    assert len(response_data) == 3

    for {{ model.name }} in {{ model.name }}s:
        assert any({{ model.name }}.id == UUID(item["id"]) for item in response_data)
"""

test_template_get_id = """
import pytest
from tests import factories
from httpx import AsyncClient
from datetime import datetime
from uuid import UUID

URI = "/api/v1/{{ model.name_hyphen }}s/{ {{- model.name -}}_id}"

@pytest.mark.anyio
async def test_get_{{ model.name }}_by_id(client: AsyncClient,) -> None:
    \"\"\"Test get {{ model.name }} by id: 200.\"\"\"

    {{ model.name }} = await factories.{{ model.name_cc }}Factory.create()

    response = await client.get(URI.format({{ model.name }}_id={{ model.name }}.id))
    assert response.status_code == 200

    response_data = response.json()["data"]
    assert response_data["id"] == str({{ model.name }}.id)
    {%- for field in model.fields %}
    {%- if not field.primary_key and field.name.endswith('_id') %}
    assert response_data["{{ field.name }}"] == str({{ model.name }}.{{ field.name }})
    {%- elif not field.primary_key %}
    {%- if field.type == "DateTime" %}
    assert response_data["{{ field.name }}"] == {{ model.name }}.{{ field.name }}.isoformat()
    {%- else %}
    assert response_data["{{ field.name }}"] == {{ model.name }}.{{ field.name }}
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
from typing import Any
from uuid import UUID

URI = "/api/v1/{{ model.name_hyphen }}s/{ {{- model.name -}}_id}"

@pytest.mark.anyio
async def test_patch_{{ model.name }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test patch {{ model.name_cc }}: 200.\"\"\"

    {%- for relation in model.relationships %}
    {{ relation.field_name_no_id }} = await factories.{{ relation.target }}Factory.create()
    {% endfor %}
    {{ model.name }} = await factories.{{ model.name_cc }}Factory.create()

    input_json = {
        {%- for field in model.fields -%}
        {%- if not field.primary_key and field.name.endswith('_id') -%}
        "{{ field.name }}": str({{ field.name | replace('_id', '.id') }}),
        {% elif not field.primary_key %}
        {%- if field.type == "DateTime" %}
        "{{ field.name }}": {{ type_to_input_value_mapping[field.type] }}.isoformat(),
        {%- else %}
        "{{ field.name }}": {{ type_to_input_value_mapping[field.type] }},
        {%- endif %}
        {%- endif %}
        {%- endfor %}
    }

    response = await client.patch(URI.format({{ model.name }}_id={{ model.name }}.id), json=input_json)
    assert response.status_code == 200

    db_{{ model.name }} = await daos.{{ model.name }}.filter_first(id={{ model.name }}.id)

    assert db_{{ model.name }} is not None
    {%- for field in model.fields %}
    {%- if not field.primary_key and field.name.endswith('_id') %}
    assert db_{{ model.name }}.{{ field.name }} == UUID(input_json["{{ field.name }}"])
    {%- elif not field.primary_key %}
    {%- if field.type == "DateTime" %}
    assert db_{{ model.name }}.{{ field.name }}.isoformat() == input_json["{{ field.name }}"]
    {%- else %}
    assert db_{{ model.name }}.{{ field.name }} == input_json["{{ field.name }}"]
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

URI = "/api/v1/{{ model.name_hyphen }}s/{ {{- model.name -}}_id}"

@pytest.mark.anyio
async def test_delete_{{ model.name }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test delete {{ model.name_cc }}: 200.\"\"\"

    {{ model.name }} = await factories.{{ model.name_cc }}Factory.create()

    response = await client.delete(URI.format({{ model.name }}_id={{ model.name }}.id))
    assert response.status_code == 200

    db_{{ model.name }} = await daos.{{ model.name }}.filter_first(id={{ model.name }}.id)
    assert db_{{ model.name }} is None
"""

TYPE_MAPPING = {
    "Integer": "int",
    "String": "str",
    "UUID": "UUID",
    "DateTime": "datetime",
    "JSONB": "dict[str, Any]",
}

TYPE_TO_INPUT_VALUE_MAPPING = {
    "Integer": "1",
    "String": "'string'",
    "UUID": "UUID('00000000-0000-0000-0000-000000000000')",
    "DateTime": "datetime.now(timezone.utc)",
    "JSONB": '{"json": "value"}',
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
            name="auth_user",
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
            name="reservation",
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
                    name="auth_user_id",
                    type=FieldDataType.UUID,
                    foreign_key="AuthUser.id",
                    nullable=False,
                ),
            ],
            relationships=[
                ModelRelationship(
                    field_name="auth_user_id",
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

        print(fn(models[1]))
