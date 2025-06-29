from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings

router = APIRouter(prefix="/api/v1/llm")

class LLMRequest(BaseModel):
    prompt: str
    model: str = settings.llm_model
    temperature: float = 0.7

class LLMResponse(BaseModel):
    response: str

@router.post("/generate", response_model=LLMResponse)
async def generate_llm(req: LLMRequest):
    try:
        client = OpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=str(settings.deepseek_api_base_url)
        )
        resp = client.chat.completions.create(
            model=req.model,
            messages=[{"role": "user", "content": req.prompt}],
            temperature=req.temperature
        )
        return {"response": resp.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek error: {e}")
