TEST_GET_TEMPLATE = """
import pytest
from tests import factories
from httpx import AsyncClient
from datetime import datetime, timezone,  timedelta


from uuid import UUID

URI = "/api/v1/{{ model.name_plural_hyphen }}/"

@pytest.mark.anyio
async def test_get_{{ model.name_plural }}(client: AsyncClient,) -> None:
    \"\"\"Test get {{ model.name_cc }}: 200.\"\"\"

    {{ model.name_plural }} = await factories.{{ model.name_cc }}Factory.create_batch(3)

    response = await client.get(URI)
    assert response.status_code == 200

    response_data = response.json()["data"]
    assert len(response_data) == 3

    for {{ model.name }},  data in zip({{ model.name_plural }}, response_data, strict=True):
        {% for field in model.primary_key_fields %}
        assert {{ model.name }}.{{ field.name }} == {% if field.type_info.encapsulate_assert %}{{ field.type_info.encapsulate_assert }}(data["{{ field.name }}"]){% else %}data["{{ field.name }}"]{% endif %}
        {%- endfor %}
"""


TEST_GET_ID_TEMPLATE = """
import pytest
from tests import factories
from httpx import AsyncClient
from datetime import datetime, timezone,  timedelta


from uuid import UUID

URI = "/api/v1/{{ model.name_plural_hyphen }}/{ {{- model.name -}}_id}"

@pytest.mark.anyio
async def test_get_{{ model.name }}_by_id(client: AsyncClient,) -> None:
    \"\"\"Test get {{ model.name }} by id: 200.\"\"\"

    {{ model.name }} = await factories.{{ model.name_cc }}Factory.create()

    response = await client.get(URI.format({{ model.name }}_id={{ model.name }}.{{ model.primary_key.name }}))
    assert response.status_code == 200

    response_data = response.json()["data"]
    assert response_data["{{ model.primary_key.name }}"] == str({{ model.name }}.{{ model.primary_key.name }})
    {%- for field in model.fields %}
    {%- if not field.primary_key and field.name.endswith('_id') %}
    assert response_data["{{ field.name }}"] == str({{ model.name }}.{{ field.name }})
    {%- elif not field.primary_key %}
    assert response_data["{{ field.name }}"] == {{ model.name }}.{{ field.name }}{{ field.type_info.test_func if field.type_info.test_func else '' }}
    {%- endif %}
    {%- endfor %}
"""

TEST_POST_TEMPLATE = """
import pytest
from tests import factories
from {{ project_name }}.daos import AllDAOs
from {{ project_name }} import enums
from httpx import AsyncClient
from datetime import datetime, timezone,  timedelta
from uuid import uuid4


from typing import Any
from uuid import UUID

URI = "/api/v1/{{ model.name_plural_hyphen }}/"

@pytest.mark.anyio
async def test_post_{{ model.name }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test create {{ model.name_cc }}: 201.\"\"\"

    {%- for relation in model.relationships %}
    {{ relation.field_name_no_id }} = await factories.{{ relation.target }}Factory.create()
    {%- endfor %}

    input_json = {
        {%- for field in model.fields  if not (field.metadata.is_created_at_timestamp or field.metadata.is_updated_at_timestamp or not field.type_info.test_value) -%}
        {% if field.metadata.is_foreign_key %}
        "{{ field.name }}": str({{ field.name | replace('_id', '.id') }}),
        {% else %}
        "{{ field.name }}": {{ field.type_info.test_value }}{{ field.type_info.test_func if field.type_info.test_func else '' }},
        {% endif %}
        {%- endfor %}
    }

    response = await client.post(URI, json=input_json)
    assert response.status_code == 201

    response_data = response.json()["data"]
    db_{{ model.name }} = await daos.{{ model.name }}.filter_first(
        {% for field in model.primary_key_fields %}
        {{ field.name }}=response_data["{{ field.name }}"],
        {%- endfor %}
    )

    assert db_{{ model.name }} is not None
    {%- for field in model.fields if not (field.metadata.is_created_at_timestamp or field.metadata.is_updated_at_timestamp or field.primary_key or not field.type_info.test_value) %}
    {%- if not field.primary_key and field.metadata.is_foreign_key %}
        {%- if field.type_info.encapsulate_assert %}
    assert db_{{ model.name }}.{{ field.name }} == {{ field.type_info.encapsulate_assert }}(input_json["{{ field.name }}"])
        {%- else %}
    assert db_{{ model.name }}.{{ field.name }} == input_json["{{ field.name }}"]
        {%- endif %}
    {%- elif not field.primary_key %}
        {%- if field.type_info.encapsulate_assert %}
    assert db_{{ model.name }}.{{ field.name }}{{ field.type_info.test_func if field.type_info.test_func else '' }} == {{ field.type_info.encapsulate_assert }}(input_json["{{ field.name }}"])
        {%- else %}
    assert db_{{ model.name }}.{{ field.name }}{{ field.type_info.test_func if field.type_info.test_func else '' }} == input_json["{{ field.name }}"]
        {%- endif %}
    {%- endif %}
    {%- endfor %}
"""

TEST_PATCH_TEMPLATE = """
import pytest
from tests import factories
from {{ project_name }}.daos import AllDAOs
from {{ project_name }} import enums
from httpx import AsyncClient
from datetime import datetime, timezone,  timedelta
from uuid import uuid4


from typing import Any
from uuid import UUID

URI = "/api/v1/{{ model.name_plural_hyphen }}/{ {{- model.name -}}_id}"

@pytest.mark.anyio
async def test_patch_{{ model.name }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test patch {{ model.name_cc }}: 200.\"\"\"

    {%- for relation in model.relationships %}
    {{ relation.field_name_no_id }} = await factories.{{ relation.target }}Factory.create()
    {%- endfor %}
    {{ model.name }} = await factories.{{ model.name_cc }}Factory.create()

    input_json = {
        {%- for field in model.fields  if not (field.metadata.is_created_at_timestamp or field.metadata.is_updated_at_timestamp or field.primary_key or not field.type_info.test_value) -%}
        {%- if not field.primary_key and field.name.endswith('_id') and field.metadata.is_foreign_key -%}
        "{{ field.name }}": str({{ field.name | replace('_id', '.id') }}),
        {% elif not field.primary_key %}
        "{{ field.name }}": {{ field.type_info.test_value }}{{ field.type_info.test_func if field.type_info.test_func else '' }},
        {%- endif %}
        {%- endfor %}
    }

    response = await client.patch(URI.format({{ model.name }}_id={{ model.name }}.{{ model.primary_key.name }}), json=input_json)
    assert response.status_code == 200

    db_{{ model.name }} = await daos.{{ model.name }}.filter_first({{ model.primary_key.name }}={{ model.name }}.{{ model.primary_key.name }})

    assert db_{{ model.name }} is not None
    {%- for field in model.fields if not (field.metadata.is_created_at_timestamp or field.metadata.is_updated_at_timestamp or field.primary_key or not field.type_info.test_value) %}
    {%- if not field.primary_key and field.metadata.is_foreign_key %}
        {%- if field.type_info.encapsulate_assert %}
    assert db_{{ model.name }}.{{ field.name }} == {{ field.type_info.encapsulate_assert }}(input_json["{{ field.name }}"])
        {%- else %}
    assert db_{{ model.name }}.{{ field.name }} == UUID(input_json["{{ field.name }}"])
        {%- endif %}
    {%- elif not field.primary_key %}
        {%- if field.type_info.encapsulate_assert %}
    assert db_{{ model.name }}.{{ field.name }}{{ field.type_info.test_func if field.type_info.test_func else '' }} == {{ field.type_info.encapsulate_assert }}(input_json["{{ field.name }}"])
        {%- else %}
    assert db_{{ model.name }}.{{ field.name }}{{ field.type_info.test_func if field.type_info.test_func else '' }} == input_json["{{ field.name }}"]
        {%- endif %}
    {%- endif %}
    {%- endfor %}

"""

TEST_DELETE_TEMPLATE = """
import pytest
from tests import factories
from {{ project_name }}.daos import AllDAOs
from httpx import AsyncClient
from datetime import datetime, timezone,  timedelta


from uuid import UUID

URI = "/api/v1/{{ model.name_plural_hyphen }}/{ {{- model.name -}}_id}"

@pytest.mark.anyio
async def test_delete_{{ model.name }}(client: AsyncClient, daos: AllDAOs,) -> None:
    \"\"\"Test delete {{ model.name_cc }}: 200.\"\"\"

    {{ model.name }} = await factories.{{ model.name_cc }}Factory.create()

    response = await client.delete(URI.format({{ model.name }}_id={{ model.name }}.{{ model.primary_key.name }}))
    assert response.status_code == 200

    db_{{ model.name }} = await daos.{{ model.name }}.filter_first({{ model.primary_key.name }}={{ model.name }}.{{ model.primary_key.name }})
    assert db_{{ model.name }} is None
"""
