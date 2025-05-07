import pytest
import pytest_asyncio
from datetime import timedelta
import redis.asyncio as redis
from httpx import AsyncClient, ASGITransport
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth.security import create_access_token
from main import app

# ---------- Redis клієнт ---------
@pytest_asyncio.fixture(scope="function")
async def redis_client():
    client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
# ---------- Очистка Redis перед кожним тестом ----------
@pytest_asyncio.fixture(autouse=True)
async def clear_redis(redis_client):
    keys = await redis_client.keys("rate_limit_*")
    if keys:
        await redis_client.delete(*keys)
    yield
    # Додаткове очищення після тесту, якщо потрібно
    keys = await redis_client.keys("rate_limit_*")
    if keys:
        await redis_client.delete(*keys)

# ---------- HTTP-клієнт з FastAPI app ----------
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client
    finally:
        await client.aclose()
        await transport.aclose()

# ---------- Токен для авторизованого користувача ----------
@pytest.fixture
def access_token():
    return create_access_token(
        data={"sub": "testusername"}, 
        expires_delta=timedelta(minutes=10)
    )

# # ---------- Тести для авторизованого користувача ----------
@pytest.mark.asyncio
async def test_authenticated_user_under_limit(async_client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    for _ in range(8):
        response = await async_client.get("/books", headers=headers)
        assert response.status_code == 200
        asyncio.sleep(1)

@pytest.mark.asyncio
async def test_authenticated_user_over_limit(async_client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    # Спочатку 8 успішних запитів
    for _ in range(8):
        response = await async_client.get("/books", headers=headers)
        assert response.status_code == 200
    
    # 9-й запит має повернути 429
    response = await async_client.get("/books", headers=headers)
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]

@pytest.mark.asyncio
async def test_anonymous_user_under_limit(async_client):
    for _ in range(2):
        response = await async_client.get("/books")
        assert response.status_code == 401  # Або 401, залежно від вашого API

@pytest.mark.asyncio
async def test_anonymous_user_over_limit(async_client):
    # Спочатку 2 запити
    for _ in range(2):
        response = await async_client.get("/books")
        assert response.status_code == 401  # Або 401
    
    # 3-й запит (якщо ліміт 2)
    response = await async_client.get("/books")
    assert response.status_code == 401