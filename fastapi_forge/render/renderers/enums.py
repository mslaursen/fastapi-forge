from enum import StrEnum, auto


class RendererType(StrEnum):
    MODEL = auto()
    ROUTER = auto()
    DAO = auto()
    DTO = auto()
    TEST_POST = auto()
    TEST_GET = auto()
    TEST_GET_ID = auto()
    TEST_PATCH = auto()
    TEST_DELETE = auto()
    ENUM = auto()
