from sqlmodel import desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from .models import Todo
import uuid
from .schemas import TodoCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


class TodoService:

    async def get_all_todos(self, user_id, session: AsyncSession):
        statement = (
            select(Todo).where(Todo.owner_id == user_id).order_by(desc(Todo.created_at))
        )

        result = await session.execute(statement)
        return result.scalars().all()

    async def get_todo(self, user_id, todo_id, session: AsyncSession):
        statement = select(Todo).where(Todo.id == todo_id, Todo.owner_id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def create_todo(self, todo_data: TodoCreate, session: AsyncSession):
        new_todo = Todo(**todo_data.model_dump())

        try:
            session.add(new_todo)
            await session.commit()
            await session.refresh(new_todo)
            return new_todo

        except IntegrityError:
            session.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
