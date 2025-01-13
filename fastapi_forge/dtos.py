from pydantic import BaseModel


class ForgeProjectRequestDTO(BaseModel):
    """Temp."""

    project_name: str
    use_postgres: bool
    create_daos: bool
    create_endpoints: bool
