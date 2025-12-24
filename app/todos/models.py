from sqlalchemy import table
from sqlmodel import SQLModel, Relationship, Field
from typing import Optional
import uuid


from app.users import models
from datetime import datetime


class Todo(SQLModel, table=True):

    __tablename__ = "todos"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = None
    completed: bool = False
    owner_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    owner: Optional["models.User"] = Relationship(back_populates="todos")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def __repr__(self) -> str:
        return f"<Title {self.title}"
