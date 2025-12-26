from sqlalchemy import table
from sqlmodel import SQLModel, Field, Relationship
from typing import List
import uuid
from pydantic import EmailStr

from app.todos import models
from datetime import datetime

"""
Contains the user model for creating the database
"""


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(primary_key=True, nullable=False, default_factory=uuid.uuid4)
    first_name: str
    last_name: str
    email: EmailStr = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    role: str
    is_verified: bool = Field(default=False)

    todos: List["models.Todo"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def __repr__(self):
        return f"<User {self.email}"
