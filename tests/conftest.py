import pytest

from fastapi_forge.type_info_registry import TypeInfoRegistry, enum_registry


@pytest.fixture(autouse=True)
def clear_enum_registry() -> None:
    enum_registry.clear()


@pytest.fixture
def type_info_registry() -> TypeInfoRegistry:
    return TypeInfoRegistry()
