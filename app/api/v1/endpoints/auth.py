from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, DbSession
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.token import RefreshTokenRequest, TokenResponse
from app.schemas.user import PasswordChange, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_service(session: DbSession) -> UserService:
    repository = UserRepository(session)
    return UserService(repository, session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_auth_service(session: DbSession) -> AuthService:
    user_repository = UserRepository(session)
    refresh_token_repository = RefreshTokenRepository(session)

    return AuthService(
        session=session,
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    service: UserServiceDep,
) -> User:
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def login(data: UserLogin, service: AuthServiceDep) -> TokenResponse:
    return await service.login(data)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest, service: AuthServiceDep
) -> TokenResponse:
    return await service.refresh(request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: RefreshTokenRequest, service: AuthServiceDep) -> None:
    await service.logout(request)


@router.patch(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    data: PasswordChange,
    current_user: CurrentUser,
    service: UserServiceDep,
) -> None:
    await service.change_password(current_user, data)
