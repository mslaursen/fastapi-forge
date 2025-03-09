{%- if cookiecutter.use_builtin_auth %}
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer as _HTTPBearer
from src.dtos.auth_user_dtos import AuthUserDTO
from src.daos import GetDAOs
from src import exceptions
from src.utils import auth_utils
from typing import Annotated


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
            raise exceptions.Http401("Missing token.")


auth_scheme = HTTPBearer()


def get_token(token: str = Depends(auth_scheme)) -> str:
    """Return access token as str."""
    return token


GetToken = Annotated[str, Depends(get_token)]


async def get_current_user(
    token: GetToken,
    daos: GetDAOs,
) -> AuthUserDTO:
    """Get current user from token data."""
    token_data = auth_utils.decode_token(token)

    user = await daos.auth_user.filter_first(id=token_data.user_id)

    if not user:
        raise exceptions.Http404("Decoded user not found.")

    return AuthUserDTO.model_validate(user)


GetCurrentUser = Annotated[AuthUserDTO, Depends(get_current_user)]
{% endif %}