import pytest
from fastapi_forge.dtos import Model, ModelField, ModelRelationship


@pytest.fixture
def models() -> list[Model]:
    """Return a list of Model instances."""
    return [
        Model(
            name="AppUser",
            fields=[
                ModelField(name="id", type="UUID", primary_key=True),
                ModelField(name="name", type="String", nullable=False),
                ModelField(name="email", type="String", unique=True),
                ModelField(name="password", type="String", nullable=False),
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
        Model(
            name="Table",
            fields=[
                ModelField(name="id", type="UUID", primary_key=True),
                ModelField(name="number", type="Integer", nullable=False),
                ModelField(name="seats", type="Integer", nullable=False),
                ModelField(name="restaurant_id", type="UUID", nullable=False),
                ModelField(name="time", type="DateTime", nullable=False),
            ],
            relationships=[
                ModelRelationship(
                    type="ManyToOne", target="Restaurant", foreign_key="restaurant_id"
                )
            ],
        ),
    ]
