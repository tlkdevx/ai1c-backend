# app/api/rag.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.rag_service import RAGService

router = APIRouter()

class RAGRequest(BaseModel):
    query: str = Field(..., example="Как распарсить cf-файл?")
    k: int = Field(5, ge=1, le=20, description="Количество примеров для возвращения")

@router.post("/api/rag")
async def rag_search(request: RAGRequest):
    try:
        service = RAGService()
        results = await service.search(request.query, request.k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
