# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    subject: str, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = {"sub": subject}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    # используем .get_secret_value() для SecretStr
    key = settings.jwt_secret.get_secret_value()
    return jwt.encode(to_encode, key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> str:
    key = settings.jwt_secret.get_secret_value()
    payload = jwt.decode(token, key, algorithms=[settings.jwt_algorithm])
    return payload.get("sub")
