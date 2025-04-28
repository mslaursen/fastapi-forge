from cookiecutter.utils import simple_filter
from fastapi_forge.utils.string_utils import camel_to_snake as _camel_to_snake


@simple_filter
def camel_to_snake(value: str) -> str:
    return _camel_to_snake(value)
