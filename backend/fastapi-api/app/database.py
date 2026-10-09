from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    Declarative base for all SQLAlchemy models.
    Replaces JPA entity scanning from Spring Boot.
    """
    pass


def get_db():
    """
    FastAPI dependency that yields a DB session per request.
    Replaces Spring's automatic transaction management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
