import sqlalchemy as sa
import uuid

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


meta = sa.MetaData()


class Base(DeclarativeBase):
    """Base model for all other models."""

    metadata = meta

    __tablename__: str

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
