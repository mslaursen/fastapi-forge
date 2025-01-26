from pydantic import BaseModel, computed_field


class ModelField(BaseModel):
    """ModelField DTO."""

    name: str
    type: str
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    foreign_key: str | None = None

    @computed_field
    @property
    def factory_field_value(self) -> str | None:
        """Return the appropriate factory default for the model field."""

        faker_placeholder = "factory.Faker({placeholder})"

        if "email" in self.name:
            return faker_placeholder.format(placeholder='"email"')

        type_to_faker = {
            "String": '"text"',
            "Integer": '"random_int"',
            "Float": '"random_float"',
            "Boolan": '"boolean"',
            "DateTime": '"date_time"',
        }

        if self.type not in type_to_faker:
            return None

        return faker_placeholder.format(placeholder=type_to_faker[self.type])


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
