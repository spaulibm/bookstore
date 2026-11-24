from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import auth, books


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Bookstore API", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(books.router)
