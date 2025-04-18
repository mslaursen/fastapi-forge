from fastapi_forge.dtos import ModelField, ModelRelationship


def _gen_field(
    field: ModelField,
    target: str | None = None,
) -> str:
    type_info = field.type_info
    args = [
        f"{'sa.' if type_info.sqlalchemy_prefix else ''}{type_info.sqlalchemy_type}"
    ]

    if field.metadata.is_foreign_key and target:
        args.append(f'sa.ForeignKey("{target + ".id"}", ondelete="{field.on_delete}")')
    if field.primary_key:
        args.append("primary_key=True")
    if field.unique:
        args.append("unique=True")
    if field.index:
        args.append("index=True")
    if field.default_value:
        if field.type_enum:
            args.append(f"default=enums.{field.type_enum}.{field.default_value}")
        else:
            args.append(f"default={field.default_value}")
    if field.extra_kwargs:
        for k, v in field.extra_kwargs.items():
            args.append(f"{k}={v}")

    return f"""
    {field.name}: Mapped[{field.type_info.python_type}{" | None" if field.nullable else ""}] = mapped_column(
        {",\n        ".join(args)}
    )
    """.strip()


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

    return _gen_field(field=field, target=target)


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
