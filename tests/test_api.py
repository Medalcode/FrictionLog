import os
import pytest
from fastapi.testclient import TestClient
import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def setup_teardown_db():
    """Use a separate database for tests."""
    original_db_path = app_module.DB_PATH
    test_db = "test_frictionlog.db"
    app_module.DB_PATH = test_db
    
    # Ensure tables exist in the test DB
    app_module.ensure_tables()
    app_module.migrate_tables()
    
    yield
    
    # Teardown
    app_module.DB_PATH = original_db_path
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            pass

def test_registrar_friccion():
    response = client.post("/registrar-friccion", json={"description": "Test friction", "severity": 3})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "id" in response.json()

def test_registrar_friccion_missing_desc():
    response = client.post("/registrar-friccion", json={"severity": 3})
    assert response.status_code == 422 # Pydantic validation error

def test_list_fricciones():
    # Create one
    client.post("/registrar-friccion", json={"description": "Test list", "severity": 1})
    
    response = client.get("/fricciones")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["description"] == "Test list"

def test_analizar_con_ia_heuristic(monkeypatch):
    """Test heuristic fallback when LLM_API_URL is not set."""
    monkeypatch.delenv("LLM_API_URL", raising=False)
    
    response = client.post("/analizar-con-ia", json={"description": "Problema con Debian apt install"})
    assert response.status_code == 200
    data = response.json()
    assert data["from"] == "heuristic"
    # Logic in app.py checks generally for "debian" or "apt"
    assert "DevOps" in data["categoria"]
    assert "PyDeb-Shield" in data["nombre_comercial"]

def test_analyze_friction_persistence(monkeypatch):
    """Test that analyzing a friction persists the data in DB."""
    monkeypatch.delenv("LLM_API_URL", raising=False)
    
    # 1. Create friction
    resp = client.post("/registrar-friccion", json={"description": "Test persistence", "severity": 2})
    friction_id = resp.json()["id"]
    
    # 2. Analyze it
    resp = client.post(f"/fricciones/{friction_id}/analizar")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    # Check immediate response structure
    analysis = data["analysis"]
    assert analysis["from"] == "heuristic"
    
    # 3. Verify persistence
    resp = client.get("/fricciones")
    items = resp.json()
    # Find our item
    item = next((x for x in items if x["id"] == friction_id), None)
    assert item is not None
    assert item["nombre_comercial"] == "IdeaLab-Core" # Default heuristic fallback
    assert item["categoria"] == "General"
