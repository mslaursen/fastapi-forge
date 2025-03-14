from enum import StrEnum


class FieldDataType(StrEnum):
    STRING = "String"
    INTEGER = "Integer"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    UUID = "UUID"
    JSONB = "JSONB"

    def as_python_type(self) -> str:
        return {
            FieldDataType.STRING: "str",
            FieldDataType.INTEGER: "int",
            FieldDataType.FLOAT: "float",
            FieldDataType.BOOLEAN: "bool",
            FieldDataType.DATETIME: "str",
            FieldDataType.UUID: "UUID",
            FieldDataType.JSONB: "dict[str, Any]",
        }[self]
