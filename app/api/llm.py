from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from app.core.config import settings
from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models.user import User
import httpx
import logging

router = APIRouter()

class GenerateCodeRequest(BaseModel):
    prompt: str

class GenerateCodeResponse(BaseModel):
    code: str
    explanation: str = ""

@router.post("/api/v1/generate-code/", response_model=GenerateCodeResponse)
async def generate_code(
    data: GenerateCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    try:
        api_url = f"{settings.deepseek_api_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": "You are an expert 1C:Enterprise developer. Generate BSL/epf code for the task."},
                {"role": "user", "content": data.prompt},
            ],
            "temperature": 0.7,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()

        code_text = ""
        explanation = ""
        if "choices" in result and len(result["choices"]) > 0:
            code_text = result["choices"][0].get("message", {}).get("content", "")
            explanation = "Генерация выполнена через DeepSeek."

        try:
            db.execute(
                text("INSERT INTO task_history (user_id, prompt, code, created_at) VALUES (:user_id, :prompt, :code, NOW())"),
                {"user_id": current_user.id, "prompt": data.prompt, "code": code_text}
            )
            db.commit()
        except Exception as db_err:
            logging.error(f"Ошибка при записи истории: {db_err}")

        return GenerateCodeResponse(code=code_text, explanation=explanation)

    except httpx.HTTPStatusError as e:
        logging.error(f"DeepSeek HTTP error: {e.response.status_code} {e.response.text}")
        raise HTTPException(status_code=500, detail=f"DeepSeek error: {e.response.text}")
    except Exception as e:
        logging.error(f"Ошибка генерации кода: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
