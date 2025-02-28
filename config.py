import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE = os.getenv("DATABASE", "cv_parser")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

config = Config() 