from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

engine = create_engine(settings.database_url.unicode_string())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
