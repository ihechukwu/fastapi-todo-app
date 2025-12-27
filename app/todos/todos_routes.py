from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from .service import TodoService
from .schemas import TodoCreate, TodoResponse
from app.core.database import get_session
from app.auth.dependencies import get_current_user, RoleChecker
from sqlmodel.ext.asyncio.session import AsyncSession


todos_router = APIRouter()

todo_service = TodoService()


@todos_router.get("/")
async def get_all_todos(
    user_credentials: dict = Depends(get_current_user),
    _=Depends(RoleChecker(["admin", "user"])),
    session: AsyncSession = Depends(get_session),
):
    user_id = user_credentials.id

    todo = await todo_service.get_all_todos(user_id=user_id, session=session)
    return todo


@todos_router.post("/", response_model=TodoResponse)
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
