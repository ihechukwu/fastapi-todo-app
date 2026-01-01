from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi import Depends, HTTPException, status, Request
import jwt
from ..core.config import settings
from .schemas import TokenData
from app.users.service import UserService
from ..core.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import decode_access_token
from app.core.redis import token_in_blocklist
from typing import List


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

user_service = UserService()


"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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
"""


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = self.token_is_valid(token)

        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        self.verify_access_token(token_data)

        return token_data

    def token_is_valid(self, token: str) -> bool:
        token_data = decode_access_token(token)
        return token_data

    def verify_access_token(self, token_data: dict):
        raise NotImplementedError("Please override this method in child class")


class AccessTokenBearer(TokenBearer):
    def verify_access_token(self, token_data: dict):

        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_access_token(self, token_data: dict):

        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide refresh token",
            )


async def get_current_user(
    user_credentials: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    email = user_credentials["email"]

    user = await user_service.get_user(email, session)
    return user


class RoleChecker:
    """
    Docstring for RoleChecker
    This is the role checker class, it takes a list of roles
    """

    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user=Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied"
            )

        elif not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please verify your account first",
            )
