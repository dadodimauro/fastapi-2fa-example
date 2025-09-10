import httpx
import pytest
from fastapi import FastAPI, status


@pytest.mark.asyncio
async def test_healthz(
    app: FastAPI,
) -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/healthz")
        assert response.status_code == status.HTTP_200_OK
