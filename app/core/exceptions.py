from uuid import UUID

from app.core.constants import TASK_NOT_FOUND_MESSAGE


class TaskNotFoundError(Exception):
    def __init__(self, task_id: UUID | str):
        self.task_id = task_id
        message = TASK_NOT_FOUND_MESSAGE.format(task_id=task_id)
        super().__init__(message)


class RelatedResourceNotFoundError(Exception):
    def __init__(self, resource: str, resource_id: UUID):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} with ID {resource_id} not found")