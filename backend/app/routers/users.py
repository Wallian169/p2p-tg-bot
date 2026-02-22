from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db_session import get_session
from app.models import User
from app.schemas import UserCreate, UserRead

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"description": "User already registered or other client error"}},
)
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    # Перевіряємо, чи юзер уже існує
    existing = await session.execute(select(User).where(User.telegram_id == user_in.telegram_id))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail=f"User with {User.telegram_id=} already exists")

    new_user = User(**user_in.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@user_router.get("/me", response_model=UserRead, responses={404: {"description": "User not found"}})
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")
