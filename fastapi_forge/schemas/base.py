from pydantic import (
    BaseModel,
    ConfigDict,
)


class BaseSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
