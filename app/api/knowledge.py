# app/api/knowledge.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.knowledge import Knowledge

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])

class KnowledgeChunkOut(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    text: str

    class Config:
        from_attributes = True

@router.get("/search", response_model=List[KnowledgeChunkOut])
def search_knowledge(
    query: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Full-text поиск по тексту чанков (простая версия)
    results = (
        db.query(Knowledge)
        .filter(Knowledge.text.ilike(f"%{query}%"))
        .limit(10)
        .all()
    )
    if not results:
        raise HTTPException(status_code=404, detail="Ничего не найдено.")
    return results
