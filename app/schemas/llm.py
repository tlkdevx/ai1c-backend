# app/schemas/llm.py
from pydantic import BaseModel, Field
from typing import Literal

class LLMRequest(BaseModel):
    prompt: str
    model: str
    provider: Literal["openai", "deepseek"]
    temperature: float = Field(1.0, ge=0, le=2)

class LLMResponse(BaseModel):
    text: str
