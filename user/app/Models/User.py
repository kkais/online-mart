from typing import Optional
from sqlmodel import Field, SQLModel

class UserBase(SQLModel):
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    api_key: str = Field(max_length=1024)
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: Optional[str] = Field(max_length=1024)

# class UserCreate(User):
#     pass

class UserUpdate(User):
    pass

class UserRead(SQLModel):
    id: int
    first_name: str
    last_name: str
    email: str
    is_active: bool
    api_key: str


class UserLogin(SQLModel):
    email: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    iss: str