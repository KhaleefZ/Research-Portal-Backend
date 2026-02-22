import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Research Portal - Finance Extractor"
    # Required for the Research Tool logic 
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Deployment settings [cite: 51]
    ALLOWED_HOSTS: list = ["*"] 
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB limit [cite: 56]

settings = Settings()