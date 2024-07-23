import enum
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Enum, Column, Relationship

class OrderStatus(str):
    open = "open"
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    completed = "completed"
    cancelled = "cancelled"

class OrderBase(SQLModel):
    total_amount: float = Field(gt=0.0)
    status: str = Field(default="open")
                                

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(gt=0)
    invoice_id: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=datetime.now(tz=None))
    updated_at: Optional[datetime] = Field(default=datetime.now(tz=None))

    # order_items: Optional[list["OrderItems"]] = Field(default=[], sa_column_kwargs={"onupdate": "CASCADE", "ondelete": "CASCADE"})
    order_items: Optional[list["OrderItem"]] = Relationship(back_populates="order")

class OrderRead(SQLModel):
    id: Optional[int]
    user_id: Optional[int]
    total_amount: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    status: str
    order_items: Optional[list["OrderItem"]]

class OrderUpdateSatus(SQLModel):
    status: str

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", nullable=False)
    product_id: int = Field(gt=0,nullable=False)
    qty: int = Field(gt=0, nullable=False)
    unit_price: float = Field(gt=0.0, nullable=False)
    total_price: float = Field(gt=0.0, nullable=False)
    created_at: Optional[datetime] = Field(default=datetime.now(tz=None))
    updated_at: Optional[datetime] = Field(default=datetime.now(tz=None))

    order: Optional[Order] = Relationship(back_populates="order_items")