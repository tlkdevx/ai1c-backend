# app/db/models/embedding.py

from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Embedding(Base):
    __tablename__ = "embeddings"

    id          = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    vector      = Column(JSON, nullable=False)

    document    = relationship(
        "Document",
        back_populates="embeddings"
    )
