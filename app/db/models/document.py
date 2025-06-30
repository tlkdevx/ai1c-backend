# app/db/models/document.py

from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    content     = Column(LargeBinary, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner       = relationship("User", back_populates="documents")

    embeddings  = relationship(
        "Embedding",
        back_populates="document",
        cascade="all, delete-orphan"
    )

    knowledges  = relationship(
        "Knowledge",
        back_populates="document",
        cascade="all, delete-orphan"
    )
