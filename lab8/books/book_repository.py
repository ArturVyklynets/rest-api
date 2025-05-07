import time
import redis.asyncio as redis

from beanie import PydanticObjectId
from fastapi import HTTPException, Request

from db.mongo import books_collection
from .models import Book




class BookRepository:
    RATE_LIMITS = {
      "authenticated": (8, 60),
      "anonymous": (2, 60),
    }

    @staticmethod
    async def get_books(limit: int = 10, cursor: int = 0):
        total = await books_collection.count_documents({})
        books_cursor = books_collection.find({}).skip(cursor).limit(limit + 1)
        books = await books_cursor.to_list(length=limit + 1)

        has_more = len(books) > limit
        items = books[:limit]

        for book in items:
            book['id'] = str(book['_id'])
            book.pop('_id', None)

        next_cursor = cursor + limit if has_more else None
        previous_cursor = cursor - limit if cursor - limit >= 0 else None
        return {
            "items": items,
            "next_cursor": next_cursor,
            "previous_cursor": previous_cursor,
            "total": total
        }

    @staticmethod
    async def get_book(book_id_param: str):
        try:
            object_id = PydanticObjectId(book_id_param)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid book ID format")

        book = await books_collection.find_one({"_id": object_id})
        if book:
            return Book(**book).to_dict()
        return None

    @staticmethod
    async def delete_book(book_id_param: str):
        try:
            object_id = PydanticObjectId(book_id_param)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        result = await books_collection.delete_one({"_id": object_id})
        return result.deleted_count > 0

    @staticmethod
    async def add_book(book_data):
        if await books_collection.find_one({"title": book_data["title"], "author": book_data["author"]}):
            raise ValueError("A book with this title and author already exists.")

        book = Book(**book_data)

        result = await books_collection.insert_one(book.dict())
        book.id = str(result.inserted_id)

        return book.to_dict()
    
    @classmethod
    async def rate_limit(self, request: Request, user_id: str | None):
          r = redis.Redis(host="redis", port=6379, decode_responses=True)
          identity = user_id or request.client.host
          limit_type = "authenticated" if user_id else "anonymous"
          limit, period = BookRepository.RATE_LIMITS[limit_type]
          key = f"rate_limit_{identity}"
          now = int(time.time())
          window_start = now - period
          
          await r.zremrangebyscore(key, min=0, max=window_start)
          await r.zadd(key, {str(now): now})
          await r.expire(key, period)
          
          request_count = await r.zcount(key, min=window_start, max=now)
          
          if request_count > limit:
              raise HTTPException(
                  status_code=429,
                  detail=f"Too many requests. Limit is {limit} requests per {period} seconds"
              )
          await r.aclose()