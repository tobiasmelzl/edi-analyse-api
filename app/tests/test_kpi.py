import pytest
from httpx import AsyncClient
from app.main import app
headers = {"X-API-Key": "supersecret"}

@pytest.mark.asyncio
async def test_health_ok():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_empty_kpi():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/kpi/partner", headers=headers)
    assert r.status_code == 200
    assert r.json() == []
