import os
import boto3
import structlog
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()


# Logger configuration
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()]
    )
logger = structlog.get_logger()


class Settings(BaseSettings):
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT")
    MYSQL_DB: str = os.getenv("MYSQL_DB")
    DB_URL: str = os.getenv('DATABASE_URL')

    S3_BUCKET: str = os.getenv("S3_BUCKET", "documents")
    AWS_ACCESS_KEY_ID: str =os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str =os.getenv("AWS_SECRET_ACCESS_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")


    # S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")  # For Minio
    
    



@lru_cache() # Caches settings for performance, avoids loading .env repeatedly
def get_settings():
    return Settings()
