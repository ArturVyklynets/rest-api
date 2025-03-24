from fastapi import FastAPI
from books.router import books_router

app = FastAPI()

app.include_router(books_router)
