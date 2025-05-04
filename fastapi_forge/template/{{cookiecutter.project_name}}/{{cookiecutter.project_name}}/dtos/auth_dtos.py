{%- if cookiecutter.use_builtin_auth %}
from uuid import UUID
from pydantic import BaseModel, SecretStr, EmailStr
from {{ cookiecutter.project_name }} import enums
from {{ cookiecutter.project_name }}.dtos import BaseOrmModel


class TokenData(BaseModel):
    """Token data."""

    user_id: UUID


class UserLoginDTO(BaseModel):
    """DTO for user login."""

    email: str
    password: SecretStr


class UserCreateDTO(BaseModel):
    """DTO for user creation."""

    email: EmailStr
    password: SecretStr


class UserCreateResponseDTO(BaseOrmModel):
    """DTO for created user response."""

    {% for field in cookiecutter.auth_model.fields if not (field.metadata.is_created_at_timestamp or field.metadata.is_updated_at_timestamp or field.name == "password") -%}
    {{ field.name }}: {{ field.type_info.python_type }}{% if field.nullable %} | None{% endif %}
    {% endfor %}


class LoginResponse(BaseModel):
    """Response model for login."""

    access_token: str
{% endif %}