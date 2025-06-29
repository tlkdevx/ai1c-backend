import os
import httpx
from typing import Literal

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

class LLMRouter:
    def __init__(self, model: Literal["gpt-4", "gpt-3.5", "deepseek-coder", "deepseek-chat"]):
        self.model = model

    async def call(self, prompt: str) -> str:
        if self.model in ["gpt-4", "gpt-3.5"]:
            return await self._call_openai(prompt)
        elif self.model in ["deepseek-coder", "deepseek-chat"]:
            return await self._call_deepseek(prompt)
        else:
            raise ValueError(f"Unknown model: {self.model}")

    async def _call_openai(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model if self.model != "gpt-3.5" else "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def _call_deepseek(self, prompt: str) -> str:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
