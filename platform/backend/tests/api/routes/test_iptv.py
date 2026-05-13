"""IPTV public routes — no DB. Run without Postgres: PYTEST_DISABLE_DB_FIXTURE=1 pytest ..."""

from fastapi.testclient import TestClient

from app.core.config import settings


def test_iptv_bootstrap(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/iptv/bootstrap")
    assert r.status_code == 200
    body = r.json()
    assert body["schema_version"] == "0.1"
    assert "gateway_hls_base_url" in body


def test_iptv_health(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/iptv/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "vella-iptv-control-plane"
