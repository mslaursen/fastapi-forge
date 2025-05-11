from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.elements import NamedColumn


meta = sa.MetaData()


class Base(DeclarativeBase):
    """Base model for all other models."""

    metadata = meta

    __tablename__: str

    @classmethod
    def get_primary_key_column(cls) -> NamedColumn[Any]:
        return next(iter(cls.__table__.primary_key))

