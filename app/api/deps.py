from typing import Annotated

import jwt
from fastapi import Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.service import CacheService
from app.core.constants import (
    DEFAULT_OFFSET,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MIN_OFFSET,
    MIN_PAGE_SIZE,
    SEARCH_MAX_LENGTH,
)
from app.core.enums import UserRole
from app.core.exceptions import (
    InactiveUserError,
    InvalidTokenError,
    PermissionDeniedError,
)
from app.core.jwt import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

DbSession = Annotated[AsyncSession, Depends(get_db)]
bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
]


async def get_current_user(credentials: BearerCredentials, session: DbSession) -> User:
    if credentials is None:
        raise InvalidTokenError()
    try:
        payload = decode_token(credentials.credentials, "access")
        user_id = payload.sub
    except (jwt.InvalidTokenError, ValueError, KeyError) as exc:
        raise InvalidTokenError() from exc
    repository = UserRepository(session)
    user = await repository.get_by_id(user_id)
    if user is None:
        raise InvalidTokenError()
    if not user.is_active:
        raise InactiveUserError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.ADMIN:
        raise PermissionDeniedError()
    return current_user


AdminUser = Annotated[User, Depends(require_admin)]


class PaginationParams:
    def __init__(
        self,
        offset: int = Query(
            default=DEFAULT_OFFSET,
            ge=MIN_OFFSET,
        ),
        limit: int = Query(
            default=DEFAULT_PAGE_SIZE,
            ge=MIN_PAGE_SIZE,
            le=MAX_PAGE_SIZE,
        ),
    ):
        self.offset = offset
        self.limit = limit


PaginationDep = Annotated[
    PaginationParams,
    Depends(PaginationParams),
]

class SearchParams:
    def __init__(
        self,
        search: str | None = Query(
            default=None,
            max_length=SEARCH_MAX_LENGTH,
            description="Keyword for case-insensitive searching",
        ),
    ):
        self.search = search.strip() or None if search else None


SearchDep = Annotated[
    SearchParams,
    Depends(SearchParams),
]

def get_cache_service(request: Request) -> CacheService:
    client = getattr(
        request.app.state,
        "redis",
        None,
    )

    return CacheService(client)


CacheDep = Annotated[
    CacheService,
    Depends(get_cache_service),
]