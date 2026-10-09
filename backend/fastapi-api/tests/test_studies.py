import pytest
import uuid
from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token
from app.study.models import Study
from tests.conftest import TestingSessionLocal
from tests.test_auth import create_test_user

class TestStudies:

    def test_crear_estudio(self, client: TestClient):
        db = TestingSessionLocal()
        user = create_test_user(db, username="patient1", email="p1@ex.com")
        token = create_access_token(user.id, [])
        db.close()

        response = client.post("/api/studies", headers={"Authorization": f"Bearer {token}"}, json={
            "modality": "XRAY",
            "study_date": "2026-10-10T10:00:00"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "PENDING"
        assert data["modality"] == "XRAY"
        assert "id" in data

    def test_listar_estudios_aislados_por_usuario(self, client: TestClient):
        db = TestingSessionLocal()
        u1 = create_test_user(db, username="u1", email="u1@ex.com")
        u2 = create_test_user(db, username="u2", email="u2@ex.com")
        
        # Insertar estudios manualmente
        s1 = Study(user_id=u1.id, modality="CT")
        s2 = Study(user_id=u2.id, modality="MRI")
        db.add_all([s1, s2])
        db.commit()
        
        token1 = create_access_token(u1.id, [])
        db.close()

        response = client.get("/api/studies", headers={"Authorization": f"Bearer {token1}"})
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        assert data[0]["modality"] == "CT"

    def test_consultar_estudio_propio(self, client: TestClient):
        db = TestingSessionLocal()
        u1 = create_test_user(db, username="u1", email="u1@ex.com")
        s1 = Study(user_id=u1.id, modality="MRI")
        db.add(s1)
        db.commit()
        db.refresh(s1)
        
        token = create_access_token(u1.id, [])
        db.close()

        response = client.get(f"/api/studies/{s1.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["modality"] == "MRI"

    def test_consultar_estudio_ajeno_devuelve_404(self, client: TestClient):
        db = TestingSessionLocal()
        u1 = create_test_user(db, username="u1", email="u1@ex.com")
        u2 = create_test_user(db, username="u2", email="u2@ex.com")
        s1 = Study(user_id=u1.id)
        db.add(s1)
        db.commit()
        db.refresh(s1)
        
        token2 = create_access_token(u2.id, [])
        db.close()

        response = client.get(f"/api/studies/{s1.id}", headers={"Authorization": f"Bearer {token2}"})
        assert response.status_code == 404

    def test_consultar_estudio_inexistente_devuelve_404(self, client: TestClient):
        db = TestingSessionLocal()
        u1 = create_test_user(db, username="u1", email="u1@ex.com")
        token = create_access_token(u1.id, [])
        db.close()

        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/studies/{fake_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
