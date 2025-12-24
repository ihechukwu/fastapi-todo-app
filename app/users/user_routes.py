from fastapi import APIRouter, Depends
from app.core.database import get_session
from .service import UserService
from .schemas import UserCreate, UserResponse
from sqlmodel.ext.asyncio.session import AsyncSession


user_service = UserService()

users_router = APIRouter()


@users_router.post("/signup", response_model=UserResponse)
async def create_account(
    user: UserCreate, session: AsyncSession = Depends(get_session)
):
    new_user = await user_service.create_user(user, session)

    return new_user


@users_router.get("/me/{email}", response_model=UserResponse)
async def get_user(email: str, session: AsyncSession = Depends(get_session)):

    user = await user_service.get_user(email, session)

    return user
