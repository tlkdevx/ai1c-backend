# app/services/rag_service.py

class RAGService:
    def __init__(self):
        # TODO: инициализация векторного хранилища (pgvector / FAISS / Chroma)
        pass

    async def search(self, query: str, k: int = 5) -> list[str]:
        # Временный заглушечный код — вернём фиктивные примеры
        return [f"Example {i} for query '{query}'" for i in range(1, k + 1)]
