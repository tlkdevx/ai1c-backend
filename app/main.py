from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, llm  # импорт без get_current_user!

app = FastAPI(title="AI1C API")

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.frontend_url)],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth")
app.include_router(llm.router)  # <= БЕЗ dependencies!
