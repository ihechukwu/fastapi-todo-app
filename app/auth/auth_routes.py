from fastapi import Depends, APIRouter, HTTPException, status
from app.core.database import get_session
from app.users.service import UserService
from .schemas import UserLogin
from sqlmodel.ext.asyncio.session import AsyncSession
from . import utils


auth_router = APIRouter()

user_service = UserService()


@auth_router.post("/login")
async def login_user(
    user_data: UserLogin, session: AsyncSession = Depends(get_session)
):

    user = await user_service.get_user(email=user_data.email, session=session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Does not exist"
        )

    is_password_valid = utils.verify_password(user_data.password, user.password)

    if not is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    access_token = utils.create_access_token(
        data={"email": user.email, "user_id": user.id}
    )
