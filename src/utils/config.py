import os

from dotenv import load_dotenv


load_dotenv()

class Config:
    API_KEY = os.getenv("API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME")
    RETREIVER_NAME = os.getenv("retreiver_NAME")
    VECTOR_PATH = os.getenv("VECTOR_PATH")
    DATA_PATH = os.getenv("DATA_PATH")
    DEVICE = os.getenv('DEVICE')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///yara.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RAG_API_URL = os.environ.get('RAG_API_URL') or 'http://localhost:8000/query'
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

if __name__ == "__main__":
    print(Config.API_KEY)
    print(Config.DATA_PATH)
    print(Config.RETREIVER_NAME)
    print(Config.DEVICE)