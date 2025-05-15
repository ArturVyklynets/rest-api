from unittest.mock import AsyncMock, patch

import pytest
from fastapi import Request, HTTPException

from books.book_repository import BookRepository


@pytest.mark.asyncio
@patch("books.book_repository.redis.Redis")
async def test_rate_limit_authenticated_user_allowed(mock_redis_class):
    mock_redis = AsyncMock()
    mock_redis.zcount.return_value = 5
    mock_redis_class.return_value = mock_redis

    repo = BookRepository()

    class DummyRequest:
        client = type("Client", (), {"host": "1.2.3.4"})

    await repo.rate_limit(DummyRequest(), user_id="user123")


@pytest.mark.asyncio
@patch("books.book_repository.redis.Redis")
async def test_rate_limit_authenticated_user_blocked(mock_redis_class):
    mock_redis = AsyncMock()
    mock_redis.zcount.return_value = 9
    mock_redis_class.return_value = mock_redis

    repo = BookRepository()

    class DummyRequest:
        client = type("Client", (), {"host": "1.2.3.4"})

    with pytest.raises(HTTPException) as exc_info:
        await repo.rate_limit(DummyRequest(), user_id="user123")
    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
@patch("books.book_repository.redis.Redis")
async def test_rate_limit_anonymous_user_allowed(mock_redis_class):
    mock_redis = AsyncMock()
    mock_redis.zcount.return_value = 1
    mock_redis_class.return_value = mock_redis

    repo = BookRepository()

    class DummyRequest:
        client = type("Client", (), {"host": "1.2.3.4"})

    await repo.rate_limit(DummyRequest(), user_id=None)


@pytest.mark.asyncio
@patch("books.book_repository.redis.Redis")
async def test_rate_limit_anonymous_user_blocked(mock_redis_class):
    mock_redis = AsyncMock()
    mock_redis.zcount.return_value = 3
    mock_redis_class.return_value = mock_redis

    repo = BookRepository()

    class DummyRequest:
        client = type("Client", (), {"host": "1.2.3.4"})

    with pytest.raises(HTTPException) as exc_info:
        await repo.rate_limit(DummyRequest(), user_id=None)
    assert exc_info.value.status_code == 429
