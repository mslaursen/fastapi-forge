{%- if cookiecutter.use_builtin_auth %}
from datetime import datetime, timedelta, timezone
from typing import Any
from {{cookiecutter.project_name}}.dtos.auth_dtos import TokenData
import jwt
import json
from uuid import UUID
from {{cookiecutter.project_name}} import exceptions
from {{cookiecutter.project_name}}.settings import settings
from passlib.context import CryptContext
from {{cookiecutter.project_name}}.constants import CREATE_TOKEN_EXPIRE_MINUTES


class Encoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return pwd_context.verify(plain_password, hashed_password)


def _encode_token(data: TokenData, expires_at: datetime) -> str:
    """Encode a token."""

    to_encode = data.model_dump()
    to_encode["exp"] = expires_at

    return jwt.encode(
        to_encode,
        settings.jwt.secret.get_secret_value(),
        algorithm=settings.jwt.algorithm,
        json_encoder=Encoder,
    )


def create_access_token(data: TokenData) -> str:
    """Create an access token."""

    return _encode_token(
        data,
        datetime.now(timezone.utc)
        + timedelta(
            minutes=CREATE_TOKEN_EXPIRE_MINUTES,
        ),
    )


def decode_token(token: str) -> TokenData:
    """Decode a token, returning the payload."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt.secret.get_secret_value(),
            algorithms=[settings.jwt.algorithm],
        )
        return TokenData(**payload)

    except jwt.exceptions.PyJWTError:
        raise exceptions.Http401(detail="Invalid token")
{% endif %}
