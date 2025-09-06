from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    UUID4,
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


def validate_password(value: str) -> str:
    validations = [
        (
            lambda v: any(char.isdigit() for char in v),
            "Password must contain at least one digit",
        ),
        (
            lambda v: any(char.isupper() for char in v),
            "Password must contain at least one uppercase letter",
        ),
        (
            lambda v: any(char.islower() for char in v),
            "Password must contain at least one lowercase letter",
        ),
    ]
    for condition, error_message in validations:
        if not condition(value):
            raise ValueError(error_message)
    return value


ValidPassword = Annotated[
    str, Field(min_length=8, max_length=64), AfterValidator(validate_password)
]


class UserBase(BaseModel):
    email: EmailStr
    role: Literal["USER"] = "USER"

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: ValidPassword


class UserDB(UserBase):
    hashed_password: str


class UserResponse(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
