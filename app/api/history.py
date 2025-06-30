# app/api/history.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.api.auth import get_current_user
from app.db.models.user import User
from app.db.models.document import Document

router = APIRouter(prefix="/api/v1/history", tags=["history"])

class HistoryRecord(BaseModel):
    id: int
    name: str
    uploaded_at: datetime  # <--- БЫЛО str, стало datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[HistoryRecord])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = (
        db.query(Document)
        .filter(Document.owner_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return docs
