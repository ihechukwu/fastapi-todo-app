import uuid
from pydantic import BaseModel, EmailStr


class TokenData(BaseModel):
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):

    id: uuid.UUID
    email: EmailStr

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):

    user: UserPublic
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True
