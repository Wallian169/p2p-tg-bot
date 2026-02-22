from __future__ import annotations

import asyncio
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from starlette import status

from app.db_session import get_session
from app.models import Order, User, PaymentMethod, OrderAction, OrderStatus, Currency
from app.schemas import OrderCreate, OrderRead, OrderUpdate

orders_router = APIRouter(prefix="/orders", tags=["Orders"])
ORDERS_PER_PAGE = 20


@orders_router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    user_uuid: str,
    session: AsyncSession = Depends(get_session),
):
    user_stmt = select(User).where(User.uuid == user_uuid)
    curr_stmt = select(Currency).where(Currency.id == order_in.currency_id)
    meth_smth = session.execute(
        select(PaymentMethod).where(PaymentMethod.id.in_(order_in.payment_methods))
    )
    user = (await session.execute(user_stmt)).scalar_one_or_none()
    currency = (await session.execute(curr_stmt)).scalar_one_or_none()
    methods = list((await meth_smth).scalars().all())

    if not user:
        raise HTTPException(404, "User not found")
    if not currency:
        raise HTTPException(404, f"Currency with id {order_in.currency_id} not found")
    if len(methods) != len(order_in.payment_methods):
        raise HTTPException(400, "One or more payment methods are invalid")

    new_order = Order(
        **order_in.model_dump(exclude={"payment_methods"}),
        owner_id=user.id,
        payment_methods=methods,
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
    order_with_data = result.unique().scalar_one()
    return order_with_data


@orders_router.get("/", response_model=List[OrderRead])
async def get_orders(
    currency_id: int,
    action: Annotated[OrderAction, Query(description="Buy or sell")],
    page: Annotated[int, Query(ge=1)] = 1,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Order)
        .options(
            joinedload(Order.owner),
            joinedload(Order.currency_obj),
            selectinload(Order.payment_methods),
        )
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


@orders_router.patch("/{order_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
async def cancel_order(order_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order with {order_id} does not exist")

    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Order already canceled")

    order.status = OrderStatus.CANCELLED

    await session.commit()
    await session.refresh(order)  # Оновлюємо об'єкт перед поверненням

    return {"order_id": order.id, "status": order.status}


@orders_router.patch("/{order_id}/update", response_model=OrderRead, status_code=status.HTTP_200_OK)
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.payment_methods),
            selectinload(Order.owner),
            selectinload(Order.currency_obj),
        )
        .where(Order.id == order_id)
    )
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with {order_id} does not exist")
    if order.status != OrderStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active orders can be updated")

    update_data = order_in.model_dump(exclude_unset=True)
    p_method_ids = update_data.pop("payment_methods", None)

    for field, value in update_data.items():
        setattr(order, field, value)
    if p_method_ids is not None:
        methods_stmt = select(PaymentMethod).where(PaymentMethod.id.in_(p_method_ids))
        methods_res = await session.execute(methods_stmt)
        found_methods = methods_res.scalars().all()
        if not found_methods:
            raise HTTPException(status_code=404, detail="Methods do not exist")

        order.payment_methods = found_methods

    await session.commit()
    await session.refresh(order)
    return order
