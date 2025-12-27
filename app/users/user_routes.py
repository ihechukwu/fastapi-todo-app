from email import message
import uuid
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from urllib3 import HTTPResponse
from app.auth import auth_routes, utils
from app.core.database import get_session
from .service import UserService
from .schemas import PasswordReset, PasswordResetRequest, UserCreate, UserResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.auth.dependencies import RefreshTokenBearer, get_current_user, RoleChecker
from app.core.mail import create_message, mail
from app.auth.utils import create_url_safe_token, decode_url_safe_token
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


@users_router.delete("/admin/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: uuid.UUID,
    _=Depends(RoleChecker(["admin"])),
    session: AsyncSession = Depends(get_session),
):
    await user_service.delete_user(id=id, session=session)


@users_router.post("/password-reset-request")
async def password_reset_request(
    user_email_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):

    user_email = user_email_data.email
    user = await user_service.get_user(email=user_email, session=session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    token = create_url_safe_token({"email": user_email})

    link = f"http://{settings.DOMAIN}/api/v1/users/reset-password/{token}"

    html_body = f"""
<h2> Please click <a href="{link}">here </a> to reset password</h2>

"""
    subject = f"Password reset"

    message = create_message(recipients=[user_email], subject=subject, body=html_body)
    background_tasks.add_task(mail.send_message, message)

    return {"msg": "Please check email and change password"}


@users_router.post("/reset-password/{token}")
async def password_reset_verify(
    token: str,
    user_password: PasswordReset,
    session: AsyncSession = Depends(get_session),
):

    token_data = decode_url_safe_token(token)
    user_email = token_data["email"]
    hash_password = utils.get_password_hash(user_password.password)
    user = await user_service.reset_password(
        email=user_email, password=hash_password, session=session
    )

    return {"msg": "password reset successful, login now "}
