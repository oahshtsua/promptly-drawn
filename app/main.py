from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.endpoints import auth, healthcheck, image_generation


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/api/docs/",
    lifespan=lifespan,
)

app.include_router(healthcheck.router)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(
    image_generation.router, prefix="/generation", tags=["Image Generation"]
)
