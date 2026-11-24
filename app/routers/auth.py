"""Auth router: register + login."""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas import UserRegister, Token, UserOut
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await user_service.register_user(db, body.email, body.password)
    return user


@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Accepts application/x-www-form-urlencoded (username=email, password=...).
    Compatible with FastAPI's built-in OAuth2 form and Swagger UI.
    """
    user = await user_service.authenticate_user(db, form.username, form.password)
    token = user_service.create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
