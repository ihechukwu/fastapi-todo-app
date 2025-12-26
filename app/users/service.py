from httpx import get
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import User
from .schemas import UserCreate
from ..auth.utils import get_password_hash
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


class UserService:

    async def create_user(self, user: UserCreate, session: AsyncSession):

        new_user = User(**user.model_dump())
        new_user.password = get_password_hash(user.password)
        new_user.role = "user"

        try:
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return new_user

        except IntegrityError:
            await session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User Already Exists",
            )

    async def get_user(self, email: str, session: AsyncSession):
        statment = select(User).where(User.email == email)
        result = await session.execute(statment)
        return result.scalar_one_or_none()

    async def verify_by_email(self, email: EmailStr, session: AsyncSession):
        user = await self.get_user(email)

        user.is_verified = True

        try:
            session.add(user)
            await session.commit()

            await session.refresh(user)
            return user

        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
