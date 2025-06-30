# app/api/search.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.embedding import Embedding
from app.db.models.knowledge import Knowledge
from app.db.models.document import Document

import numpy as np
from sentence_transformers import SentenceTransformer

router = APIRouter(prefix="/api/v1/search", tags=["search"])

# ---- Для локального embedding ----
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    document_id: int
    chunk_index: int
    similarity: float
    text: str

@router.post("/", response_model=List[SearchResult])
async def semantic_search(
    req: SearchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query_vec = model.encode([req.query])[0]

    # Эмбеддинги только пользователя
    docs = db.query(Document).filter(Document.owner_id == current_user.id).all()
    doc_ids = [d.id for d in docs]
    embs = db.query(Embedding).filter(Embedding.document_id.in_(doc_ids)).all()

    scored = []
    for e in embs:
        emb_vec = np.array(e.vector)
        sim = float(np.dot(query_vec, emb_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(emb_vec) + 1e-8))
        # knowledge_id = e.id  # вариант если chunk_index совпадает с id
        knowledge = db.query(Knowledge).filter(
            Knowledge.document_id == e.document_id,
            Knowledge.chunk_index == e.id  # если chunk_index == id эмбеддинга, иначе подбери верно!
        ).first()
        scored.append({
            "document_id": e.document_id,
            "chunk_index": e.id,
            "similarity": sim,
            "text": knowledge.text if knowledge else ""
        })

    # Топ-5 по схожести
    top = sorted(scored, key=lambda x: x["similarity"], reverse=True)[:5]
    return top
