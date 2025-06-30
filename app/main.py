from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as doc_router
from app.api.llm import router as llm_router

app = FastAPI(title="AI1C Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(doc_router)   # contains prefix="/api/v1/documents"
app.include_router(llm_router)   # contains prefix="/api/v1/llm"
