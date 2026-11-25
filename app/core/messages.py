# Authentication
INVALID_CREDENTIALS = "Invalid email or password"
INVALID_TOKEN = "Invalid or expired token"
INACTIVE_USER = "Inactive user"
EMAIL_ALREADY_EXISTS = "Email already exists"

# Authorization
PERMISSION_DENIED = "Permission denied"
ADMIN_REQUIRED = "Admin privileges required"
CANNOT_DELETE_SELF = "You cannot delete your own account"
LAST_ACTIVE_ADMIN = "Cannot remove the last active admin"

# Resources
TASK_NOT_FOUND = "Task not found"
USER_NOT_FOUND = "User with id {user_id} not found"

# Database
DATABASE_CONSTRAINT_VIOLATION = "Data violates a database constraint"
RESOURCE_ALREADY_EXISTS = "Resource already exists"

# USER VALIDATION
FULL_NAME_CANNOT_BE_NULL = "full_name cannot be null"
ROLE_CANNOT_BE_NULL = "role cannot be null"
IS_ACTIVE_CANNOT_BE_NULL = "is_active cannot be null"
FIELD_CANNOT_BE_NULL = "{field} cannot be null"
CANNOT_DEMOTE_OR_DEACTIVATE = "You cannot demote or deactive your own account"
LAST_ACTIVE_ADMIN = "Cannot remove the last active admin"
CANNOT_DELETE_SELF = "Admin cannot delete their own account"
USER_HAS_RELATED_RESOURCES = "Cannot delete user because related resources still exist."
NEW_PASSWORD_SAME_AS_OLD = "New password must be different from the current password."

# WORKSPACE
WORKSPACE_NOT_FOUND = "Workspace not found"
WORKSPACE_ACCESS_DENIED = "You do not have access to this workspace"
WORKSPACE_OWNER_REQUIRED = "Only the workspace owner can perform this action"

WORKSPACE_MEMBER_NOT_FOUND = "Workspace member not found"
WORKSPACE_MEMBER_ALREADY_EXISTS = "User is already a workspace member"
WORKSPACE_OWNER_CANNOT_BE_REMOVED = "Workspace owner cannot be removed"
WORKSPACE_OWNER_CANNOT_BE_INVITED = "Workspace owner already has access"
WORKSPACE_MEMBER_USER_NOT_FOUND = "User to invite was not found"
WORKSPACE_INVALID_ROLE = "Invalid workspace role"
WORKSPACE_HAS_PROJECTS = "Cannot delete workspace while it has projects"

# Project
PROJECT_NOT_FOUND = "Project not found."
PROJECT_HAS_RELATED_RESOURCES = (
    "Cannot delete project because it has related resources."
)
PROJECT_ARCHIVED = (
    "Project is archived. Restore it before making changes."
)
FIELD_CANNOT_BE_NULL = "{field} cannot be null"


TASK_ASSIGNEE_NOT_MEMBER = (
    "Assignee must be a member of the workspace."
)
TASK_ASSIGNEE_NOT_FOUND = "Assignee not found"
TASK_ASSIGNEE_INACTIVE = "Assignee is inactive"
TASK_DUE_DATE_MUST_BE_IN_FUTURE = "Due date must be in the future"