from pwdlib import PasswordHash
import jwt
from datetime import timedelta, datetime
from app.core.config import settings
import uuid
from fastapi import HTTPException, status
from itsdangerous import URLSafeTimedSerializer

password_hash = PasswordHash.recommended()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTE = settings.ACCESS_TOKEN_EXPIRE_MINUTE


def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(data: dict, expire: timedelta = None, refresh: bool = False):
    to_encode = data.copy()
    if expire:
        expire = datetime.utcnow() + expire
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)

    to_encode.update({"exp": expire, "jti": str(uuid.uuid4()), "refresh": refresh})
    try:

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    except jwt.PyJWTError:
        raise credentials_exception

    return encoded_jwt


def decode_access_token(token: str):

    try:

        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])

        return payload

    except jwt.PyJWTError:
        raise credentials_exception


token_serializer = URLSafeTimedSerializer(
    secret_key=settings.SECRET_KEY, salt="email-configuration"
)


def create_url_safe_token(data: dict):
    token = token_serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):

    try:
        token_data = token_serializer.loads(token)

        return token_data

    except Exception:
        raise credentials_exception
