from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.user import User as UserModel
from app.db.models.document import Document as DocumentModel
from datetime import datetime

from openai import OpenAI

router = APIRouter(prefix="/api/v1/generate-code", tags=["generate-code"])

class GenerateCodeRequest(BaseModel):
    prompt: str
    model: str = settings.llm_model

class GenerateCodeResponse(BaseModel):
    code: str
    explanation: str
    task_id: int

@router.post("/", response_model=GenerateCodeResponse)
async def generate_code(
    req: GenerateCodeRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        client = OpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=str(settings.deepseek_api_base_url) + "/v1"
        )
        messages = [
            {"role": "system", "content": "Ты пишешь на языке 1С:BSL. На входе ТЗ, на выходе — код и пояснения."},
            {"role": "user", "content": req.prompt}
        ]
        resp = client.chat.completions.create(
            model=req.model,
            messages=messages,
            temperature=0.7
        )
        answer = resp.choices[0].message.content
        code_part = ""
        explanation_part = ""
        if "Пояснение:" in answer:
            code_part, explanation_part = answer.split("Пояснение:", 1)
        else:
            code_part = answer
            explanation_part = "Пояснений не было."

        doc = DocumentModel(
            name=f"CodeGen_{datetime.now().isoformat()}",
            content=code_part.encode("utf-8"),
            owner_id=user.id
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        return GenerateCodeResponse(
            code=code_part.strip(),
            explanation=explanation_part.strip(),
            task_id=doc.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek error: {e}")
