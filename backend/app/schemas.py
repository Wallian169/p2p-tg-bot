from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, field_validator, Field


class ORMBase(BaseModel):
    model_config = {"from_attributes": True}


class PaymentMethodBase(ORMBase):
    name: str


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodRead(PaymentMethodBase):
    id: int


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
    description: Optional[str] = Field(None, max_length=200)

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class OrderCreate(OrderBase):
    payment_method_ids: List[int] = []


class OrderUpdate(ORMBase):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    payment_method_ids: Optional[List[int]] = None

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
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    owner: UserRead
    currency_obj: CurrencyRead
    payment_methods: List[PaymentMethodRead]
