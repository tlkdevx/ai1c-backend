from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # <-- Исправлено тут!
    prompt = Column(Text, nullable=False)
    code = Column(Text)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Временно отключи, если нет модели User с tasks
    # user = relationship("User", back_populates="tasks")
