import pytest

from fastapi_forge.type_info_registry import enum_registry


@pytest.fixture(autouse=True)
def clear_enum_registry() -> None:
    enum_registry.clear()
