from __future__ import annotations
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from starlette import status

from app.db_session import get_session
from app.models import Order, User, PaymentMethod, OrderAction, OrderStatus
from app.schemas import OrderCreate, OrderRead

orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    user_uuid: str,
    session: AsyncSession = Depends(get_session),
):
    user_res = await session.execute(select(User).where(User.uuid == user_uuid))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_uuid} not found")
    method_ids = order_in.payment_methods
    res = await session.execute(select(PaymentMethod).where(PaymentMethod.id.in_(method_ids)))
    existing_methods: list[PaymentMethod] = list(res.scalars().all())
    if len(existing_methods) != len(method_ids):
        raise HTTPException(status_code=400, detail="Selected unexisting payment methods")

    new_order = Order(
        **order_in.model_dump(exclude={"payment_methods"}),
        owner_id=user.id,
        payment_methods=existing_methods,
    )

    session.add(new_order)
    await session.commit()
    stmt = (
        select(Order)
        .options(
            joinedload(Order.owner),
            joinedload(Order.currency_obj),
            selectinload(Order.payment_methods),
        )
        .where(Order.id == new_order.id)
    )
    result = await session.execute(stmt)
    order_with_data = result.scalar_one()
    return order_with_data


ORDERS_PER_PAGE = 20


@orders_router.get("/", response_model=List[OrderRead])
async def get_orders(
    currency_id: int,
    action: Annotated[OrderAction, Query(description="Buy or sell")],
    page: Annotated[int, Query(ge=0)] = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Order)
        .options(joinedload(Order.owner), selectinload(Order.payment_methods))
        .where(
            Order.currency_id == currency_id,
            Order.status == OrderStatus.ACTIVE,
            Order.action == action,
        )
    )

    if action == OrderAction.BUY:
        stmt = stmt.order_by(Order.rate.desc())
    else:
        stmt = stmt.order_by(Order.rate.asc())

    skip = (page - 1) * ORDERS_PER_PAGE

    stmt = stmt.offset(skip).limit(ORDERS_PER_PAGE)

    result = await session.execute(stmt)
    return result.scalars().unique().all()
