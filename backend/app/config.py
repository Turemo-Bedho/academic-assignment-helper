import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://student:secure_password@postgres:5432/academic_helper")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/assignment")
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

settings = Settings()