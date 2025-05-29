from typing import Annotated

from pydantic import Field

BoundedStr = Annotated[str, Field(..., min_length=1, max_length=100)]
SnakeCaseStr = Annotated[BoundedStr, Field(..., pattern=r"^[a-z][a-z0-9_]*$")]
ModelName = SnakeCaseStr
FieldName = SnakeCaseStr
BackPopulates = Annotated[str, Field(..., pattern=r"^[a-z][a-z0-9_]*$")]
ProjectName = Annotated[
    BoundedStr,
    Field(..., pattern=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"),
]
EnumStr = Annotated[
    BoundedStr,
    Field(
        ...,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
    ),
]
