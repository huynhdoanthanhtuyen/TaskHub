from dataclasses import dataclass
from uuid import UUID


@dataclass
class Task:
    id: UUID
    title: str
    description: str | None
    completed: bool = False
