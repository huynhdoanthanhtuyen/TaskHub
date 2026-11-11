from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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
        user = User(
            email=str(data.email).lower(),
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=UserRole.MEMBER,
        )
        try:
            await self.repository.create(user)
            await self.session.commit()
            await self.session.refresh(user)
        except IntegrityError as exc:
            await self.session.rollback()

            sqlstate = getattr(
                getattr(exc.orig, "__cause__", None),
                "sqlstate",
                None,
            )

            constraint_name = getattr(
                getattr(exc.orig, "__cause__", None),
                "constraint_name",
                None,
            )

            if sqlstate == "23505" and constraint_name == "ix_users_email":
                raise EmailAlreadyExistsError() from exc

            raise
        return user
