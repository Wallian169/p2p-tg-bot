from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db_session import get_session
from app.models import Currency
from app.schemas import CurrencyCreate, CurrencyRead

currency_router = APIRouter(prefix="/currencies", tags=["Currencies"])

@currency_router.post("/", response_model=CurrencyRead, status_code=status.HTTP_201_CREATED)
async def create_currency(
    currency_in: CurrencyCreate,
    session: AsyncSession = Depends(get_session)
):
    new_currency = Currency(**currency_in.model_dump())
    session.add(new_currency)
    await session.commit()
    await session.refresh(new_currency)
    return new_currency

@currency_router.get("/", response_model=list[CurrencyRead])
async def list_currencies(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Currency))
    return result.scalars().all()
