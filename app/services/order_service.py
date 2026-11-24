"""Order service: checkout cart → order, status updates."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import Book, Order, OrderItem


async def checkout(db: AsyncSession, user_id: int, cart: dict[int, int]) -> Order:
    """
    cart: {book_id: quantity}
    Validates stock, creates Order + OrderItems, decrements stock.
    """
    if not cart:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    # Load all books in one query
    book_ids = list(cart.keys())
    result = await db.execute(select(Book).where(Book.id.in_(book_ids)))
    books = {b.id: b for b in result.scalars().all()}

    for book_id, qty in cart.items():
        if book_id not in books:
            raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
        if books[book_id].stock < qty:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock for '{books[book_id].title}'",
            )

    total = sum(books[bid].price * qty for bid, qty in cart.items())
    order = Order(user_id=user_id, status="pending", total=round(total, 2))
    db.add(order)
    await db.flush()  # get order.id

    for book_id, qty in cart.items():
        db.add(OrderItem(
            order_id=order.id,
            book_id=book_id,
            quantity=qty,
            unit_price=books[book_id].price,
        ))
        books[book_id].stock -= qty

    await db.commit()
    # Reload with items
    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items))
    )
    return result.scalar_one()


async def get_order(db: AsyncSession, order_id: int, user_id: int | None = None) -> Order:
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if user_id is not None and order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your order")
    return order


async def list_orders(db: AsyncSession, user_id: int) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def update_status(db: AsyncSession, order_id: int, new_status: str) -> Order:
    order = await get_order(db, order_id)
    order.status = new_status
    await db.commit()
    await db.refresh(order)
    return order
