
import pytest
from httpx import AsyncClient
from api_service.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_submit_job_invalid_url():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/images/process", json={
            "imageUrl": "not-a-url",
            "transformations": ["resize:100x100"]
        })
    assert response.status_code == 422 # Validation Error
