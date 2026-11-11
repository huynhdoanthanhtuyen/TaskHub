from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserAdminUpdate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["Users"])


def get_user_service(session: DbSession) -> UserService:
    repository = UserRepository(session)
    return UserService(repository, session)


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(current_user: CurrentUser) -> User:
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser,
    service: UserServiceDep,
) -> User:
    return await service.update_me(current_user, data)


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def list_users(
    admin: AdminUser,
    service: UserServiceDep,
) -> list[User]:
    return await service.list_users()


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def admin_update_user(
    user_id: UUID,
    data: UserAdminUpdate,
    admin: AdminUser,
    service: UserServiceDep,
) -> User:
    return await service.admin_update_user(
        user_id,
        data,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    admin: AdminUser,
    service: UserServiceDep,
) -> None:
    await service.delete_user(
        user_id,
        admin,
    )
