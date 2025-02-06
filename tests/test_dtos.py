from fastapi_forge.dtos import ModelField
from fastapi_forge.enums import FieldDataType


def test_model_field_dto() -> None:
    """Test ModelField DTO."""
    model_field = ModelField(
        name="id",
        type=FieldDataType.UUID,
        primary_key=True,
    )
    assert model_field.factory_field_value is None
