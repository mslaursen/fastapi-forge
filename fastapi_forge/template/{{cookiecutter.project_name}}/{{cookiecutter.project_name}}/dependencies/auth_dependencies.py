{% if cookiecutter.use_builtin_auth %}
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer as _HTTPBearer

from {{cookiecutter.project_name}} import exceptions
from {{cookiecutter.project_name}}.daos import GetDAOs
from {{cookiecutter.project_name}}.dtos.{{ cookiecutter.auth_model.name }}_dtos import {{ cookiecutter.auth_model.name_cc }}DTO
from {{cookiecutter.project_name}}.utils import auth_utils


class HTTPBearer(_HTTPBearer):
    """
    HTTPBearer with access token.
    Returns access token as str.
    """

    async def __call__(self, request: Request) -> str | None:  # type: ignore
        """Return access token."""
        try:
            obj = await super().__call__(request)
            return obj.credentials if obj else None
        except HTTPException:
            msg = "Missing token."
            raise exceptions.Http401(msg)


auth_scheme = HTTPBearer()


def get_token(token: str = Depends(auth_scheme)) -> str:
    """Return access token as str."""
    return token


GetToken = Annotated[str, Depends(get_token)]


async def get_current_user(
    token: GetToken,
    daos: GetDAOs,
) -> {{ cookiecutter.auth_model.name_cc }}DTO:
    """Get current user from token data."""
    token_data = auth_utils.decode_token(token)

    user = await daos.{{ cookiecutter.auth_model.name }}.filter_first(id=token_data.user_id)

    if not user:
        msg = "Decoded user not found."
        raise exceptions.Http404(msg)

    return {{ cookiecutter.auth_model.name_cc }}DTO.model_validate(user)


GetCurrentUser = Annotated[{{ cookiecutter.auth_model.name_cc }}DTO, Depends(get_current_user)]
{% endif %}