from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.models import User
from app.database.session import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class AuthService:
    def __init__(self):
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        return self.context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.context.verify(plain_password, hashed_password)

    def create_access_token(
        self, data: dict, expires_delta: timedelta = timedelta(minutes=15)
    ):
        to_encode = data.copy()
        issued = datetime.now(timezone.utc)
        expiry = issued + expires_delta
        to_encode.update({"exp": expiry, "iat": issued})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt


auth_service = AuthService()


async def get_user(session: AsyncSession, email: str):
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> User | None:
    user = await get_user(session, email)
    if not user:
        return None
    if not auth_service.verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_db_session),
):
    CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise CREDENTIALS_EXCEPTION
    except jwt.InvalidTokenError:
        raise CREDENTIALS_EXCEPTION

    user = await get_user(session, email)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user
