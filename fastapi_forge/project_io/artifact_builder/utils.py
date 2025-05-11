from fastapi_forge.enums import FieldDataTypeEnum
from fastapi_forge.schemas import ModelField, ModelFieldMetadata, ProjectSpec


def insert_relation_fields(project_spec: ProjectSpec) -> None:
    """Adds ModelFields to a model, based on its relationships."""
    for model in project_spec.models:
        field_names_set = {field.name for field in model.fields}
        for relation in model.relationships:
            if relation.field_name in field_names_set:
                continue
            model.fields.append(
                ModelField(
                    name=relation.field_name,
                    type=FieldDataTypeEnum.UUID,
                    nullable=relation.nullable,
                    unique=relation.unique,
                    index=relation.index,
                    metadata=ModelFieldMetadata(is_foreign_key=True),
                ),
            )
