from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from src.config import settings

engine = create_engine(settings.DATABASE_URL_psycopg)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base = declarative_base(metadata=meta)


class Database_Helper:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.meta = meta
        self.Base = Base

    def get_db(self) -> Generator[Session, None, None]:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


db_helper = Database_Helper()
