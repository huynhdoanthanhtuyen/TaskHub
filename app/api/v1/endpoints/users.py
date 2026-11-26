from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    AdminUser,
    CurrentUser,
    DbSession,
    PaginationDep,
    SearchDep,
)
from app.core.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserAdminUpdate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def get_user_service(
    session: DbSession,
) -> UserService:
    repository = UserRepository(session)

    return UserService(
        repository=repository,
        session=session,
    )


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
    },
)
async def get_me(
    current_user: CurrentUser,
) -> User:
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Email already exists",
        },
    },
)
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser,
    service: UserServiceDep,
) -> User:
    return await service.update_me(
        current_user,
        data,
    )


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List, search and filter users",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Admin permission required",
        },
    },
)
async def list_users(
    admin: AdminUser,
    service: UserServiceDep,
    pagination: PaginationDep,
    searching: SearchDep,
    role: UserRole | None = None,
    is_active: bool | None = None,
) -> UserListResponse:
    users, total = await service.list_users(
        offset=pagination.offset,
        limit=pagination.limit,
        role=role,
        is_active=is_active,
        search=searching.search,
    )

    return UserListResponse(
        items=[
            UserResponse.model_validate(user)
            for user in users
        ],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a user as administrator",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Admin permission required",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
        },
    },
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
        admin,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user as administrator",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Admin permission required",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
        },
        status.HTTP_409_CONFLICT: {
            "description": "User has related resources",
        },
    },
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