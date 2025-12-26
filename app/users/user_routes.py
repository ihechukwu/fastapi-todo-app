from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from app.auth import auth_routes
from app.core.database import get_session
from .service import UserService
from .schemas import UserCreate, UserResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.auth.dependencies import RefreshTokenBearer, get_current_user, RoleChecker
from app.core.mail import create_message, mail
from app.auth.utils import create_url_safe_token
from app.core.config import settings


user_service = UserService()

users_router = APIRouter()


@users_router.post("/signup")
async def create_account(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    new_user = await user_service.create_user(user, session)
    token = create_url_safe_token({"email": new_user.email})
    link = f"http://{settings.DOMAIN}/api/v1/auth/verify-email/{token}"

    html_message = f"""<h1>Welcome to Todo App </h1> 
    
    <p> Click <a href="{link}">here</a> to verify email </p>
    
    """
    subject = "Account Verification"
    message = create_message([new_user.email], subject=subject, body=html_message)
    background_tasks.add_task(mail.send_message, message)

    return JSONResponse(
        content={
            "msg": "Account creation successful please check your email for verification"
        },
    )


@users_router.get("/me", response_model=UserResponse)
async def get_user(
    user=Depends(get_current_user), _=Depends(RoleChecker(["admin", "user"]))
):

    return user
