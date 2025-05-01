from abc import abstractmethod
from typing import Any, Protocol


class DatabaseInspector(Protocol):
    @abstractmethod
    def validate_connection_string(self, connection_string: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def fetch_enums(self, schema: str) -> dict[str, list[str]]:
        raise NotImplementedError

    @abstractmethod
    def fetch_enum_columns(self, schema: str) -> list[tuple[Any, ...]]:
        raise NotImplementedError

    @abstractmethod
    def fetch_schema_tables(self, schema: str) -> list[tuple[Any, ...]]:
        raise NotImplementedError

    @abstractmethod
    def get_connection_string(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_db_name(self) -> str:
        raise NotImplementedError
