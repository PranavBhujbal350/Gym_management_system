import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-key-change-me")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/gym_management")
    DB_NAME = os.getenv("DB_NAME", "gym_management")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    PORT = int(os.getenv("PORT", 5000))
