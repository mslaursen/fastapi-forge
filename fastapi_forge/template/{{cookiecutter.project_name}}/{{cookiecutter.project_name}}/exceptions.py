from fastapi import HTTPException
from starlette import status


class Http401(HTTPException):
    """Unauthorized 401."""

    def __init__(self, detail: str = "Unauthorized."):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = detail


class Http403(HTTPException):
    """Forbidden 403."""

    def __init__(self, detail: str = "Forbidden."):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = detail


class Http404(HTTPException):
    """Not found 404."""

    def __init__(self, detail: str = "Not found."):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail


class Http500(HTTPException):
    """Internal server error 500."""

    def __init__(self, detail: str = "Internal server error."):
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = detail