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


class OrderValidatorMixin:
    @field_validator("amount", "rate", mode="after")
    @classmethod
    def must_be_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Value must be greater than zero")
        return v

    @field_validator("payment_methods", mode="after", check_fields=False)
    @classmethod
    def check_at_least_one_method(cls, v: list[int] | None) -> list[int] | None:
        # We only validate if the field is actually provided (not None)
        if v is not None and len(v) == 0:
            raise ValueError("At least one method must be provided")
        return v


class OrderBase(ORMBase):
    currency_id: int = Field(..., gt=0, examples=[1])
    action: OrderAction
    amount: Decimal = Field(max_digits=10, decimal_places=2, examples=[100.50])
    rate: Decimal = Field(max_digits=5, decimal_places=2, examples=[41.50])
    description: str | None = Field(None, max_length=200)


class OrderCreate(OrderBase, OrderValidatorMixin):
    payment_methods: list[int] = Field(..., min_length=1)


class OrderUpdate(OrderValidatorMixin, ORMBase):
    # All fields optional for PATCH requests
    amount: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    rate: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    description: str | None = Field(None, max_length=200)
    payment_methods: list[int] | None = Field(None, examples=[[1, 2]])


class OrderRead(OrderBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    owner: UserRead
    currency_obj: CurrencyRead
    payment_methods: list[PaymentMethodRead]
