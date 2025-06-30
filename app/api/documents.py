# app/api/documents.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from pydantic import BaseModel  # <-- ВАЖНО! Добавлен импорт

from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.document import Document
from app.db.models.knowledge import Knowledge
from app.db.models.embedding import Embedding

import httpx

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

class DocumentOut(BaseModel):
    id: int
    name: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    content = await file.read()
    doc = Document(
        name=file.filename,
        content=content,
        owner_id=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # --- Чанкуем текст (просто на абзацы/строки, для теста) ---
    try:
        text = content.decode('utf-8', errors='ignore')
    except Exception:
        text = ""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Не удалось прочитать текст документа.")

    # Простейший split, дальше усложним
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    if not chunks:
        chunks = [text]  # fallback

    for idx, chunk in enumerate(chunks):
        # 1. Сохраняем chunk в Knowledge
        k = Knowledge(
            document_id=doc.id,
            chunk_index=idx,
            text=chunk
        )
        db.add(k)
        db.commit()
        db.refresh(k)

        # 2. Вызываем DeepSeek для эмбеддинга
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{settings.deepseek_api_base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {settings.deepseek_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.deepseek_embedding_model,
                        "input": chunk,
                    }
                )
                response.raise_for_status()
                result = response.json()
            embedding_vector = result["data"][0]["embedding"]
            emb = Embedding(
                document_id=doc.id,
                vector=embedding_vector
            )
            db.add(emb)
            db.commit()
        except Exception as e:
            print(f"Ошибка при генерации embedding: {e}")

    return doc
