from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings
import os

from typing import ClassVar

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    SECRET_KEY:str = os.getenv('SECRET_KEY')
    ALGORITHM:str = os.getenv('ALGORITHM')



def get_settings() -> Settings:
    return Settings()