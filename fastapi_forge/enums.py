from enum import StrEnum


class HTTPMethod(StrEnum):
    GET = "get"
    GET_ID = "get_id"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class FieldDataType(StrEnum):
    STRING = "String"
    INTEGER = "Integer"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    UUID = "UUID"
    JSONB = "JSONB"
