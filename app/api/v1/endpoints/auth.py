from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])
DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_user_service(session: DbSession) -> UserService:
    repository = UserRepository(session)
    return UserService(repository, session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


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
