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
class DBSettings(BaseSettings):
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
{% if cookiecutter.use_redis %}
class RedisSettings(BaseSettings):
    """Configuration for Redis."""

    host: str = "redis"
    port: int = 6379
    password: SecretStr = SecretStr("")
    max_connections: int = 50

    @property
    def url(self) -> URL:
        """Generates a URL for the Redis connection."""

        return URL.build(
            scheme="redis"  ,
            host=self.host,
            port=self.port,
            password=self.password.get_secret_value(),
        )

    model_config = SettingsConfigDict(env_file=".env", env_prefix=f"{PREFIX}REDIS_")

{% endif %}
{% if cookiecutter.use_rabbitmq %}
class RabbitMQSettings(BaseSettings):
    """Configuration for RabbitMQ."""

    host: str = "rabbitmq"
    port: int = 5672
    user: str = "user"
    password: SecretStr = SecretStr("password")
    vhost: str = "/"
    connection_pool_size: int = 2
    channel_pool_size: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_prefix=f"{PREFIX}RABBITMQ_")


    @property
    def url(self) -> URL:
        """Generates a URL for RabbitMQ connection."""
        return URL.build(
            scheme="amqp",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password.get_secret_value(),
            path=self.vhost,
        )
{% endif %}
{% if cookiecutter.use_builtin_auth %}
class JWTSettings(BaseSettings):
    """Configuration for JWT."""

    secret: SecretStr = SecretStr("")
    algorithm: str = "HS256"
{% endif %}

{% if cookiecutter.use_prometheus %}
class PrometheusSettings(BaseSettings):
    enabled: bool = True
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix=f"{PREFIX}PROMETHEUS_"
    )
{% endif %}

class Settings(BaseSettings):
    """Main settings."""

    env: str = "local"
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    log_level: str = "info"
    reload: bool = False
    
    {% if cookiecutter.use_postgres -%}
    db: DBSettings = DBSettings()
    {% endif %}
    {%- if cookiecutter.use_redis -%}
    redis: RedisSettings = RedisSettings()
    {% endif %}
    {%- if cookiecutter.use_builtin_auth -%}
    jwt: JWTSettings = JWTSettings()
    {% endif %}
    {%- if cookiecutter.use_rabbitmq -%}
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    {% endif %}
    {% if cookiecutter.use_prometheus %}
    prometheus: PrometheusSettings = PrometheusSettings()
    {% endif %}
    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_prefix=PREFIX,
    )


settings = Settings()
