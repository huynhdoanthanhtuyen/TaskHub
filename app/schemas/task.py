from uuid import UUID
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
  title:str = Field(min_length=1, max_length=200, description="Title of task")
  description:str|None = None

class TaskUpdate(BaseModel):
  title:str|None = Field(default= None,min_length=1, max_length=200)
  description:str|None = None
  completed:bool|None = None

class TaskResponse(BaseModel):
  id: UUID
  title: str
  description: str |None
  completed: bool
