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


class LastActiveAdminError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message=messages.LAST_ACTIVE_ADMIN,
            status_code=status.HTTP_409_CONFLICT,
        )


class CannotDeleteSelfError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message=messages.CANNOT_DELETE_SELF,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class CannotModifySelfError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.CANNOT_DEMOTE_OR_DEACTIVATE,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UserHasRelatedResourcesError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message=messages.USER_HAS_RELATED_RESOURCES,
            status_code=status.HTTP_409_CONFLICT,
        )


class NewPasswordSameAsOldError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message=messages.NEW_PASSWORD_SAME_AS_OLD,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class WorkspaceNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class WorkspaceAccessDeniedError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_ACCESS_DENIED,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class WorkspaceOwnerRequiredError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_OWNER_REQUIRED,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class WorkspaceMemberNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_MEMBER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class WorkspaceMemberAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_MEMBER_ALREADY_EXISTS,
            status_code=status.HTTP_409_CONFLICT,
        )


class WorkspaceOwnerCannotBeRemovedError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_OWNER_CANNOT_BE_REMOVED,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class WorkspaceOwnerCannotBeInvitedError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_OWNER_CANNOT_BE_INVITED,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class WorkspaceMemberUserNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_MEMBER_USER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class WorkspaceHasProjectsError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_HAS_PROJECTS,
            status_code=status.HTTP_409_CONFLICT,
        )


class WorkspaceInvalidRoleError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.WORKSPACE_INVALID_ROLE,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ProjectNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.PROJECT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ProjectHasRelatedResourcesError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.PROJECT_HAS_RELATED_RESOURCES,
            status_code=status.HTTP_409_CONFLICT,
        )


class TaskAssigneeNotMemberError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.TASK_ASSIGNEE_NOT_MEMBER,
            status_code=status.HTTP_400_BAD_REQUEST,
        )




class LabelNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.LABEL_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class LabelAlreadyAttachedError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.LABEL_ALREADY_ATTACHED,
            status_code=status.HTTP_409_CONFLICT,
        )


class LabelNotAttachedError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.LABEL_NOT_ATTACHED,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class LabelProjectMismatchError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.LABEL_PROJECT_MISMATCH,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class LabelAttachConflictError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.LABEL_ATTACH_CONFLICT,
            status_code=status.HTTP_409_CONFLICT,
        )




class CommentNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.COMMENT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class CommentEditForbiddenError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.COMMENT_EDIT_FORBIDDEN,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class CommentDeleteForbiddenError(AppException):
    def __init__(self):
        super().__init__(
            message=messages.COMMENT_DELETE_FORBIDDEN,
            status_code=status.HTTP_403_FORBIDDEN,
        )
