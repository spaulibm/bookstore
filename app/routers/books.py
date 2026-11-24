"""Books router: CRUD + search."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, require_admin
from app.schemas import BookCreate, BookUpdate, BookOut
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookOut])
async def list_books(
    q: Optional[str] = Query(None, description="Search title or author"),
    genre: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await book_service.list_books(db, q=q, genre=genre, limit=limit, offset=offset)


@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    return await book_service.get_book(db, book_id)


@router.post("", response_model=BookOut, status_code=201, dependencies=[Depends(require_admin)])
async def create_book(body: BookCreate, db: AsyncSession = Depends(get_db)):
    return await book_service.create_book(db, body)


@router.put("/{book_id}", response_model=BookOut, dependencies=[Depends(require_admin)])
async def update_book(book_id: int, body: BookUpdate, db: AsyncSession = Depends(get_db)):
    return await book_service.update_book(db, book_id, body)


@router.delete("/{book_id}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    await book_service.delete_book(db, book_id)
