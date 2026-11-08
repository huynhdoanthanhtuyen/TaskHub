import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DESCRIPTION_MAX_LENGTH, TITLE_MAX_LENGTH
from app.core.enums import TaskPriority, TaskStatus
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.project import Project
    from app.models.task_label import TaskLabel
    from app.models.user import User


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(TITLE_MAX_LENGTH),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            name="task_status",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
        default=TaskStatus.TODO,
        server_default=TaskStatus.TODO.value,
    )

    priority: Mapped[TaskPriority] = mapped_column(
        Enum(
            TaskPriority,
            name="task_priority",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
        default=TaskPriority.MEDIUM,
        server_default=TaskPriority.MEDIUM.value,
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks",
    )

    assignee: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assignee_id],
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )

    labels: Mapped[list["TaskLabel"]] = relationship(
        "TaskLabel",
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
