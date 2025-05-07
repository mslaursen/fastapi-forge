from fastapi_forge.schemas import ModelField, ModelRelationship


class JinjaFilters:
    @staticmethod
    def generate_field(
        field: ModelField, relationships: list[ModelRelationship] | None = None
    ) -> str:
        target = None
        if field.metadata.is_foreign_key and relationships is not None:
            target = next(
                (
                    relation
                    for relation in relationships
                    if relation.field_name == field.name
                ),
                None,
            )

        target_data = None
        if target:
            target_data = (target.target_model, target.on_delete)

        if relationships is not None and target is None:
            raise ValueError(f"Target was not found for Foreign Key {field.name}")

        type_info = field.type_info
        args = [
            f"{'sa.' if type_info.sqlalchemy_prefix else ''}{type_info.sqlalchemy_type}"
        ]

        if field.metadata.is_foreign_key and target_data:
            target_model, on_delete = target_data
            args.append(
                f'sa.ForeignKey("{target_model + ".id"}", ondelete="{on_delete}")'
            )
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

    @staticmethod
    def generate_relationship(
        relation: ModelRelationship, is_self_reference: bool = False
    ) -> str:
        """Generates a relationship field for SQLAlchemy."""
        args = []
        args.append(f"foreign_keys=[{relation.field_name}]")
        if relation.back_populates:
            args.append(f'back_populates="{relation.back_populates}"')
        args.append("uselist=False")

        target_repr = (
            relation.target if not is_self_reference else f'"{relation.target}"'
        )
        return f"""
        {relation.field_name_no_id}: Mapped[{target_repr}] = relationship(
            {",\n        ".join(args)}
        )
        """.strip()
