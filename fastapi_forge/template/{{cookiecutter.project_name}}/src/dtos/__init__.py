from pydantic import BaseModel, ConfigDict, Field
from fastapi import Depends
from uuid import UUID
from typing import Annotated


#############
# Base DTOs #
#############


class BaseOrmModel(BaseModel):
    """Base ORM model."""

    model_config = ConfigDict(from_attributes=True)


######################
# Data Response DTOs #
######################


class DataResponse[T: BaseModel](BaseModel):
    """Model for response data."""

    data: T | None = None


class CreatedResponse(BaseModel):
    """Model for created objects, returning the id."""

    id: UUID


class EmptyResponse(BaseModel):
    """Model for empty response."""

    data: None = None


###################
# Pagination DTOs #
###################


class PaginationParams(BaseModel):
    """DTO for offset pagination."""

    offset: int = Field(0, ge=0)
    limit: int = Field(20, le=20, ge=1)


class PaginationParamsSortBy(PaginationParams):
    """DTO for offset pagination with sorting."""

    sort_by: str
    sort_order: str = "asc"


class OffsetPaginationMetadata(BaseModel):
    """DTO for offset pagination metadata."""

    total: int


class OffsetResults[T: BaseModel](BaseModel):
    """DTO for offset paginated response."""

    data: list[T]
    pagination: OffsetPaginationMetadata


Pagination = Annotated[PaginationParams, Depends()]
