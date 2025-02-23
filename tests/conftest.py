import pytest
from fastapi_forge.dtos import Model


@pytest.fixture
def models() -> list[Model]:
    """Return a list of Model instances."""
    return []
