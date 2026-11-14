import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    LABEL_COLOR_MAX_LENGTH,
    LABEL_NAME_MAX_LENGTH,
)
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task_label import TaskLabel


class Label(Base):
    __tablename__ = "labels"

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

    name: Mapped[str] = mapped_column(
        String(LABEL_NAME_MAX_LENGTH),
        nullable=False,
    )

    color: Mapped[str] = mapped_column(
        String(LABEL_COLOR_MAX_LENGTH),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="labels",
    )

    task_labels: Mapped[list["TaskLabel"]] = relationship(
        "TaskLabel",
        back_populates="label",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
