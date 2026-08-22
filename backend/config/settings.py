from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CETRI AI OS"
    jwt_secret: str = "supersecretkey_change_me_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    # AI provider configuration
    ai_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
