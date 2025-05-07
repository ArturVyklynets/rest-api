import os

from fastapi import APIRouter, HTTPException, Query, Depends, Request, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .book_repository import BookRepository
from .schema import BookSchema
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
books_router = APIRouter()

book_repo = BookRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@books_router.get("/books")
async def get_all_books(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    cursor: int = Query(0, ge=0),
    authorization: Optional[str] = Header(default=None)
):
    user = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user = payload.get("sub")
        except JWTError:
            pass

    await book_repo.rate_limit(request, user)
    return await book_repo.get_books(limit=limit, cursor=cursor)

@books_router.get("/book/{book_id}")
async def get_book_by_id(request: Request, book_id: str, user: str = Depends(get_current_user)):
    
    await book_repo.rate_limit(request, user)
    book = await book_repo.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@books_router.delete("/book/{book_id}", status_code=204)
async def delete_book_by_id(request: Request, book_id: str, user: str = Depends(get_current_user)):
    await book_repo.rate_limit(request, user)
    if await book_repo.delete_book(book_id):
        return
    raise HTTPException(status_code=404, detail="Book not found")


@books_router.post("/books", response_model=BookSchema, status_code=201)
async def create_book(request: Request, book_data: BookSchema, user: str = Depends(get_current_user)):
    await book_repo.rate_limit(request, user)
    try:
        new_book = await book_repo.add_book(book_data.model_dump())
        return new_book
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
