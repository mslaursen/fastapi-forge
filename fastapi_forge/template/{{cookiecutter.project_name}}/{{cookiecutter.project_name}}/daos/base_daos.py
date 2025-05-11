from typing import Any, Sequence
from pydantic import BaseModel
from sqlalchemy.ext.asyncio.session import AsyncSession

from {{cookiecutter.project_name}}.db import Base
from {{cookiecutter.project_name}}.dtos import (
    OffsetPaginationMetadata,
    PaginationParams,
    PaginationParamsSortBy,
    OffsetResults,
)
from uuid import UUID, uuid4
from typing import get_args
from types import get_original_bases
import sqlalchemy as sa


PaginationType = PaginationParams | PaginationParamsSortBy
QueryType = sa.Select[Any] | sa.Update | sa.Delete


class BaseDAO[
    Model: Base,
    InputDTO: BaseModel,
    UpdateDTO: BaseModel,
]:
    """
    Base class for all Data Access Objects (DAOs).

    Inherit from this class to create a new DAO that provides CRUD operations
    for a specific model.

    Example:
        To create a new DAO for a model called `User`, define a new class like so:

        >>> class UserDAO(BaseDAO[User, UserInputDTO, UserUpdateDTO]):
        >>>     ...
    """

    model: type[Model]

    def __init_subclass__(
        cls,
    ) -> None:
        base = get_original_bases(cls)[0]
        cls.model = get_args(base)[0]

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    ###################
    # Private methods #
    ###################

    def _apply_param_filters[
        T: QueryType,
    ](self, query: T, **filter_params: Any) -> T:
        """Apply filters to query."""
        for key, value in filter_params.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)  # type: ignore
            else:
                raise ValueError(f"Invalid filter parameter: {key}")
        return query

    def _apply_base_filter(
        self,
        query: sa.Select[Any] | None = None,
        loads: list[Any] | None = None,
        **filter_params: Any,
    ) -> sa.Select[tuple[Model]]:
        """Get records by filter parameters."""
        if query is None:
            query = sa.select(self.model)
        query = self._apply_param_filters(query, **filter_params)
        if loads is not None:
            query = query.options(*loads)
        return query

    def _apply_sort(
        self,
        query: sa.Select[tuple[Model]],
        sort_by: str,
        sort_order: str,
    ) -> sa.Select[tuple[Model]]:
        """Apply sorting to query."""
        if hasattr(self.model, sort_by) is False:
            raise ValueError(f"Invalid sort parameter: {sort_by}")
        query = query.order_by(
            getattr(sa, sort_order)(getattr(self.model, sort_by)),
        )
        return query

    async def _compute_offset_pagination(
        self,
        query: sa.Select[tuple[Model]],
    ) -> OffsetPaginationMetadata:
        """Compute offset pagination metadata."""
        count_query = sa.select(sa.func.count()).select_from(query.subquery())
        result = await self.session.execute(count_query)
        total = result.scalar_one_or_none() or 0
        return OffsetPaginationMetadata(total=total)

    ##################
    # Public methods #
    ##################

    async def create(
        self,
        input_dto: InputDTO,
    ) -> Model:
        """Create and return a new record."""
        record = self.model(
            **input_dto.model_dump(),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def filter(
        self,
        loads: list[Any] | None = None,
        **filter_params: Any,
    ) -> Sequence[Model] | None:
        """Get records by filter parameters."""
        query = self._apply_base_filter(loads=loads, **filter_params)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def filter_first(
        self,
        loads: list[Any] | None = None,
        **filter_params: Any,
    ) -> Model | None:
        """Get a single record by filter parameters."""
        query = self._apply_base_filter(loads=loads, **filter_params)
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update(
        self,
        id: UUID,
        update_dto: UpdateDTO,
    ) -> None:
        """Update a record by ID."""
        update_dict = update_dto.model_dump(exclude_none=True)
        if not update_dict:
            return
        query = (
            sa.update(self.model)
            .where(self.model.get_primary_key_column() == id)
            .values(
                **update_dict,
            )
        )
        await self.session.execute(query)

    async def delete(
        self,
        **filter_params: Any,
    ) -> None:
        """Delete records by filter parameters."""
        query = sa.delete(self.model)
        query = self._apply_param_filters(query, **filter_params)
        await self.session.execute(query)

    async def get_offset_results[
        T: BaseModel
    ](
        self,
        out_dto: type[T],
        pagination: PaginationType,
        query: sa.sql.Select[tuple[Model]] | None = None,
    ) -> OffsetResults[T]:
        """Get offset paginated results."""

        if query is None:
            query = sa.select(self.model)

        computed_pagination = await self._compute_offset_pagination(query)
        query = query.offset(pagination.offset).limit(pagination.limit)

        if isinstance(pagination, PaginationParamsSortBy):
            query = self._apply_sort(
                query,
                pagination.sort_by,
                pagination.sort_order,
            )

        results = await self.session.execute(query)

        return OffsetResults(
            data=[out_dto.model_validate(row) for row in results.scalars()],
            pagination=computed_pagination,
        )
