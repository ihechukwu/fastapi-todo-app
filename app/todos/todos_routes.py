import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.todos.models import Todo
from .service import TodoService
from .schemas import TodoCreate, TodoResponse, TodoUpdate
from app.core.database import get_session
from app.auth.dependencies import get_current_user, RoleChecker
from sqlmodel.ext.asyncio.session import AsyncSession


todos_router = APIRouter()

todo_service = TodoService()


@todos_router.get("/")
async def get_all_todos(
    search: str | None = None,
    skip: int = 0,
    limit: int = 2,
    completed: bool = False,
    user_credentials: dict = Depends(get_current_user),
    _=Depends(RoleChecker(["admin", "user"])),
    session: AsyncSession = Depends(get_session),
):
    user_id = user_credentials.id

    todo = await todo_service.get_all_todos(
        user_id=user_id,
        search=search,
        skip=skip,
        limit=limit,
        completed=completed,
        session=session,
    )
    return todo


@todos_router.get("/{id}")
async def get_todo(
    id: uuid.UUID,
    user_credentials: dict = Depends(get_current_user),
    _=Depends(RoleChecker(["admin", "user"])),
    session: AsyncSession = Depends(get_session),
):
    user_id = user_credentials.id
    todo = await todo_service.get_todo(user_id=user_id, todo_id=id, session=session)
    return todo


@todos_router.post(
    "/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED
)
async def create_todo(
    todo_data: TodoCreate,
    user_credentials: dict = Depends(get_current_user),
    _=Depends(RoleChecker(["admin", "user"])),
    session: AsyncSession = Depends(get_session),
):

    owner_id = user_credentials.id

    new_todo = await todo_service.create_todo(
        todo_data=todo_data, owner_id=owner_id, session=session
    )

    return new_todo


@todos_router.put("/{id}")
async def update_todo(
    todo_data: TodoUpdate,
    id: uuid.UUID,
    user_credentials: dict = Depends(get_current_user),
    _=Depends(RoleChecker(["admin", "user"])),
    session: AsyncSession = Depends(get_session),
):
    user_id = user_credentials.id
    updated_todo = await todo_service.update_todo(
        todo_data=todo_data, user_id=user_id, todo_id=id, session=session
    )

    return updated_todo


@todos_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    id: uuid.UUID,
    user_credentials: dict = Depends(get_current_user),
    _=Depends(RoleChecker(["admin", "user"])),
    session: AsyncSession = Depends(get_session),
):

    user_id = user_credentials.id

    await todo_service.delete_todo(user_id=user_id, todo_id=id, session=session)
    return


@todos_router.get("/complete/{id}")
async def complete_todo(
    id: uuid.UUID,
    user_credentials: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):

    user_id = user_credentials.id
    todo = await todo_service.complete_todo(
        user_id=user_id, todo_id=id, session=session
    )

    return todo
