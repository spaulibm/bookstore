from __future__ import annotations
import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str
    created_at: datetime.datetime


# ─── Books ────────────────────────────────────────────────────────────────────

class BookCreate(BaseModel):
    isbn: str = Field(max_length=20)
    title: str = Field(max_length=255)
    author: str = Field(max_length=255)
    genre: str = Field(max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    cover_url: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    cover_url: Optional[str] = None


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    isbn: str
    title: str
    author: str
    genre: str
    price: float
    stock: int
    cover_url: Optional[str]


# ─── Cart ────────────────────────────────────────────────────────────────────

class CartItem(BaseModel):
    book_id: int
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    book_id: int
    title: str
    quantity: int
    unit_price: float
    subtotal: float


class CartOut(BaseModel):
    items: list[CartItemOut]
    total: float


# ─── Orders ──────────────────────────────────────────────────────────────────

class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    book_id: int
    quantity: int
    unit_price: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    total: float
    created_at: datetime.datetime
    items: list[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    status: Literal["pending", "paid", "shipped", "cancelled"]
