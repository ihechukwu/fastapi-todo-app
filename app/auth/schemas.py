from pydantic import BaseModel, EmailStr


class TokenData(BaseModel):
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str
