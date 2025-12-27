from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import uuid
from app.users.schemas import UserResponse


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    completed: bool
    owner_id: uuid.UUID
    owner: UserResponse
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TodoUpdate(TodoCreate):
    pass
