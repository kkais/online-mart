from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class InventoryBase(SQLModel):
    product_id: int = Field(gt=0)
    qty: int = Field()
    unit_cost: float = Field(gt=0.0)

class Inventory(InventoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sales_order_id: Optional[int] = Field(default=None)
    purchases_order_id: Optional[int] = Field(default=None)
    returns: Optional[bool] = Field(default=False)
    description: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=datetime.now(tz=None))
    updated_at: Optional[datetime] = Field(default=datetime.now(tz=None))

class InventoryRead(SQLModel):
    id: Optional[int]
    product_id: int
    qty: int
    unit_cost: float
    sales_order_id: Optional[int]
    purchases_order_id: Optional[int]
    returns: Optional[bool]
    description: Optional[str]

class InventoryBalance(SQLModel):
    product_id: int
    total_qty: int