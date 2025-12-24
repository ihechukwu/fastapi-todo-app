from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
from ..core.config import settings
from .schemas import TokenData
from app.users.service import UserService
from ..core.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
user_service = UserService()


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise credential_exceptions
        token_data = TokenData(email=email)

        user = await user_service.get_user(email=token_data.email, session=session)

        if user is None:
            raise credential_exceptions

        return user

    except Exception:
        raise credential_exceptions
