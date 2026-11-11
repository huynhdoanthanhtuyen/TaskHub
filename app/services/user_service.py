from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.exceptions import (
    CannotDeleteSelfError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    LastActiveAdminError,
    UserNotFoundError,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import PasswordChange, UserAdminUpdate, UserCreate, UserUpdate


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

    async def change_password(
        self,
        user: User,
        data: PasswordChange,
    ) -> None:
        if not verify_password(
            data.old_password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError()

        new_hashed_password = hash_password(data.new_password)

        refresh_token_repository = RefreshTokenRepository(self.session)

        try:
            user.hashed_password = new_hashed_password

            await refresh_token_repository.revoke_all_for_user(user.id)

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def update_me(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return user

        if "email" in update_data:
            update_data["email"] = str(update_data["email"]).lower()

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            await self.session.commit()
            await self.session.refresh(user)
        except IntegrityError as exc:
            await self.session.rollback()
            raise EmailAlreadyExistsError() from exc
        except Exception:
            await self.session.rollback()
            raise

        return user

    async def list_users(self) -> list[User]:
        return await self.repository.get_all()

    async def admin_update_user(
        self,
        user_id: UUID,
        data: UserAdminUpdate,
    ) -> User:
        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return user

        if user.role == UserRole.ADMIN and user.is_active:
            new_role = update_data.get("role", user.role)
            new_is_active = update_data.get(
                "is_active",
                user.is_active,
            )

            if new_role != UserRole.ADMIN or not new_is_active:
                admin_count = await self.repository.count_active_admins()

                if admin_count <= 1:
                    raise LastActiveAdminError()

        try:
            for field, value in update_data.items():
                setattr(user, field, value)

            await self.session.commit()
            await self.session.refresh(user)

        except Exception:
            await self.session.rollback()
            raise

        return user

    async def delete_user(
        self,
        user_id: UUID,
        current_admin: User,
    ) -> None:
        if user_id == current_admin.id:
            raise CannotDeleteSelfError()

        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        if user.role == UserRole.ADMIN and user.is_active:
            admin_count = await self.repository.count_active_admins()

            if admin_count <= 1:
                raise LastActiveAdminError()

        try:
            await self.repository.delete(user)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
