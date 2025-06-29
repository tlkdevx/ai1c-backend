# app/api/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User as DBUser  # теперь правильный путь

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(DBUser).filter(DBUser.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    from app.core.security import get_password_hash
    hashed = get_password_hash(user.password)
    db_user = DBUser(email=user.email, full_name=user.full_name, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.get(DBUser, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
