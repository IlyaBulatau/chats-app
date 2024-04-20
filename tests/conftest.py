import pytest
from pytest_factoryboy import register 
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.pool import NullPool

import asyncio

from chat.main import app, setup_mapper
from chat.settings import DB_SETTINGS
from chat.core.database.connect import get_db
from chat.core.database.tables import mapper_registry
from tests.factories.users import UserFactory


TEST_DB_NAME = "test_chat"


register(UserFactory)

@pytest.fixture(scope="session", autouse=True)
def set_session_provider_facotry(db_session):
    """Добавляет обьект сесси к фабрикам"""
    UserFactory.set_session(db_session)


@pytest.fixture(scope="session")
def client():
    """Клиент для запросов"""
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture(scope="session", autouse=True)
def prepare_table():
    """Маппит таблицы"""
    setup_mapper()


@pytest.fixture(scope="session", autouse=True)
async def db_session(event_loop):
    """Переопределяет получение БД сессии в тестах и приложении Depends"""
    DB_SETTINGS.name = TEST_DB_NAME
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-multiple-asyncio-event-loops
    engine = create_async_engine(DB_SETTINGS.dsn, future=True, poolclass=NullPool)
    session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

    async def override_session():
        yield session
    
    await clear_tables(session)
    app.dependency_overrides[get_db] = override_session

    async with session() as async_session:
        yield async_session
        

async def clear_tables(session: AsyncSession):
    tables = ", ".join([table_name for table_name in reversed(mapper_registry.metadata.tables)])
    clear_query = text(f"""TRUNCATE TABLE {tables} CASCADE""")
    
    async with session() as async_session:
        await async_session.execute(clear_query)
        await async_session.commit()


@pytest.fixture(scope="session")
def event_loop():
    # https://stackoverflow.com/questions/61022713/pytest-asyncio-has-a-closed-event-loop-but-only-when-running-all-tests
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()