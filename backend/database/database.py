from sqlalchemy import create_engine

from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)

from backend.core.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()