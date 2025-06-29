# app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

from app.api.auth       import router as auth_router, get_current_user
from app.api.llm        import router as llm_router
from app.api.users      import router as users_router
from app.api.ones       import router as ones_router
from app.api.rag        import router as rag_router
from app.api.documents  import router as documents_router
from app.api.qa         import router as qa_router

app = FastAPI(title="AI1C Backend")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
# все последующие роуты требуют авторизации
app.include_router(llm_router,       dependencies=[Depends(get_current_user)])
app.include_router(users_router,     dependencies=[Depends(get_current_user)])
app.include_router(ones_router,      dependencies=[Depends(get_current_user)])
app.include_router(rag_router,       dependencies=[Depends(get_current_user)])
app.include_router(documents_router, dependencies=[Depends(get_current_user)])
app.include_router(qa_router,        dependencies=[Depends(get_current_user)])
