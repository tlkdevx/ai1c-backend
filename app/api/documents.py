from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.document import Document as DocumentModel

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
    current_user=Depends(get_current_user),
):
    raw_bytes = await file.read()
    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, detail="Файл должен быть в кодировке UTF-8")

    doc = DocumentModel(
        name=file.filename,
        content=raw_bytes,
        owner_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc
