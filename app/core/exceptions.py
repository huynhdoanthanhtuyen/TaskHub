from uuid import UUID

from app.core import messages


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        headers: dict[str, str] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.headers = headers
        super().__init__(message)


class TaskNotFoundError(AppException):
    def __init__(self, task_id: UUID | str):
        self.task_id = task_id
        super().__init__(
            message=messages.TASK_NOT_FOUND.format(task_id=task_id),
            status_code=404,
        )


class UserNotFoundError(AppException):
    def __init__(self, user_id: UUID | str):
        self.user_id = user_id
        super().__init__(
            message=messages.USER_NOT_FOUND.format(user_id=user_id),
            status_code=404,
        )


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.INVALID_CREDENTIALS,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.INVALID_TOKEN,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.INACTIVE_USER,
            status_code=403,
        )


class PermissionDeniedError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.PERMISSION_DENIED,
            status_code=403,
        )


class EmailAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.EMAIL_ALREADY_EXISTS,
            status_code=409,
        )


class LastActiveAdminError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message=messages.LAST_ACTIVE_ADMIN,
            status_code=409,
        )


class CannotDeleteSelfError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message=messages.CANNOT_DELETE_SELF,
            status_code=403,
        )
