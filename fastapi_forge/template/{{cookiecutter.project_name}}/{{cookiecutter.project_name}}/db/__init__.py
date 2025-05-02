import sqlalchemy as sa

from sqlalchemy.orm import DeclarativeBase


meta = sa.MetaData()


class Base(DeclarativeBase):
    """Base model for all other models."""

    metadata = meta

    __tablename__: str

