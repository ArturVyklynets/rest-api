import pytest
import pytest_asyncio
from datetime import timedelta
import redis.asyncio as redis
from httpx import AsyncClient, ASGITransport
from books.book_repository import BookRepository
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth.security import create_access_token
from main import app

@pytest_asyncio.fixture(scope="function")
async def redis_client():
    client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()

@pytest_asyncio.fixture(autouse=True)
async def clear_redis(redis_client):
    keys = await redis_client.keys("rate_limit_*")
    if keys:
        await redis_client.delete(*keys)
    yield

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client
    finally:
        await client.aclose()
        await transport.aclose()

@pytest.fixture
def access_token():
    return create_access_token(
        data={"sub": "testusername"}, 
        expires_delta=timedelta(minutes=10)
    )

@pytest.fixture
async def book_repo():
    repo = BookRepository()
    yield repo
    await repo.close_redis()

@pytest.mark.asyncio
async def test_authenticated_user_over_limit(async_client, access_token, book_repo):
    headers = {"Authorization": f"Bearer {access_token}"}
    responses = []
    
    for _ in range(8):
        response = await async_client.get("/books", headers=headers)
        responses.append(response)
        await asyncio.sleep(1)
    
    for r in responses:
        assert r.status_code == 200
    
    response = await async_client.get("/books", headers=headers)
    assert response.status_code == 429
    assert "Too many requests." in response.text

@pytest.mark.asyncio
async def test_anonymous_user_under_limit(async_client):
    for _ in range(2):
        response = await async_client.get("/books")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_anonymous_user_over_limit(async_client):
    for _ in range(2):
        response = await async_client.get("/books")
        assert response.status_code == 401
    
    response = await async_client.get("/books")
    assert response.status_code == 401