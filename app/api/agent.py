# app/api/agent.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx

from app.db.session import get_db
from app.api.auth import get_current_user
from app.db.models.document import Document as DocumentModel
from app.db.models.embedding import Embedding as EmbeddingModel
from app.core.config import settings

import numpy as np

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

class AgentAskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4

class AgentAskResponse(BaseModel):
    answer: str
    sources: List[dict]

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

async def get_question_embedding(question: str) -> List[float]:
    # Векторизация запроса через DeepSeek API (или локально если есть модель)
    url = "https://api.deepseek.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": question,
        "model": "deepseek-embedding"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        return data["data"][0]["embedding"]

@router.post("/ask", response_model=AgentAskResponse)
async def agent_ask(
    req: AgentAskRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1. Получаем эмбеддинг вопроса
    question_emb = await get_question_embedding(req.question)

    # 2. Ищем топ-k наиболее похожих эмбеддингов из базы
    all_embeddings = db.query(EmbeddingModel).all()
    similarities = []
    for emb in all_embeddings:
        sim = cosine_similarity(question_emb, emb.vector)
        similarities.append((sim, emb))
    similarities = sorted(similarities, key=lambda x: -x[0])
    top_embeddings = similarities[:req.top_k]

    # 3. Собираем контекст для ответа
    context_chunks = []
    sources = []
    for sim, emb in top_embeddings:
        doc = db.query(DocumentModel).filter(DocumentModel.id == emb.document_id).first()
        chunk = {
            "content": emb.chunk_text,
            "similarity": sim,
            "doc_name": doc.name if doc else "unknown"
        }
        context_chunks.append(emb.chunk_text)
        sources.append(chunk)
    context_str = "\n\n".join(context_chunks)

    # 4. Формируем prompt для DeepSeek
    prompt = (
        f"Вопрос пользователя:\n{req.question}\n\n"
        f"Релевантные фрагменты из документов:\n{context_str}\n\n"
        f"Ответь на вопрос максимально подробно, используя только эти фрагменты. Если ответа нет — так и скажи."
    )

    # 5. Запрос к DeepSeek LLM
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты помощник по документации 1С. Отвечай по фактам."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1024
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        answer = data["choices"][0]["message"]["content"]

    return AgentAskResponse(answer=answer, sources=sources)
