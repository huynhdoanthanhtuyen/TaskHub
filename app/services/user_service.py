from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.enums import UserRole
from app.core.exceptions import (
    CannotDeleteSelfError,
    CannotModifySelfError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    LastActiveAdminError,
    NewPasswordSameAsOldError,
    UserHasRelatedResourcesError,
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

    async def change_password(
        self,
        user: User,
        data: PasswordChange,
    ) -> None:
        is_valid = await run_in_threadpool(
            verify_password,
            data.old_password,
            user.hashed_password,
        )

        if not is_valid:
            raise InvalidCredentialsError()
        if data.new_password == data.old_password:
            raise NewPasswordSameAsOldError()

        new_hashed_password = await run_in_threadpool(
            hash_password,
            data.new_password,
        )

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

    async def list_users(
        self,
        offset: int,
        limit: int,
    ) -> dict:
        items = await self.repository.get_paginated(offset, limit)
        total = await self.repository.count_users()

        return {
            "items": items,
            "total": total,
        }
    async def admin_update_user(
        self,
        user_id: UUID,
        data: UserAdminUpdate,
        current_admin: User,
    ) -> User:
        update_data = data.model_dump(exclude_unset=True)

        try:
            await self.repository.lock_admin_management()

            user = await self.repository.get_by_id_fresh(user_id)

            if user is None:
                raise UserNotFoundError(user_id=user_id)

            if not update_data:
                await self.session.commit()
                return user

            if user_id == current_admin.id and (
                update_data.get("role", user.role) != UserRole.ADMIN
                or update_data.get("is_active", user.is_active) is False
            ):
                raise CannotModifySelfError()

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

            for field, value in update_data.items():
                setattr(user, field, value)

            await self.session.commit()
            await self.session.refresh(user)

            return user

        except Exception:
            await self.session.rollback()
            raise

    async def delete_user(
        self,
        user_id: UUID,
        current_admin: User,
    ) -> None:
        if user_id == current_admin.id:
            raise CannotDeleteSelfError()

        try:
            await self.repository.lock_admin_management()

            user = await self.repository.get_by_id_fresh(user_id)

            if user is None:
                raise UserNotFoundError(user_id=user_id)

            if user.role == UserRole.ADMIN and user.is_active:
                admin_count = await self.repository.count_active_admins()

                if admin_count <= 1:
                    raise LastActiveAdminError()

            await self.repository.delete(user)
            await self.session.commit()

        except IntegrityError as exc:
            await self.session.rollback()
            raise UserHasRelatedResourcesError() from exc

        except Exception:
            await self.session.rollback()
            raise
