import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    # Model configuration
    MODEL_DIR = "models"
    MODEL_FILE_PREFIX = "prophet_model"
    
    # API configuration
    API_TITLE = "Park Visitor Forecast API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Predicts daily visitor volume for US National Parks"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

config = Config() 