import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["friend"] == "Maya"

@pytest.mark.asyncio
async def test_demo_samples_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/demo-samples")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 4

@pytest.mark.asyncio
async def test_analyze_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "product_name": "Gluten-Free Brown Rice Pasta",
            "ingredients_text": "Organic brown rice flour, water. Certified Gluten-Free.",
            "category": "pasta",
            "dedicated_facility": True,
            "certified_gf": True
        }
        res = await client.post("/api/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["verdict"] == "SAFE"
        assert "tabpfn" in data
        assert "gemma_analysis" in data
