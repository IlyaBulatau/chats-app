import pytest
from httpx import AsyncClient, ASGITransport

from chat.main import app
from chat.settings import DB_SETTINGS


TEST_DB_NAME = "test_chat"


@pytest.fixture(scope="session")
def client():
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.fixture(autouse=True)
async def ovveride(monkeypatch):
    monkeypatch.setattr(DB_SETTINGS, "name", TEST_DB_NAME)
    # monkeypatch.setenv("DB_NAME", TEST_DB_NAME)
    