import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_auth_missing():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/partners")
    assert r.status_code == 401
