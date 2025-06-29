# app/api/documents.py

from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.document import Document as DocumentModel
from app.db.models.embedding import Embedding as EmbeddingModel
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

class EmbeddingOut(BaseModel):
    id: int
    vector: List[float]
    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    name: str
    uploaded_at: datetime
    embeddings: List[EmbeddingOut] = []
    class Config:
        from_attributes = True

@router.post("/", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    content = await file.read()
    doc = DocumentModel(
        name=file.filename,
        content=content,
        owner_id=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Собираем URL без лишних слэшей
    embed_url = f"{settings.DEEPSEEK_API_BASE_URL}/v1/embed_file"
    try:
        resp = httpx.post(
            embed_url,
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY.get_secret_value()}"},
            files={"file": (file.filename, content, file.content_type)},
            timeout=30.0
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        db.delete(doc)
        db.commit()
        raise HTTPException(500, detail=f"Embedding error: {exc}")

    data = resp.json()
    vector = data.get("embedding") or data.get("vector") or []
    if not isinstance(vector, list):
        raise HTTPException(500, detail="Embedding error: unexpected format")

    emb = EmbeddingModel(document_id=doc.id, vector=vector)
    db.add(emb)
    db.commit()
    db.refresh(emb)

    doc.embeddings = [emb]
    return doc
