from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import Config

engine = None
SessionLocal = None


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    global engine, SessionLocal

    if Config.use_cloud_sql_connector():
        from google.cloud.sql.connector import Connector

        connector = Connector()

        def getconn():
            return connector.connect(
                Config.CLOUD_SQL_CONNECTION_NAME,
                "pg8000",
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                db=Config.DB_NAME,
            )

        engine = create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=2,
        )
    else:
        engine = create_engine(
            Config.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=2,
        )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    if SessionLocal is None:
        init_db()
    return SessionLocal()
