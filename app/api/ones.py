# app/api/ones.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Any, Dict
from app.services.ones_service import OnesService

router = APIRouter()

class EPFRequest(BaseModel):
    code: str

@router.post("/api/ones/parse-cf")
async def parse_cf(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        service = OnesService()
        result = await service.parse_cf(file)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ones/generate-epf")
async def generate_epf(request: EPFRequest):
    try:
        service = OnesService()
        epf_bytes = await service.generate_epf(request.code)
        return {
            "filename": "generated.epf",
            "content_base64": epf_bytes.decode("utf-8")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
