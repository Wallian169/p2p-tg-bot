from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Enum, Numeric, DateTime, func, Column, Table, BigInteger
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
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    uuid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    picture: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False)


class OrderAction(PyEnum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(PyEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    HIDDEN = "HIDDEN"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[OrderAction] = mapped_column(Enum(OrderAction, name="orderAction"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="orderStatus"),
        default=OrderStatus.ACTIVE,
        nullable=False
    )
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"))
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
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

class DealStatus(PyEnum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    status: Mapped[DealStatus] = mapped_column(
        Enum(DealStatus, name="deal_status"),
        default=DealStatus.PENDING,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=15)
    )