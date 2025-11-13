from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Enum, Numeric, DateTime, func, Column, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    orders: Mapped[list["Order"]] = relationship(
        secondary="order_payment_methods",
        back_populates="payment_methods",
    )

order_payment_methods = Table(
    "order_payment_methods",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("payment_method_id", ForeignKey("payment_methods.id"), primary_key=True)
)

class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    icon: Mapped[str | None] = mapped_column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    picture: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False)


class OrderAction(PyEnum):
    BUY = "BUY"
    SELL = "SELL"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[OrderAction] = mapped_column(Enum(OrderAction, name="orderAction"), nullable=False)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    payment_methods: Mapped[list[PaymentMethod]] = relationship(
        secondary=order_payment_methods,
        back_populates="orders",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    owner = relationship("User")
    currency_obj = relationship("Currency")
