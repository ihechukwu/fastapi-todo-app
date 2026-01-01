from datetime import datetime
from sqlmodel import desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from .models import Todo
import uuid
from .schemas import TodoCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


class TodoService:

    async def get_all_todos(
        self, user_id, search, skip, limit, completed, session: AsyncSession
    ):
        statement = (
            select(Todo).where(Todo.owner_id == user_id).order_by(desc(Todo.created_at))
        )

        if search:
            statement = statement.where(Todo.title.ilike(f"%{search.strip()}%"))

        statement = (
            statement.offset(skip).limit(limit=limit).where(Todo.completed == completed)
        )

        result = await session.execute(statement)
        return result.scalars().all()

    async def get_todo(self, user_id, todo_id, session: AsyncSession):
        statement = select(Todo).where(Todo.id == todo_id, Todo.owner_id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def create_todo(
        self, todo_data: TodoCreate, owner_id: uuid.UUID, session: AsyncSession
    ):
        new_todo = Todo(**todo_data.model_dump())

        new_todo.owner_id = owner_id

        print(new_todo)

        try:
            session.add(new_todo)
            await session.commit()
            await session.refresh(new_todo)
            return new_todo

        except IntegrityError as e:
            await session.rollback()
            print(e)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )

    async def update_todo(self, todo_data, user_id, todo_id, session: AsyncSession):

        todo = await self.get_todo(user_id=user_id, todo_id=todo_id, session=session)
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="not found"
            )

        todo_dict = todo_data.model_dump()

        for key, value in todo_dict.items():
            if hasattr(todo, key):
                setattr(todo, key, value)
                todo.updated_at = datetime.utcnow()

        await session.commit()

        return todo

    async def delete_todo(self, user_id, todo_id, session: AsyncSession):
        todo = await self.get_todo(user_id=user_id, todo_id=todo_id, session=session)

        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong"
            )

        await session.delete(todo)
        await session.commit()

        return

    async def complete_todo(self, user_id, todo_id, session: AsyncSession):
        todo = await self.get_todo(user_id=user_id, todo_id=todo_id, session=session)
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong"
            )

        todo.completed = True
        await session.commit()

        return todo
