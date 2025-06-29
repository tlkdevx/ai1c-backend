# app/services/ones_service.py

from typing import Dict
from fastapi import UploadFile

class OnesService:
    async def parse_cf(self, file: UploadFile) -> Dict:
        """
        Заглушка: распарсим .cf/.epf и вернём JSON.
        В будущем здесь вызов v8unpack/cfparser.
        """
        content = await file.read()
        # TODO: реальный разбор
        return {
            "filename": file.filename,
            "size_bytes": len(content),
            "parsed": "stub data"
        }

    async def generate_epf(self, code: str) -> bytes:
        """
        Заглушка: соберёт .epf из BSL-кода.
        В будущем здесь вызов epf_builder.
        """
        # TODO: реальная упаковка
        return code.encode("utf-8")
