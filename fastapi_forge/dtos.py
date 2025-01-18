from pydantic import BaseModel


class ModelField(BaseModel):
    """ModelField DTO."""

    name: str
    type: str
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    foreign_key: str | None = None


class ModelRelationship(BaseModel):
    """ModelRelationship DTO."""

    type: str
    target: str
    foreign_key: str


class Model(BaseModel):
    """Model DTO."""

    name: str
    fields: list[ModelField]
    relationships: list[ModelRelationship] = []


class ForgeProjectRequestDTO(BaseModel):
    """ForgeProjectRequest DTO."""

    project_name: str
    use_postgres: bool
    create_daos: bool
    create_routes: bool
    models: list[Model]
