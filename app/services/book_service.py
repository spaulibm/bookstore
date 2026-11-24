"""Book service: CRUD + search."""
from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status

from app.models import Book
from app.schemas import BookCreate, BookUpdate


async def list_books(
    db: AsyncSession,
    q: Optional[str] = None,
    genre: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Book]:
    stmt = select(Book)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(or_(Book.title.ilike(pattern), Book.author.ilike(pattern)))
    if genre:
        stmt = stmt.where(Book.genre.ilike(genre))
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_book(db: AsyncSession, book_id: int) -> Book:
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


async def create_book(db: AsyncSession, data: BookCreate) -> Book:
    book = Book(**data.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def update_book(db: AsyncSession, book_id: int, data: BookUpdate) -> Book:
    book = await get_book(db, book_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(book, field, value)
    await db.commit()
    await db.refresh(book)
    return book


async def delete_book(db: AsyncSession, book_id: int) -> None:
    book = await get_book(db, book_id)
    await db.delete(book)
    await db.commit()


async def list_genres(db: AsyncSession) -> list[str]:
    result = await db.execute(select(Book.genre).distinct())
    return [row[0] for row in result.all()]
