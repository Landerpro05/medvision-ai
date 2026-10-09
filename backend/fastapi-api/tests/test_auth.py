"""
Tests para autenticación JWT y dependencias de seguridad.
Usan SQLite en memoria.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.user.models import User, Role
from app.security import hash_password
from app.auth.jwt import create_access_token
from tests.conftest import TestingSessionLocal


def create_test_user(db: Session, username="testuser", email="test@example.com", password="securepass123", roles=None):
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )
    if roles:
        for r_name in roles:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name)
                db.add(role)
                db.commit()
            user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestAuthLogin:
    """Tests para POST /api/auth/login."""

    def test_login_correcto(self, client: TestClient):
        db = TestingSessionLocal()
        create_test_user(db)
        db.close()

        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "securepass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_email_incorrecto(self, client: TestClient):
        response = client.post("/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "securepass123"
        })
        assert response.status_code == 401
        assert "access_token" not in response.json()

    def test_login_password_incorrecto(self, client: TestClient):
        db = TestingSessionLocal()
        create_test_user(db)
        db.close()

        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "access_token" not in response.json()

    def test_swagger_login_correcto(self, client: TestClient):
        db = TestingSessionLocal()
        create_test_user(db)
        db.close()

        response = client.post("/api/auth/swagger_login", data={
            "username": "test@example.com",
            "password": "securepass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_swagger_login_credenciales_incorrectas(self, client: TestClient):
        db = TestingSessionLocal()
        create_test_user(db)
        db.close()

        # Email incorrecto
        response = client.post("/api/auth/swagger_login", data={
            "username": "wrong@example.com",
            "password": "securepass123"
        })
        assert response.status_code == 401

        # Password incorrecto
        response2 = client.post("/api/auth/swagger_login", data={
            "username": "test@example.com",
            "password": "wrongpassword"
        })
        assert response2.status_code == 401




class TestSeguridadYAutorizacion:
    """Tests para acceso a endpoints protegidos."""

    def test_acceder_sin_token(self, client: TestClient):
        response = client.get("/api/users")
        assert response.status_code == 401

    def test_acceder_con_token_invalido(self, client: TestClient):
        response = client.get("/api/users", headers={"Authorization": "Bearer tokenfalso"})
        assert response.status_code == 401

    def test_usuario_consulta_su_propio_perfil(self, client: TestClient):
        db = TestingSessionLocal()
        user = create_test_user(db)
        token = create_access_token(user.id, [])
        db.close()

        response = client.get(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    def test_usuario_consulta_perfil_ajeno_devuelve_403(self, client: TestClient):
        db = TestingSessionLocal()
        user1 = create_test_user(db, username="u1", email="u1@ex.com")
        user2 = create_test_user(db, username="u2", email="u2@ex.com")
        token_u1 = create_access_token(user1.id, [])
        db.close()

        response = client.get(f"/api/users/{user2.id}", headers={"Authorization": f"Bearer {token_u1}"})
        assert response.status_code == 403

    def test_admin_consulta_perfil_ajeno_devuelve_200(self, client: TestClient):
        db = TestingSessionLocal()
        admin = create_test_user(db, username="admin", email="admin@ex.com", roles=["ADMIN"])
        user2 = create_test_user(db, username="u2", email="u2@ex.com")
        token_admin = create_access_token(admin.id, ["ADMIN"])
        db.close()

        response = client.get(f"/api/users/{user2.id}", headers={"Authorization": f"Bearer {token_admin}"})
        assert response.status_code == 200
        assert response.json()["username"] == "u2"

    def test_no_admin_intenta_listar_usuarios_devuelve_403(self, client: TestClient):
        db = TestingSessionLocal()
        user = create_test_user(db)
        token = create_access_token(user.id, [])
        db.close()

        response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    def test_admin_lista_usuarios_devuelve_200(self, client: TestClient):
        db = TestingSessionLocal()
        admin = create_test_user(db, username="admin", email="admin@ex.com", roles=["ADMIN"])
        create_test_user(db, username="u2", email="u2@ex.com")
        token_admin = create_access_token(admin.id, ["ADMIN"])
        db.close()

        response = client.get("/api/users", headers={"Authorization": f"Bearer {token_admin}"})
        assert response.status_code == 200
        assert len(response.json()) == 2
