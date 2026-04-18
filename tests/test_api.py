import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import httpx
import api as api_module

@pytest.fixture(autouse=True)
def mock_pb_client(monkeypatch):
    """Fixture to mock PocketBase HTTP requests for all tests."""
    db_records = {}
    
    async def mock_post_impl(url, json=None, **kwargs):
        if "api/collections/fricciones/records" in url:
            record_id = f"mock_{len(db_records) + 1}"
            record = {
                "id": record_id,
                "user_id": json.get("user_id", "anonymous") if json else "anonymous",
                "description": json.get("description", "") if json else "",
                "severity": json.get("severity", 1) if json else 1,
                "created": "2026-05-21T19:00:00Z",
                "categoria": None,
                "tipo_problema": None,
                "impacto": None,
                "idea_solucion": None
            }
            db_records[record_id] = record
            
            mock_res = MagicMock(spec=httpx.Response)
            mock_res.status_code = 200
            mock_res.json.return_value = record
            return mock_res
        raise ValueError(f"Unmocked POST URL: {url}")
        
    async def mock_get_impl(url, **kwargs):
        if "api/collections/fricciones/records?" in url or url.endswith("api/collections/fricciones/records"):
            mock_res = MagicMock(spec=httpx.Response)
            mock_res.status_code = 200
            mock_res.json.return_value = {"items": list(db_records.values())}
            return mock_res
        elif "api/collections/fricciones/records/" in url:
            record_id = url.split("/")[-1]
            if record_id in db_records:
                mock_res = MagicMock(spec=httpx.Response)
                mock_res.status_code = 200
                mock_res.json.return_value = db_records[record_id]
                return mock_res
            else:
                mock_res = MagicMock(spec=httpx.Response)
                mock_res.status_code = 404
                mock_res.text = "Not Found"
                return mock_res
        raise ValueError(f"Unmocked GET URL: {url}")
        
    async def mock_patch_impl(url, json=None, **kwargs):
        if "api/collections/fricciones/records/" in url:
            record_id = url.split("/")[-1]
            if record_id in db_records:
                db_records[record_id].update(json)
                mock_res = MagicMock(spec=httpx.Response)
                mock_res.status_code = 200
                mock_res.json.return_value = db_records[record_id]
                return mock_res
            else:
                mock_res = MagicMock(spec=httpx.Response)
                mock_res.status_code = 404
                mock_res.text = "Not Found"
                return mock_res
        raise ValueError(f"Unmocked PATCH URL: {url}")
        
    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post_impl)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_impl)
    monkeypatch.setattr(httpx.AsyncClient, "patch", mock_patch_impl)
    
    return db_records

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
    # Mock Gemini API response in core.py
    monkeypatch.setattr(api_module.core, "analizar_friccion", lambda desc: {
        "categoria": "DevOps",
        "tipo_problema": "latencia alta en base de datos",
        "impacto": "alto",
        "idea_solucion": "implementar caché con redis para endpoints de lectura"
    })
    
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
        assert item["nombre_comercial"] == "latencia alta en base de datos"
        assert item["categoria"] == "DevOps"
        assert item["arquitectura"] == "Impacto: alto"
        assert item["mvp_features"] == "implementar caché con redis para endpoints de lectura"

def test_analizar_con_ia(monkeypatch):
    # Mock API_KEY to pass the config check
    monkeypatch.setattr(api_module, "API_KEY", "mock_key")
    # Mock analizar_friccion in api module
    monkeypatch.setattr(api_module, "analizar_friccion", lambda desc: {
        "categoria": "DevOps",
        "tipo_problema": "latencia alta en base de datos",
        "impacto": "alto",
        "idea_solucion": "implementar caché con redis para endpoints de lectura"
    })
    
    with TestClient(api_module.app) as client:
        response = client.post("/analizar-con-ia", json={"description": "Test description long enough"})
        assert response.status_code == 200
        data = response.json()
        assert "analisis" in data
        assert data["analisis"]["categoria"] == "DevOps"
        assert data["analisis"]["tipo_problema"] == "latencia alta en base de datos"
        assert data["analisis"]["impacto"] == "alto"
        assert data["analisis"]["idea_solucion"] == "implementar caché con redis para endpoints de lectura"
