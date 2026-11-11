from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdminManagementLock(Base):
    __tablename__ = "admin_management_locks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
