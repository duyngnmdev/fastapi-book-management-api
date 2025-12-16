import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseModel):
    PROJECT_NAME: str = "Books Management API"
    SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL")


settings = Settings()
