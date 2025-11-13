from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Enum, Numeric, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Picture(Base):
    __tablename__ = 'pictures'
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(255), nullable=False)

class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    icon: Mapped[str | None] = mapped_column(String, nullable=True)  # path to picture

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

    owner = relationship("User", lazy="joined")
    currency_obj = relationship("Currency", lazy="joined")