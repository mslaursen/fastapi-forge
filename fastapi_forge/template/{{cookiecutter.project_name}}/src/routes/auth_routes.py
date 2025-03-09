{%- if cookiecutter.use_builtin_auth %}
from fastapi import APIRouter
from src.dtos.auth_dtos import UserLoginDTO, UserCreateDTO, LoginResponse, TokenData
from src.dtos.auth_user_dtos import AuthUserDTO, AuthUserInputDTO
from src.dtos import DataResponse, CreatedResponse
from src.daos import GetDAOs
from src import exceptions
from src.utils import auth_utils
from src.dependencies.auth_dependencies import GetCurrentUser


router = APIRouter(prefix="/auth")


@router.post("/login-email", status_code=201)
async def login(
    input_dto: UserLoginDTO,
    daos: GetDAOs,
) -> DataResponse[LoginResponse]:
    """Login by email and password."""

    user = await daos.auth_user.filter_first(email=input_dto.email)

    if user is None:
        raise exceptions.Http401("Wrong email or password")

    is_valid_password = auth_utils.verify_password(
        input_dto.password.get_secret_value(), user.password
    )

    if not is_valid_password:
        raise exceptions.Http401("Wrong email or password")

    token = auth_utils.create_access_token(
        data=TokenData(
            user_id=user.id,
        )
    )

    return DataResponse(data=LoginResponse(access_token=token))


@router.post("/register", status_code=201)
async def register(
    input_dto: UserCreateDTO,
    daos: GetDAOs,
) -> DataResponse:
    """Register by email and password."""

    user = await daos.auth_user.filter_first(email=input_dto.email)

    if user:
        raise exceptions.Http401("User already exists")

    user_id = await daos.auth_user.create(
        AuthUserInputDTO(
            email=input_dto.email,
            password=auth_utils.hash_password(
                input_dto.password.get_secret_value(),
            ),
        )
    )


    return DataResponse(
        data=CreatedResponse(
            id=user_id,
        )
    )


@router.get("/users/me", status_code=200)
async def get_current_user(
    current_user: GetCurrentUser,
) -> DataResponse[AuthUserDTO]:
    """Get current user."""

    return DataResponse(data=current_user)
{% endif %}
