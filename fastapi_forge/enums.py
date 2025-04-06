from enum import StrEnum


class FieldDataType(StrEnum):
    STRING = "String"
    INTEGER = "Integer"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    UUID = "UUID"
    JSONB = "JSONB"

    @classmethod
    def from_db_type(cls, db_type: str) -> "FieldDataType":
        db_type = db_type.lower()
        match db_type:
            case _ if db_type.startswith("character varying") or db_type == "text":
                return cls.STRING
            case "integer" | "bigint" | "smallint":
                return cls.INTEGER
            case "numeric":
                return cls.FLOAT
            case "boolean":
                return cls.BOOLEAN
            case "uuid":
                return cls.UUID
            case _ if db_type.startswith("timestamp") or "date":
                return cls.DATETIME
            case "jsonb":
                return cls.JSONB
            case _:
                raise ValueError(f"Unsupported database type: {db_type}")


class HTTPMethod(StrEnum):
    GET = "get"
    GET_ID = "get_id"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"
