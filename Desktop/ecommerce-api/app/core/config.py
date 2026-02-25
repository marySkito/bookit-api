from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TITLE: str = "Ecommerce API"
    API_VERSION: str = "2.0.0"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str
    STRIPE_SECRET_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
