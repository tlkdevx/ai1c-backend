from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.history import History
from openai import OpenAI

router = APIRouter(prefix="/api/v1/generate-code", tags=["generate-code"])

class CodeRequest(BaseModel):
    prompt: str

class CodeResponse(BaseModel):
    code: str

@router.post("/", response_model=CodeResponse)
def generate_code(
    req: CodeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        client = OpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=str(settings.deepseek_api_base_url)
        )
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": req.prompt}],
            temperature=0.7
        )
        code = resp.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek error: {e}")

    # Сохраняем историю
    h = History(
        user_id=current_user.id,
        prompt=req.prompt,
        code=code
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return {"code": code}
