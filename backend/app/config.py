import json
import os


class Config:
    APP_NAME = os.getenv("APP_NAME", "ParkSmart API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+pg8000://parksmart:parksmart@localhost:5432/parksmart",
    )
    CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME", "")
    DB_USER = os.getenv("DB_USER", "parksmart")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "parksmart")
    DB_NAME = os.getenv("DB_NAME", "parksmart")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    CORS_ORIGINS = json.loads(
        os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:5173"]')
    )

    @classmethod
    def use_cloud_sql_connector(cls) -> bool:
        return bool(cls.CLOUD_SQL_CONNECTION_NAME)
