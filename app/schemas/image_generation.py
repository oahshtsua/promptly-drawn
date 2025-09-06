from datetime import datetime
from typing import Annotated

from pydantic import UUID4, BaseModel, Field


class GeneratedImageBase(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    inference_steps: Annotated[int, Field(ge=0)] = 50


class GeneratedImageCreate(GeneratedImageBase):
    pass


class GeneratedImageRead(GeneratedImageBase):
    id: UUID4
    status: str
    filename: str
    created_at: datetime


class GeneratedImagePresignedUrl(BaseModel):
    id: UUID4
    url: str
    expiry: str
