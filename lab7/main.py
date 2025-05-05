from fastapi import FastAPI

from auth.auth_router import auth_router
from books.router import books_router
from db.mongo import books_collection

app = FastAPI()

app.include_router(auth_router)
app.include_router(books_router)

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
        for book in sample_books:
            await books_collection.insert_one(book)
        print("Sample books added to the database.")


@app.on_event("startup")
async def startup_db():
    await add_sample_books()
