from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.database.session import get_db_session
from app.schemas.auth import Token, UserCreate, UserResponse
from app.services.auth import (
    auth_service,
    authenticate_user,
)

router = APIRouter()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    hashed_password = auth_service.get_password_hash(user_create.password)
    user = User(
        **user_create.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
    )
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the given email already exists",
        )
    return user


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(
        data={"sub": user.email},
    )
    return Token(access_token=access_token, token_type="bearer")
