# app/db/models/knowledge.py

from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Порядковый номер чанка в документе
    text = Column(Text, nullable=False)            # Содержимое чанка

    document = relationship("Document", back_populates="knowledges")
