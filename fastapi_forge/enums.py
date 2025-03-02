from enum import StrEnum


class FieldDataType(StrEnum):
    STRING = "String"
    INTEGER = "Integer"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    UUID = "UUID"


class RelationshipType(StrEnum):
    """
    RelationshipType Enum.

    Commented out enums are not yet supported.
    """

    # ONE_TO_ONE = "OneToOne"
    # ONE_TO_MANY = "OneToMany"
    MANY_TO_ONE = "ManyToOne"
    # MANY_TO_MANY = "ManyToMany"
