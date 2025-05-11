ROUTERS_TEMPLATE = """
from fastapi import APIRouter
from {{ project_name }}.daos import GetDAOs
from {{ project_name }}.dtos.{{ model.name  }}_dtos import {{ model.name_cc }}InputDTO, {{ model.name_cc }}DTO, {{ model.name_cc }}UpdateDTO
from {{ project_name }}.dtos import (
    DataResponse,
    Pagination,
    OffsetResults,
    CreatedResponse,
    EmptyResponse,
)
from uuid import UUID

router = APIRouter(prefix="/{{ model.name_plural_hyphen }}")


@router.post("/", status_code=201)
async def create_{{ model.name }}(
    input_dto: {{ model.name_cc }}InputDTO,
    daos: GetDAOs,
) -> DataResponse[{{ model.name_cc }}DTO]:
    \"\"\"Create a new {{ model.name_cc }}.\"\"\"

    created_obj = await daos.{{ model.name }}.create(input_dto)
    return DataResponse(
        data={{ model.name_cc }}DTO.model_validate(created_obj)
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

    await daos.{{ model.name }}.delete({{ model.primary_key.name }}={{ model.name }}_id)
    return EmptyResponse()


@router.get("/")
async def get_{{ model.name }}_paginated(
    daos: GetDAOs,
    pagination: Pagination,
) -> OffsetResults[{{ model.name_cc }}DTO]:
    \"\"\"Get all {{ model.name_plural_cc }} paginated.\"\"\"

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

    {{ model.name }} = await daos.{{ model.name }}.filter_first({{ model.primary_key.name }}={{ model.name }}_id)
    return DataResponse(data={{ model.name_cc }}DTO.model_validate({{ model.name }}))
"""
