from uuid import UUID

from fastapi import status

from app.core import messages


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
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
            status_code=status.HTTP_404_NOT_FOUND,
        )


class RelatedResourceNotFoundError(Exception):
    def __init__(self, resource: str, resource_id: UUID):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} with ID {resource_id} not found")


class UserNotFoundError(AppException):
    def __init__(self, user_id: UUID | str):
        self.user_id = user_id
        super().__init__(
            message=messages.USER_NOT_FOUND.format(user_id=user_id),
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.INVALID_TOKEN,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.INACTIVE_USER,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class PermissionDeniedError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.PERMISSION_DENIED,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class EmailAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.EMAIL_ALREADY_EXISTS,
            status_code=status.HTTP_409_CONFLICT,
        )