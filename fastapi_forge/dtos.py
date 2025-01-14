from pydantic import BaseModel
from typing import Any


class ForgeProjectRequestDTO(BaseModel):
    """Temp."""

    project_name: str
    use_postgres: bool
    create_daos: bool
    create_endpoints: bool
    models: dict[str, Any]
