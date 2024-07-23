from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True, gt=0)
    name: str = Field(index=True)
    price: float = Field(gt=0)
    user_id: Optional[int] = Field(default=None)
    created_at: Optional[datetime] = Field(default=datetime.now(tz=None))
    updated_at: Optional[datetime] = Field(default=datetime.now(tz=None))
