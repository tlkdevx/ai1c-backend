# app/api/search.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.embedding import Embedding
from app.db.models.knowledge import Knowledge
from app.db.models.document import Document

import httpx
import numpy as np
from typing import List

router = APIRouter(prefix="/api/v1/search", tags=["search"])

@router.post("/")
async def semantic_search(
    query: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1. Получаем embedding для запроса
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{settings.deepseek_api_base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.deepseek_embedding_model,
                "input": query,
            }
        )
        response.raise_for_status()
        query_vec = np.array(response.json()["data"][0]["embedding"])

    # 2. Получаем все эмбеддинги пользователя
    docs = db.query(Document).filter(Document.owner_id == current_user.id).all()
    doc_ids = [d.id for d in docs]
    embs = db.query(Embedding).filter(Embedding.document_id.in_(doc_ids)).all()

    # 3. Считаем косинусное сходство
    scored = []
    for e in embs:
        emb_vec = np.array(e.vector)
        # Косинусная мера (чем ближе к 1 — тем лучше)
        sim = float(np.dot(query_vec, emb_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(emb_vec) + 1e-8))
        scored.append((sim, e))

    # 4. Возвращаем топ-5 чанков
    top = sorted(scored, key=lambda x: x[0], reverse=True)[:5]
    result = []
    for sim, emb in top:
        knowledge = db.query(Knowledge).filter(Knowledge.document_id == emb.document_id, Knowledge.chunk_index == emb.id).first()
        result.append({
            "document_id": emb.document_id,
            "chunk_index": emb.id,
            "similarity": sim,
            "text": knowledge.text if knowledge else ""
        })
    return {"results": result}
