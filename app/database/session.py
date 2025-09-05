from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)


async def get_db_session():
    async with async_session() as session:
        yield session
