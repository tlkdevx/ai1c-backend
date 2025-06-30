from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.db.session import get_db
from app.db.models.feedback import Feedback
from app.db.models.task import Task
from app.db.models.user import User
from typing import Optional
import datetime

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])

class FeedbackIn(BaseModel):
    task_id: int = Field(..., description="ID задания/кейса")
    rating: float = Field(..., ge=1, le=5, description="Оценка (1-5)")
    comment: Optional[str] = None
    user_id: Optional[int] = None  # если нет авторизации

@router.post("/", status_code=status.HTTP_201_CREATED)
def log_feedback(feedback: FeedbackIn, db: Session = Depends(get_db)):
    # Проверяем, есть ли такой task
    task = db.query(Task).filter(Task.id == feedback.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    fb = Feedback(
        task_id=feedback.task_id,
        rating=feedback.rating,
        comment=feedback.comment,
        user_id=feedback.user_id,
        created_at=datetime.datetime.utcnow()
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"status": "ok", "feedback_id": str(fb.id)}
