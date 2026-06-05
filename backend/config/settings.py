from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "CETRI AI OS"
    jwt_secret: str = "supersecretkey_change_me_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7 # 1 week
    
    # AI API Keys (leave empty in default, load from .env)
    openai_api_key: str = ""
    gemini_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
