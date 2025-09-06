from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import GeneratedImage, User
from app.database.session import get_db_session
from app.schemas.image_generation import (
    GeneratedImageCreate,
    GeneratedImagePresignedUrl,
    GeneratedImageRead,
)
from app.services.auth import get_current_user
from app.services.storage import storage
from app.tasks.image_generation import text_to_image_generation

router = APIRouter()


@router.get("/", response_model=list[GeneratedImageRead])
async def list_generations(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    query = select(GeneratedImage).where(User.id == user.id)
    result = await session.execute(query)
    return result.scalars().all()


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=GeneratedImageRead,
)
async def submit_generation_request(
    request: GeneratedImageCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    image = GeneratedImage(
        **request.model_dump(),
        user_id=user.id,
        status="PENDING",
    )
    session.add(image)
    await session.commit()
    await session.refresh(image)

    text_to_image_generation.delay(req_id=image.id)
    return image


@router.get("/{id}/url")
async def get_presigned_url(
    id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    query = (
        select(GeneratedImage).where(GeneratedImage.id == id).where(User.id == user.id)
    )
    result = await session.execute(query)
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image with the given ID does not exist.",
        )
    if image.status == "FAILED":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image generation failed",
        )
    if image.status != "SUCCESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is not available yet. Try again later.",
        )
    url, expiry = storage.get_presigned_url(image.filename)
    return GeneratedImagePresignedUrl(id=image.id, url=url, expiry=expiry)
