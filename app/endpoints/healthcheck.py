from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
async def healthcheck():
    return {
        "env": settings.ENVIRONMENT,
        "status": "OK",
    }
