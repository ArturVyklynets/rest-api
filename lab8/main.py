from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis
from auth.auth_router import auth_router
from books.router import books_router
from db.mongo import books_collection
from books.book_repository import BookRepository

sample_books = [
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "genre": "Fiction", "pages": 218},
    {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "pages": 328, "year": 1949},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Fiction", "pages": 281, "year": 1960},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Fiction", "pages": 277, "year": 1951},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Romance", "pages": 279, "year": 1813},
]


async def add_sample_books():
    count = await books_collection.count_documents({})
    if count == 0:
        await books_collection.insert_many(sample_books)
        print("Sample books added to the database.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    book_repo = BookRepository()
    await book_repo.get_redis()
    await add_sample_books()
    print("App startup completed")

    yield

    await book_repo.close_redis()
    print("App shutting down")


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(books_router)
