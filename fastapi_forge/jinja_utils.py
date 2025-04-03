from fastapi_forge.dtos import ModelField, ModelRelationship
from fastapi_forge.enums import FieldDataType


def _map_field_type_to_sa_type(field: ModelField) -> str:
    field_type_mapping = {
        FieldDataType.UUID: "UUID(as_uuid=True)",
        FieldDataType.STRING: "String",
        FieldDataType.INTEGER: "Integer",
        FieldDataType.FLOAT: "Float",
        FieldDataType.BOOLEAN: "Boolean",
        FieldDataType.DATETIME: "DateTime(timezone=True)",
        FieldDataType.JSONB: "JSONB",
    }

    sa_type = field_type_mapping.get(field.type)

    if sa_type is None:
        raise ValueError(f"Unsupported field type: {field.type}")

    return sa_type


def _gen_field(
    field: ModelField,
    sa_type: str,
    prefix_sa: bool = True,
    target: str | None = None,
) -> str:
    args = [f"{'sa.' if prefix_sa else ''}{sa_type}"]

    if field.metadata.is_foreign_key and target:
        args.append(f'sa.ForeignKey("{target + ".id"}", ondelete="CASCADE")')
    if field.primary_key:
        args.append("primary_key=True")
    if field.unique:
        args.append("unique=True")
    if field.index:
        args.append("index=True")
    if field.default_value:
        args.append(f"default={field.default_value}")
    if field.extra_kwargs:
        for k, v in field.extra_kwargs.items():
            args.append(f"{k}={v}")

    if not isinstance(field.type, FieldDataType):
        field.type = FieldDataType(field.type)

    return f"""
    {field.name}: Mapped[{field.type.as_python_type()}{" | None" if field.nullable else ""}] = mapped_column(
        {",\n        ".join(args)}
    )
    """.strip()


def _gen_uuid_field(field: ModelField, target: str | None = None) -> str:
    return _gen_field(field, _map_field_type_to_sa_type(field), target=target)


def _gen_string_field(field: ModelField, target: str | None = None) -> str:
    return _gen_field(field, _map_field_type_to_sa_type(field), target=target)


def _gen_integer_field(field: ModelField, target: str | None = None) -> str:
    return _gen_field(field, _map_field_type_to_sa_type(field), target=target)


def _gen_float_field(field: ModelField, target: str | None = None) -> str:
    return _gen_field(field, _map_field_type_to_sa_type(field), target=target)


def _gen_boolean_field(field: ModelField, target: str | None = None) -> str:
    return _gen_field(field, _map_field_type_to_sa_type(field), target=target)


def _gen_datetime_field(field: ModelField, target: str | None = None) -> str:
    return _gen_field(field, _map_field_type_to_sa_type(field), target=target)


def _gen_jsonb_field(field: ModelField, target: str | None = None) -> str:
    return _gen_field(
        field,
        _map_field_type_to_sa_type(field),
        prefix_sa=False,
        target=target,
    )


def generate_field(
    field: ModelField,
    relationships: list[ModelRelationship] | None = None,
) -> str:
    if field.primary_key:
        return ""

    target = None
    if field.metadata.is_foreign_key and relationships is not None:
        target = next(
            (
                relation.target_model
                for relation in relationships
                if relation.field_name == field.name
            ),
            None,
        )

    if relationships is not None and target is None:
        raise ValueError(f"Target was not found for Foreign Key {field.name}")

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

    return type_to_fn[field.type](field, target=target)


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
    """.strip()
