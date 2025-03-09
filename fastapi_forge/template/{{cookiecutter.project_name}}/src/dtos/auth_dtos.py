{%- if cookiecutter.use_builtin_auth %}
from uuid import UUID
from pydantic import BaseModel, SecretStr


class TokenData(BaseModel):
    """Token data."""

    user_id: UUID


class UserLoginDTO(BaseModel):
    """DTO for user login."""

    email: str
    password: SecretStr


class UserCreateDTO(BaseModel):
    """DTO for user creation."""

    email: str
    password: SecretStr


class LoginResponse(BaseModel):
    """Response model for login."""

    access_token: str
{% endif %}