# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    database_url: str

    # DeepSeek API
    deepseek_api_key: str
    deepseek_api_base_url: str = "https://api.deepseek.com"
    deepseek_embedding_model: str = "deepseek-embedding"
    llm_model: str = "deepseek-chat"

    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
