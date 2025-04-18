from enum import StrEnum
from functools import lru_cache


class FieldDataTypeEnum(StrEnum):
    STRING = "String"
    INTEGER = "Integer"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    UUID = "UUID"
    JSONB = "JSONB"
    ENUM = "Enum"

    @classmethod
    @lru_cache
    def get_type_mappings(cls) -> dict[str, list[str]]:
        return {
            cls.STRING: [
                "character varying",
                "text",
                "varchar",
                "char",
                "user-defined",
            ],
            cls.INTEGER: [
                "integer",
                "int",
                "serial",
                "smallint",
                "bigint",
                "bigserial",
            ],
            cls.FLOAT: [
                "real",
                "float4",
                "double precision",
                "float8",
            ],
            cls.BOOLEAN: ["boolean", "bool"],
            cls.DATETIME: [
                "timestamp",
                "timestamp with time zone",
                "timestamp without time zone",
                "date",
                "datetime",
                "time",
            ],
            cls.UUID: ["uuid"],
            cls.JSONB: ["json", "jsonb"],
        }

    @classmethod
    def get_custom_types(cls) -> dict[str, "FieldDataTypeEnum"]:
        return {}

    @classmethod
    def from_db_type(cls, db_type: str) -> "FieldDataTypeEnum":
        db_type = db_type.lower()

        custom_types = cls.get_custom_types()
        if db_type in custom_types:
            return custom_types[db_type]

        for field_type, patterns in cls.get_type_mappings().items():
            if any(pattern in db_type for pattern in patterns):
                return field_type if isinstance(field_type, cls) else cls(field_type)

        raise ValueError(
            f"Unsupported database type: {db_type}. "
            f"Supported types are: {list(cls.get_type_mappings().keys())}"
        )


class OnDeleteEnum(StrEnum):
    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"


class HTTPMethodEnum(StrEnum):
    GET = "get"
    GET_ID = "get_id"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"
