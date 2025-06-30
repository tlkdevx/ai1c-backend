from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode = {"exp": expire, "sub": subject}
    key = settings.jwt_secret  # Теперь это str, а не SecretStr!
    return jwt.encode(to_encode, key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> dict:
    key = settings.jwt_secret  # Теперь это str, а не SecretStr!
    try:
        return jwt.decode(token, key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise e
