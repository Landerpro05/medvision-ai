"""
Configuración compartida de tests.

Usa una base de datos SQLite en memoria para no tocar la BD de desarrollo.
Sustituye la dependencia get_db de FastAPI para que cada test trabaje
con su propia sesión aislada y transaccional.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


# Motor SQLite en memoria — completamente aislado de PostgreSQL
SQLALCHEMY_TEST_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
)


def override_get_db():
    """Dependencia de BD para tests — usa SQLite en memoria."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    """
    Crea las tablas antes de cada test y las elimina después.
    Así cada test empieza con una BD limpia.
    """
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    """
    TestClient de FastAPI con la BD de test inyectada.
    No toca la base de datos real de desarrollo.
    """
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
