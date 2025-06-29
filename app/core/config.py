from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, SecretStr, PostgresDsn


class Settings(BaseSettings):
    secret_key: SecretStr
    database_url: PostgresDsn
    openai_api_key: SecretStr
    deepseek_api_key: SecretStr
    deepseek_api_base_url: AnyHttpUrl
    deepseek_embedding_model: str
    llm_model: str
    jwt_secret: SecretStr
    jwt_algorithm: str
    frontend_url: AnyHttpUrl

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
