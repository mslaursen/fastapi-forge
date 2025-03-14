from fastapi_forge.dtos import ModelField, ModelRelationship, Model
from fastapi_forge.string_utils import camel_to_snake
from fastapi_forge.enums import FieldDataType


def generate_relationship(relation: ModelRelationship) -> str:
    args = []
    args.append(f'"{relation.target}"')
    args.append(f"foreign_keys=[{relation.field_name}]")
    if relation.back_populates:
        args.append(f'back_populates="{relation.back_populates}"')
    args.append("uselist=False")

    return f"""
    {relation.field_name_no_id}: Mapped[{relation.target}] = relationship(
        {",\n        ".join(args)}
    )
    """


def _gen_field(field: ModelField, sa_type: str, prefix_sa: bool = True) -> str:
    args = []
    args.append(f"{'sa.' if prefix_sa else ''}{sa_type}")
    if field.foreign_key:
        args.append(
            f'sa.ForeignKey("{camel_to_snake(field.foreign_key)}", ondelete="CASCADE")'
        )
    if field.primary_key:
        args.append("primary_key=True")
    if field.unique:
        args.append("unique=True")
    if field.index:
        args.append("index=True")

    return f"""
    {field.name}: Mapped[{field.type.as_python_type()}{" | None" if field.nullable else ""}] = mapped_column(
        {",\n        ".join(args)}
    )
    """


def _gen_uuid_field(field: ModelField) -> str:
    return _gen_field(field, "UUID(as_uuid=True)")


def _gen_string_field(field: ModelField) -> str:
    return _gen_field(field, "String")


def _gen_integer_field(field: ModelField) -> str:
    return _gen_field(field, "Integer")


def _gen_float_field(field: ModelField) -> str:
    return _gen_field(field, "Float")


def _gen_boolean_field(field: ModelField) -> str:
    return _gen_field(field, "Boolean")


def _gen_datetime_field(field: ModelField) -> str:
    return _gen_field(field, "DateTime(timezone=True)")


def _gen_jsonb_field(field: ModelField) -> str:
    return _gen_field(field, "JSONB", prefix_sa=False)


def generate_field(field: ModelField) -> str:
    # currently, primary keys fields are applied by the base class
    # of the model, so we don't need to generate them here
    if field.primary_key:
        return ""

    type_to_fn = {
        FieldDataType.UUID: _gen_uuid_field,
        FieldDataType.STRING: _gen_string_field,
        FieldDataType.INTEGER: _gen_integer_field,
        FieldDataType.FLOAT: _gen_float_field,
        FieldDataType.BOOLEAN: _gen_boolean_field,
        FieldDataType.DATETIME: _gen_datetime_field,
        FieldDataType.JSONB: _gen_jsonb_field,
    }

    if field.type not in type_to_fn:
        raise ValueError(f"Unsupported field type: {field.type}")

    return type_to_fn[field.type](field)


if __name__ == "__main__":
    relation = ModelRelationship(
        field_name="restaurant_id",
        back_populates="restaurants",
    )

    model = Model(
        name="reservation",
        fields=[
            ModelField(
                name="id",
                type=FieldDataType.UUID,
                primary_key=True,
                unique=True,
            ),
            ModelField(
                name="name",
                type=FieldDataType.STRING,
                nullable=True,
            ),
            ModelField(
                name="age",
                type=FieldDataType.INTEGER,
                nullable=False,
            ),
            ModelField(
                name="price",
                type=FieldDataType.FLOAT,
                nullable=False,
            ),
            ModelField(
                name="is_active",
                type=FieldDataType.BOOLEAN,
                nullable=False,
            ),
            ModelField(
                name="created_at",
                type=FieldDataType.DATETIME,
                nullable=False,
            ),
            ModelField(
                name="restaurant_id",
                type=FieldDataType.UUID,
                nullable=True,
                foreign_key="Restaurant.id",
            ),
        ],
        relationships=[relation],
    )

    for field in model.fields:
        s = generate_field(field)
        print(s)
