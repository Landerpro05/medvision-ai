"""
Tests para los endpoints de la API de usuarios.

Usan SQLite en memoria — no modifican ni borran datos de desarrollo.
"""

import uuid


class TestHealth:
    """Tests para GET /api/health."""

    def test_health_devuelve_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_devuelve_mensaje(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert "message" in data
        assert "running" in data["message"].lower()


class TestCrearUsuario:
    """Tests para POST /api/users."""

    def test_registro_correcto(self, client):
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["enabled"] is True
        assert "id" in data

    def test_registro_no_expone_password_hash(self, client):
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
        }
        response = client.post("/api/users", json=payload)
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data
        assert "passwordHash" not in data

    def test_username_duplicado_devuelve_409(self, client):
        payload = {
            "username": "duplicado",
            "email": "email1@example.com",
            "password": "securepass123",
        }
        client.post("/api/users", json=payload)
        payload["email"] = "email2@example.com"
        response = client.post("/api/users", json=payload)
        assert response.status_code == 409

    def test_email_duplicado_devuelve_409(self, client):
        payload = {
            "username": "user1",
            "email": "duplicado@example.com",
            "password": "securepass123",
        }
        client.post("/api/users", json=payload)
        payload["username"] = "user2"
        response = client.post("/api/users", json=payload)
        assert response.status_code == 409

    def test_username_corto_devuelve_422(self, client):
        payload = {
            "username": "ab",
            "email": "test@example.com",
            "password": "securepass123",
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 422

    def test_email_invalido_devuelve_422(self, client):
        payload = {
            "username": "testuser",
            "email": "no-es-un-email",
            "password": "securepass123",
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 422

    def test_password_corta_devuelve_422(self, client):
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short",
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 422

    def test_campos_vacios_devuelve_422(self, client):
        response = client.post("/api/users", json={})
        assert response.status_code == 422

    def test_body_vacio_devuelve_422(self, client):
        response = client.post("/api/users")
        assert response.status_code == 422


from app.auth.jwt import create_access_token
from tests.conftest import TestingSessionLocal
from tests.test_auth import create_test_user

class TestListarUsuarios:
    """Tests para GET /api/users."""

    def test_listar_vacio(self, client):
        db = TestingSessionLocal()
        admin = create_test_user(db, username="admin", email="admin@ex.com", roles=["ADMIN"])
        token = create_access_token(admin.id, ["ADMIN"])
        db.close()
        
        response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        # Will return 1 because the admin user was just created!
        assert len(response.json()) == 1

    def test_listar_con_usuarios(self, client):
        for i in range(3):
            client.post("/api/users", json={
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "securepass123",
            })
        db = TestingSessionLocal()
        admin = create_test_user(db, username="admin", email="admin@ex.com", roles=["ADMIN"])
        token = create_access_token(admin.id, ["ADMIN"])
        db.close()
        
        response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # 3 created via API + 1 admin created via script

    def test_listar_no_expone_password_hash(self, client):
        client.post("/api/users", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
        })
        db = TestingSessionLocal()
        admin = create_test_user(db, username="admin", email="admin@ex.com", roles=["ADMIN"])
        token = create_access_token(admin.id, ["ADMIN"])
        db.close()
        
        response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
        for user in response.json():
            assert "password" not in user
            assert "password_hash" not in user
            assert "passwordHash" not in user


class TestObtenerUsuarioPorId:
    """Tests para GET /api/users/{id}."""

    def test_obtener_usuario_existente(self, client):
        create_resp = client.post("/api/users", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
        })
        user_id = create_resp.json()["id"]
        token = create_access_token(user_id, [])
        response = client.get(f"/api/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser"

    def test_id_inexistente_devuelve_404(self, client):
        fake_id = str(uuid.uuid4())
        db = TestingSessionLocal()
        admin = create_test_user(db, username="admin", email="admin@ex.com", roles=["ADMIN"])
        token = create_access_token(admin.id, ["ADMIN"])
        db.close()
        
        response = client.get(f"/api/users/{fake_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_obtener_usuario_no_expone_password_hash(self, client):
        create_resp = client.post("/api/users", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
        })
        user_id = create_resp.json()["id"]
        token = create_access_token(user_id, [])
        response = client.get(f"/api/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data
        assert "passwordHash" not in data

    def test_id_formato_invalido_devuelve_422(self, client):
        db = TestingSessionLocal()
        admin = create_test_user(db, username="admin", email="admin@ex.com", roles=["ADMIN"])
        token = create_access_token(admin.id, ["ADMIN"])
        db.close()
        
        response = client.get("/api/users/no-es-un-uuid", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422
