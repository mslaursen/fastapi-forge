import pathlib
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings as PydanticBaseSettings


PREFIX = "{{ cookiecutter.project_name|upper|replace('-', '_') }}_"

DOTENV = pathlib.Path(__file__).parent.parent / ".env"


class BaseSettings(PydanticBaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Settings(BaseSettings):
    """Settings for the auth service."""

    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    log_level: str = "info"
    reload: bool = False

    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_prefix=PREFIX,
    )


settings = Settings()
