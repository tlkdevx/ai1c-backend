from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as doc_router
from app.api.llm import router as llm_router
from app.api.upload_cf import router as upload_cf_router
from app.api.history import router as history_router
from app.api.agent import router as agent_router
from app.api.search import router as search_router
from app.api.cf import router as cf_router  # <-- Новый cf-роутер

app = FastAPI(title="AI1C Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшена заменить на [settings.frontend_url]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Не дублируй prefix, если он уже есть в самом роутере!
app.include_router(auth_router)
app.include_router(doc_router)
app.include_router(llm_router)
app.include_router(upload_cf_router)
app.include_router(history_router)
app.include_router(agent_router)
app.include_router(search_router)
app.include_router(cf_router)  # <-- Добавили cf-роутер
