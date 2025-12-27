from httpx import get
from pydantic import EmailStr
from sqlmodel import Session
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
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def verify_by_email(self, email: EmailStr, session: AsyncSession):
        user = await self.get_user(email, session)

        user.is_verified = True

        try:
            await session.commit()

            return user

        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )

    async def delete_user(self, id, session: AsyncSession):

        user = await self.get_user_by_id(id, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
            )

        print(user)
        try:
            await session.delete(user)
            await session.commit()

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )

    async def get_user_by_id(self, id, session: AsyncSession):
        statement = select(User).where(User.id == id)
        result = await session.execute(statement=statement)

        return result.scalar_one_or_none()

    async def reset_password(self, email, password, session: AsyncSession):
        user = await self.get_user(email=email, session=session)
        user.password = password
        try:
            await session.commit()

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
