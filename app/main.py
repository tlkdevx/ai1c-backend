from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as doc_router
from app.api.llm import router as llm_router
from app.api.upload_cf import router as upload_cf_router
from app.api.history import router as history_router

app = FastAPI(title="AI1C Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшена заменить на [settings.frontend_url]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(doc_router)
app.include_router(llm_router)
app.include_router(upload_cf_router)
app.include_router(history_router)
