import pytest

from fastapi_forge.enums import FieldDataTypeEnum
from fastapi_forge.render import create_jinja_render_manager
from fastapi_forge.schemas import Model, ModelField

render_manager = create_jinja_render_manager("test_project")


@pytest.mark.parametrize(
    "noun, expected",
    [
        ("tooth", "teeth"),
        ("teeth", "teeth"),
        ("person", "people"),
        ("people", "people"),
        ("game_zone", "game-zones"),
        ("user", "users"),
        ("auth_user", "auth-users"),
        ("hardware_setup", "hardware-setups"),
    ],
)
def test_render_post_test(noun: str, expected: str) -> None:
    model = Model(
        name=noun,
        fields=[
            ModelField(
                name="id",
                type=FieldDataTypeEnum.UUID,
                primary_key=True,
                unique=True,
            ),
        ],
    )
    model_renderer = render_manager.get_renderer("test_post")
    render = model_renderer.render(model)
    assert f'URI = "/api/v1/{expected}/"' in render
