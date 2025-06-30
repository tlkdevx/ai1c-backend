# app/api/llm.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
import httpx

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

class LLMRequest(BaseModel):
    prompt: str

class LLMResponse(BaseModel):
    result: str

@router.post("/generate", response_model=LLMResponse)
async def llm_generate(
    req: LLMRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    api_url = f"{settings.deepseek_api_base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": "Ты эксперт 1С. Отвечай максимально по делу."},
            {"role": "user", "content": req.prompt}
        ],
        "temperature": 0.3,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    result = data["choices"][0]["message"]["content"].strip()
    return LLMResponse(result=result)
