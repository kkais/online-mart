from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class CartBase(SQLModel):
    product_id: int = Field(gt=0, default=None)
    qty: int = Field(gt=0, nullable=False)

class Cart(CartBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(gt=0, default=None)
    unit_price: Optional[float] = Field(gt=0.0, default=None)
    created_at: Optional[datetime] = Field(default=datetime.now(tz=None))
    updated_at: Optional[datetime] = Field(default=datetime.now(tz=None))

class CartUpdate(SQLModel):
    qty: Optional[int]

class CartRead(SQLModel):
    id: Optional[int]
    product_id: int
    qty: int
    user_id: Optional[int]
    unit_price: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]