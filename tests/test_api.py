import os
import pytest
from fastapi.testclient import TestClient
import api as api_module
import core

@pytest.fixture(autouse=True)
def setup_teardown_db():
    """Use a separate database for tests."""
    original_db_path = core.DB_PATH
    test_db = "test_frictionlog.db"
    core.DB_PATH = test_db
    
    # Initialize the test DB explicitly since we are testing core logic too
    core.init_db()
    
    yield
    
    # Teardown
    core.DB_PATH = original_db_path
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            pass

def test_registrar_friccion():
    with TestClient(api_module.app) as client:
        # Min length is 10
        response = client.post("/registrar-friccion", json={"description": "Test friction long enough", "severity": 3})
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert "id" in response.json()

def test_registrar_friccion_too_short():
    with TestClient(api_module.app) as client:
        response = client.post("/registrar-friccion", json={"description": "short", "severity": 3})
        assert response.status_code == 422 # Pydantic validation error

def test_list_fricciones():
    with TestClient(api_module.app) as client:
        # Create one
        client.post("/registrar-friccion", json={"description": "Test list description long", "severity": 1})
        
        response = client.get("/fricciones")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Test list" in data[0]["description"]

def test_analyze_friction_persistence(monkeypatch):
    """Test that analyzing a friction persists the data in DB."""
    monkeypatch.delenv("LLM_API_URL", raising=False)
    
    with TestClient(api_module.app) as client:
        # 1. Create friction
        resp = client.post("/registrar-friccion", json={"description": "Test persistence long description", "severity": 2})
        friction_id = resp.json()["id"]
        
        # 2. Analyze it
        resp = client.post(f"/fricciones/{friction_id}/analizar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        
        # 3. Verify persistence
        resp = client.get("/fricciones")
        items = resp.json()
        # Find our item
        item = next((x for x in items if x["id"] == friction_id), None)
        assert item is not None
        assert item["nombre_comercial"] == "IdeaLab-Core" # Default heuristic fallback
        assert item["categoria"] == "General"
