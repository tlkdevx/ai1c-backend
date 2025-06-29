# Вставьте в app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserInDB(UserRead):
    hashed_password: str
