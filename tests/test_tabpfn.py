import pytest
from app.core.tabpfn_classifier import tabpfn_classifier

def test_tabpfn_safe_cassava_chips():
    ingredients = "Cassava flour, avocado oil, coconut flour, sea salt. Certified Gluten-Free."
    result = tabpfn_classifier.predict(
        raw_text=ingredients,
        category="snacks",
        dedicated_facility=True,
        certified_gf=True
    )
    assert result["risk_level"] == "SAFE"
    assert result["probabilities"]["safe"] > 70.0
    assert result["features_extracted"]["certified_gluten_free"] is True

def test_tabpfn_danger_wheat_pretzels():
    ingredients = "Enriched wheat flour, malt extract, salt, soybean oil, barley malt."
    result = tabpfn_classifier.predict(
        raw_text=ingredients,
        category="snacks",
        dedicated_facility=False,
        certified_gf=False
    )
    assert result["risk_level"] == "DANGER"
    assert result["probabilities"]["danger"] > 80.0
    assert "wheat" in result["features_extracted"]["direct_allergens"]

def test_tabpfn_caution_ambiguous_dressing():
    ingredients = "Canola oil, modified food starch, natural flavors, spices, caramel color."
    result = tabpfn_classifier.predict(
        raw_text=ingredients,
        category="salad_dressing",
        dedicated_facility=False,
        certified_gf=False
    )
    assert result["risk_level"] in ("CAUTION", "DANGER")
    assert len(result["features_extracted"]["ambiguous_terms"]) >= 3
