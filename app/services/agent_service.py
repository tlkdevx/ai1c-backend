# app/services/agent_service.py

from app.services.llm_service import DeepSeekLLM

class AgentService:
    @staticmethod
    async def solve_task(prompt: str, documents: list, user_id: int, history: list = None) -> str:
        # 1. Анализируем prompt и документы (TODO: парсинг cf/epf, выделение ошибок)
        # 2. Ищем похожие задачи в истории (TODO: добавить RAG, эмбеддинги)
        # 3. Формируем расширенный prompt для LLM на основе истории и документов
        # 4. Вызываем DeepSeek для генерации ответа (в будущем можно подменить любой LLM)
        # 5. Возвращаем и сохраняем результат

        # Пока что минимальный MVP — только передаём prompt
        answer = await DeepSeekLLM.generate(prompt)
        return answer
