# app/api/auth.py

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.core.config import settings
from app.db.session import get_db
from app.db.models.user import User as UserModel

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Pydantic-модели
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

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

class TokenRequest(BaseModel):
    email: EmailStr
    password: str

# Регистрация
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user.password)
    new_user = UserModel(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Получение токена по JSON
@router.post("/token", response_model=Token)
def login_for_access_token(
    creds: TokenRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.email == creds.email).first()
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=60)
    )
    return Token(access_token=access_token)

# Функция зависимости для получения текущего пользователя
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    try:
        user_id = decode_access_token(token)
        user = db.get(UserModel, int(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# Текущий пользователь
@router.get("/me", response_model=UserOut)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
