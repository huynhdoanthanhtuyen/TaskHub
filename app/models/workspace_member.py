import uuid

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import WorkspaceRole
from app.db.base import Base
from app.models.user import User
from app.models.workspace import Workspace


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    role: Mapped[WorkspaceRole] = mapped_column(
        Enum(
            WorkspaceRole,
            name="workspace_role",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
        default=WorkspaceRole.VIEWER,
        server_default=WorkspaceRole.VIEWER.value,
    )

    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="members",
    )

    user: Mapped["User"] = relationship(
        "User",
    )
