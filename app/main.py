from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.endpoints import healthcheck


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/api/docs/",
    lifespan=lifespan,
)

app.include_router(healthcheck.router)
