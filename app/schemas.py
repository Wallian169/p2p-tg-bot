from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, field_validator


class ORMBase(BaseModel):
    model_config = {
        "from_attributes": True
    }


class Currency(ORMBase):
    name: str
    symbol: str
    icon: str | None = None


class CurrencyCreate(Currency):
    pass


class CurrencyUpdate(Currency):
    name: str | None = None
    symbol: str | None = None
    icon: str | None = None


class CurrencyRead(Currency):
    id: int


class UserBase(ORMBase):
    uuid: str
    username: str
    picture: str | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(ORMBase):
    username: str | None = None
    picture: str | None = None


class UserRead(UserBase):
    id: int

class OrderAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderBase(ORMBase):
    owner_id: int
    currency_id: int
    action: OrderAction
    amount: Decimal

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class OrderCreate(OrderBase):
    pass


class OrderUpdate(ORMBase):
    amount: Decimal | None = None

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class OrderRead(ORMBase):
    id: int
    owner_id: int
    currency_id: int
    action: OrderAction
    amount: Decimal
    created_at: datetime
    updated_at: datetime

    owner: UserRead
    currency: CurrencyRead

