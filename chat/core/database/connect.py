from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from settings import DB_SETTINGS


async_engine = create_async_engine(url=DB_SETTINGS.dsn, future=True, echo=True)
async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncSession:  # type: ignore
    session = async_session()
    yield session
    await session.rollback()
