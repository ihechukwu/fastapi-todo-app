from httpx import get
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import User
from .schemas import UserCreate
import logging
from ..auth.utils import get_password_hash
from sqlalchemy import select


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

        except Exception as e:
            await session.rollback()

            logging.exception(e)

    async def get_user(self, email: str, session: AsyncSession):
        statment = select(User).where(User.email == email)
        result = await session.execute(statment)
        return result.scalar_one_or_none()
