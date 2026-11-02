import uuid
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Task(Base):
  __tablename__ ="tasks"
  id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  title: Mapped[str]= mapped_column(String(200), nullable=False)
  description: Mapped[str|None]= mapped_column(Text,nullable= True)
  completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
