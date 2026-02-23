from enum import Enum as PyEnum


class gitOrderAction(str, PyEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(PyEnum):
    ACTIVE = "ACTIVE"  ## listed for all
    COMPLETED = "COMPLETED"  ## hidden
    CANCELLED = "CANCELLED"  ## listed in account details
    PENDING = "PENDING"  ## listed in account details
    EXPIRED = "EXPIRED"  ## listed in account


class DealStatus(PyEnum):
    PENDING = "PENDING"  ## listed in pending orders
    PAID = "PAID"  ## maybe list?
    CANCELLED = "CANCELLED"  ## maybe list?
