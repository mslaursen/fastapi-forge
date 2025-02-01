import pathlib
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic import SecretStr
from yarl import URL

PREFIX = "{{ cookiecutter.project_name|upper|replace('-', '_') }}_"

DOTENV = pathlib.Path(__file__).parent.parent / ".env"


class BaseSettings(PydanticBaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

{% if cookiecutter.use_postgres %}
class PGSettings(BaseSettings):
    """Configuration for PostgreSQL connection."""

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    database: str = "postgres"
    pool_size: int = 15
    echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}PG_",
    )

    @property
    def url(self) -> URL:
        """Generates a URL for the PostgreSQL connection."""

        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password.get_secret_value(),
            path=f"/{self.database}",
        )
{% endif %}
{% if cookiecutter.use_builtin_auth %}
class JWTSettings(BaseSettings):
    """Configuration for JWT."""

    secret: SecretStr = SecretStr("")
    algorithm: str = "HS256"
{% endif %}

class Settings(BaseSettings):
    """Main settings."""

    env: str = "local"
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    log_level: str = "info"
    reload: bool = False
    {% if cookiecutter.use_postgres %}
    pg: PGSettings = PGSettings()
    {% endif %}
    {% if cookiecutter.use_builtin_auth %}
    jwt: JWTSettings = JWTSettings()
    {% endif %}
    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_prefix=PREFIX,
    )


settings = Settings()
