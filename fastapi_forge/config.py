from dataclasses import dataclass


@dataclass
class FastAPIServerConfig:
    """FastAPI server configuration."""

    host: str = "localhost"
    port: int = 9000
