from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


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
    telegram_id: int
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
    currency_id: int
    action: OrderAction
    amount: Decimal = Field(
        max_digits=10,
        decimal_places=2,
        examples=[100.50],
    )
    rate: Decimal = Field(max_digits=5, decimal_places=2, examples=[41.50])
    description: str | None = Field(None, max_length=200)

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class OrderCreate(OrderBase):
    payment_methods: list[int] = []

    @field_validator("payment_methods")
    @classmethod
    def check_at_least_one_method(cls, v: list[int]) -> list[int]:
        if not v or len(v) == 0:
            raise ValueError("At least one method must be provided")
        return v


class OrderUpdate(ORMBase):
    amount: Decimal | None = None
    description: str | None = None
    payment_method_ids: list[int] | None = None

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class OrderRead(OrderBase):
    id: int
    owner_id: int
    currency_id: int
    description: str | None
    created_at: datetime
    updated_at: datetime

    owner: UserRead
    currency_obj: CurrencyRead
    payment_methods: list[PaymentMethodRead]
