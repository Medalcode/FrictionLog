from unittest.mock import MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

import api as api_module
import core as core_module


@pytest.fixture(autouse=True)
def no_auth(monkeypatch):
    monkeypatch.setattr(api_module, "FRICTIONLOG_API_KEY", None)


@pytest.fixture(autouse=True)
def mock_pb_client(monkeypatch):
    """Fixture to mock PocketBase HTTP requests for all tests."""
    db_records = {}

    async def mock_post_impl(_self, url, **kwargs):
        json_data = kwargs.get("json") or {}
        if "api/collections/fricciones/records" in url:
            record_id = f"mock_{len(db_records) + 1}"
            record = {
                "id": record_id,
                "user_id": json_data.get("user_id", "anonymous"),
                "description": json_data.get("description", ""),
                "severity": json_data.get("severity", 1),
                "created": "2026-05-21T19:00:00Z",
                "categoria": None,
                "tipo_problema": None,
                "impacto": None,
                "idea_solucion": None,
            }
            db_records[record_id] = record

            mock_res = MagicMock(spec=httpx.Response)
            mock_res.status_code = 200
            mock_res.json.return_value = record
            return mock_res
        return _not_found(f"Unmocked POST URL: {url}")

    async def mock_get_impl(_self, url, **_kwargs):
        if "api/collections/fricciones/records?" in url or url.endswith(
            "api/collections/fricciones/records"
        ):
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
            return _not_found("Not Found")
        return _not_found(f"Unmocked GET URL: {url}")

    async def mock_patch_impl(_self, url, **kwargs):
        json_data = kwargs.get("json", {})
        if "api/collections/fricciones/records/" in url:
            record_id = url.split("/")[-1]
            if record_id in db_records:
                db_records[record_id].update(json_data)
                mock_res = MagicMock(spec=httpx.Response)
                mock_res.status_code = 200
                mock_res.json.return_value = db_records[record_id]
                return mock_res
            return _not_found("Not Found")
        return _not_found(f"Unmocked PATCH URL: {url}")

    async def mock_delete_impl(_self, url, **_kwargs):
        if "api/collections/fricciones/records/" in url:
            record_id = url.split("/")[-1]
            if record_id in db_records:
                del db_records[record_id]
                mock_res = MagicMock(spec=httpx.Response)
                mock_res.status_code = 204
                return mock_res
            return _not_found("Not Found")
        return _not_found(f"Unmocked DELETE URL: {url}")

    def _not_found(msg):
        mock_res = MagicMock(spec=httpx.Response)
        mock_res.status_code = 404
        mock_res.text = msg
        return mock_res

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post_impl)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_impl)
    monkeypatch.setattr(httpx.AsyncClient, "patch", mock_patch_impl)
    monkeypatch.setattr(httpx.AsyncClient, "delete", mock_delete_impl)

    return db_records


@pytest.fixture()
def client():
    with TestClient(api_module.app) as c:
        yield c


def _mock_llm(monkeypatch, response: dict):
    monkeypatch.setattr(core_module, "analizar_friccion", lambda _desc: response)


def test_registrar_friccion(client):
    response = client.post(
        "/registrar-friccion",
        json={"description": "Test friction long enough", "severity": 3},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "id" in response.json()


def test_registrar_friccion_too_short(client):
    response = client.post("/registrar-friccion", json={"description": "short", "severity": 3})
    assert response.status_code == 422


def test_list_fricciones(client):
    client.post(
        "/registrar-friccion",
        json={"description": "Test list description long", "severity": 1},
    )
    response = client.get("/fricciones")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Test list" in data[0]["description"]


def test_analyze_friction_persistence(client, monkeypatch):
    _mock_llm(
        monkeypatch,
        {
            "categoria": "DevOps",
            "tipo_problema": "latencia alta en base de datos",
            "impacto": "alto",
            "idea_solucion": "implementar caché con redis",
        },
    )

    resp = client.post(
        "/registrar-friccion",
        json={"description": "Test persistence long description", "severity": 2},
    )
    friction_id = resp.json()["id"]

    resp = client.post(f"/fricciones/{friction_id}/analizar")
    assert resp.status_code == 200

    resp = client.get("/fricciones")
    items = resp.json()
    item = next((x for x in items if x["id"] == friction_id), None)
    assert item is not None
    assert item["categoria"] == "DevOps"
    assert item["tipo_problema"] == "latencia alta en base de datos"
    assert item["impacto"] == "alto"
    assert item["idea_solucion"] == "implementar caché con redis"


def test_analizar_con_ia(client, monkeypatch):
    _mock_llm(
        monkeypatch,
        {
            "categoria": "UX",
            "tipo_problema": "menú confuso",
            "impacto": "medio",
            "idea_solucion": "rediseñar navegación con breadcrumbs",
        },
    )

    response = client.post("/analizar-con-ia", json={"description": "Test description long enough"})
    assert response.status_code == 200
    data = response.json()
    assert data["analisis"]["categoria"] == "UX"
    assert data["analisis"]["tipo_problema"] == "menú confuso"
    assert data["analisis"]["impacto"] == "medio"
    assert data["analisis"]["idea_solucion"] == "rediseñar navegación con breadcrumbs"


def test_analizar_con_ia_llm_error(client, monkeypatch):
    _mock_llm(
        monkeypatch,
        {
            "categoria": "Sin clasificar",
            "tipo_problema": "Error de clasificación",
            "impacto": "Desconocido",
            "idea_solucion": "No se pudo generar una solución técnica.",
            "error": "API key inválida",
        },
    )

    response = client.post("/analizar-con-ia", json={"description": "Test LLM error long enough"})
    assert response.status_code == 502


def test_delete_friction(client):
    resp = client.post(
        "/registrar-friccion",
        json={"description": "Friction to be deleted soon", "severity": 1},
    )
    friction_id = resp.json()["id"]

    resp_get = client.get("/fricciones")
    assert any(item["id"] == friction_id for item in resp_get.json())

    resp_del = client.delete(f"/fricciones/{friction_id}")
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "ok"

    resp_get2 = client.get("/fricciones")
    assert not any(item["id"] == friction_id for item in resp_get2.json())


def test_pocketbase_502_error(monkeypatch, client):
    async def mock_get_502(_self, _url, **_kwargs):
        mock_res = MagicMock(spec=httpx.Response)
        mock_res.status_code = 502
        mock_res.text = "Bad Gateway"
        return mock_res

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_502)

    response = client.get("/fricciones")
    assert response.status_code == 502
    assert "Error al buscar en PocketBase" in response.json()["detail"]


def test_auth_required(monkeypatch):
    monkeypatch.setattr(api_module, "FRICTIONLOG_API_KEY", "secret123")
    with TestClient(api_module.app) as c:
        response = c.get("/fricciones")
        assert response.status_code == 401

        response = c.get("/fricciones", headers={"Authorization": "Bearer wrong"})
        assert response.status_code == 401

        response = c.get("/fricciones", headers={"Authorization": "Bearer secret123"})
        assert response.status_code == 200


def test_create_friction_with_auth(monkeypatch):
    monkeypatch.setattr(api_module, "FRICTIONLOG_API_KEY", "secret123")
    with TestClient(api_module.app) as c:
        resp = c.post(
            "/registrar-friccion",
            json={"description": "Test auth friction long enough", "severity": 3},
        )
        assert resp.status_code == 401

        resp = c.post(
            "/registrar-friccion",
            json={"description": "Test auth friction long enough", "severity": 3},
            headers={"Authorization": "Bearer secret123"},
        )
        assert resp.status_code == 200
