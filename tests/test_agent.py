import pytest
from app.core.agent import allerguard_agent

@pytest.mark.asyncio
async def test_agent_full_pipeline_danger():
    result = await allerguard_agent.analyze_product(
        product_name="Dark Chocolate Peanut Crisp Bar",
        ingredients_text="Soy crisp, almond butter, peanut flour, wheat starch, natural flavors.",
        category="energy_bar",
        dedicated_facility=False,
        certified_allergen_free=False
    )
    assert result["verdict"] == "DANGER"
    assert "user_name" in result
    assert len(result["telemetry"]["traces"]) == 4
    assert result["telemetry"]["total_latency_ms"] > 0
    assert any(term in result["tabpfn"]["features_extracted"]["direct_allergens"] for term in ["almond", "peanut flour", "peanut"])
    assert "[DANGER" in result["gemma_analysis"]["analysis"]

@pytest.mark.asyncio
async def test_agent_full_pipeline_safe():
    result = await allerguard_agent.analyze_product(
        product_name="Certified Organic Corn Tortillas",
        ingredients_text="White corn, water, lime. Certified Allergen-Free.",
        category="snacks",
        dedicated_facility=True,
        certified_allergen_free=True
    )
    assert result["verdict"] == "SAFE"
    assert result["tabpfn"]["probabilities"]["safe"] > 70.0
    assert "[SAFE]" in result["gemma_analysis"]["analysis"]

