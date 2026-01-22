
import pytest
import asyncio
import httpx
from uuid import UUID

API_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_end_to_end_flow():
    # 1. Submit Job
    async with httpx.AsyncClient() as client:
        payload = {
            "imageUrl": "http://api-service:8000/static/tests/fixtures/test_image.pgm",
            "transformations": ["resize:100x100", "grayscale"]
        }
        response = await client.post(f"{API_URL}/api/v1/images/process", json=payload)
        assert response.status_code == 202
        data = response.json()
        job_id = data["jobId"]
        assert job_id is not None

    # 2. Poll Status
    max_retries = 30
    async with httpx.AsyncClient() as client:
        for _ in range(max_retries):
            await asyncio.sleep(1)
            response = await client.get(f"{API_URL}/api/v1/images/jobs/{job_id}")
            assert response.status_code == 200
            data = response.json()
            status = data["status"]
            
            if status == "COMPLETED":
                assert data["resultUrl"] is not None
                break
            if status == "FAILED":
                pytest.fail(f"Job failed: {data.get('errorMessage')}")
        else:
            pytest.fail("Job timed out")
