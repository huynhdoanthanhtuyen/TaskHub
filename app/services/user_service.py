from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.enums import UserRole
from app.core.exceptions import EmailAlreadyExistsError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, repository: UserRepository, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def register(self, data: UserCreate) -> User:
        email = str(data.email).lower()

        existing_user = await self.repository.get_by_email(email)

        if existing_user is not None:
            raise EmailAlreadyExistsError()

        hashed_password = await run_in_threadpool(
            hash_password,
            data.password,
        )

        user = User(
            email=email,
            full_name=data.full_name,
            hashed_password=hashed_password,
            role=UserRole.MEMBER,
        )

        try:
            await self.repository.create(user)
            await self.session.commit()
            await self.session.refresh(user)

        except IntegrityError:
            await self.session.rollback()

            existing_user = await self.repository.get_by_email(email)

            if existing_user is not None:
                raise EmailAlreadyExistsError()
            raise

        return user
