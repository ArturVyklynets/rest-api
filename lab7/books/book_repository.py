from beanie import PydanticObjectId
from fastapi import HTTPException

from db.mongo import books_collection
from .models import Book


class BookRepository:
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
