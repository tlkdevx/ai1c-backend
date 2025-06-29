# app/api/qa.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from openai import OpenAI

from app.api.embed_utils import search_index
from app.core.config import settings

router = APIRouter(prefix="/api/v1/qa", tags=["qa"])

class QARequest(BaseModel):
    query: str
    k: int = 5

class QAResponse(BaseModel):
    answer: str
    sources: List[int]

@router.post("/", response_model=QAResponse)
async def qa(req: QARequest):
    # 1) Находим самые близкие фрагменты
    distances, indices = search_index(req.query, k=req.k)
    # 2) Формируем системный prompt с текстом фрагментов
    snippets = [f"Fragment {i}" for i in indices]  # тут можно заменить на реальные тексты
    system_prompt = (
        "You are a 1C expert. Use the following snippets:\n" +
        "\n---\n".join(snippets)
    )
    # 3) Запускаем DeepSeek Chat
    client = OpenAI(
        api_key=settings.deepseek_api_key.get_secret_value(),
        base_url=str(settings.deepseek_api_base_url)
    )
    try:
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.query},
            ],
            temperature=0.1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {e}")

    return QAResponse(
        answer=resp.choices[0].message.content,
        sources=indices.tolist()
    )
