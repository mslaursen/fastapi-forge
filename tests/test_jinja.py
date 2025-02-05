from fastapi_forge.dtos import Model


def test_render_model_to_model(models: list[Model]) -> None:
    """Test render_model_to_model()."""
    assert len(models) == 3
