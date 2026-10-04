import pytest
from app.core.tabpfn_classifier import tabpfn_classifier

def test_tabpfn_danger_sesame_tahini():
    ingredients = "Chickpeas, tahini (ground sesame seeds), olive oil, garlic, lemon juice, sea salt."
    result = tabpfn_classifier.predict(
        raw_text=ingredients,
        category="sauces",
        dedicated_facility=False,
        certified_allergen_free=False
    )
    assert result["risk_level"] == "DANGER"
    assert result["probabilities"]["danger"] > 80.0
    assert any(term in result["features_extracted"]["direct_allergens"] for term in ["tahini", "sesame", "sesame seeds"])

def test_tabpfn_danger_coconut_vegan_cheese():
    ingredients = "Filtered water, modified potato starch, refined coconut oil, coconut cream, sea salt, natural flavors."
    result = tabpfn_classifier.predict(
        raw_text=ingredients,
        category="dairy_alt",
        dedicated_facility=False,
        certified_allergen_free=False
    )
    assert result["risk_level"] == "DANGER"
    assert result["probabilities"]["danger"] > 80.0
    assert any("coconut" in term for term in result["features_extracted"]["direct_allergens"])

def test_tabpfn_danger_tree_nut_peanut():
    ingredients = "Rolled oats, almond butter, peanut flour, honey, sea salt."
    result = tabpfn_classifier.predict(
        raw_text=ingredients,
        category="energy_bar",
        dedicated_facility=False,
        certified_allergen_free=False
    )
    assert result["risk_level"] == "DANGER"
    assert result["probabilities"]["danger"] > 80.0
    assert any(term in result["features_extracted"]["direct_allergens"] for term in ["almond", "peanut flour", "peanut"])

def test_tabpfn_safe_single_origin_rice():
    ingredients = "Organic whole grain brown rice, sea salt. Certified Allergen-Free."
    result = tabpfn_classifier.predict(
        raw_text=ingredients,
        category="snacks",
        dedicated_facility=True,
        certified_allergen_free=True
    )
    assert result["risk_level"] == "SAFE"
    assert result["probabilities"]["safe"] > 70.0
    assert result["features_extracted"]["certified_allergen_free"] is True

def test_tabpfn_caution_ambiguous_dressing():
    ingredients = "Canola oil, modified food starch, natural flavors, spices, caramel color."
    result = tabpfn_classifier.predict(
        raw_text=ingredients,
        category="condiments",
        dedicated_facility=False,
        certified_allergen_free=False
    )
    assert result["risk_level"] in ("CAUTION", "DANGER")
    assert len(result["features_extracted"]["ambiguous_terms"]) >= 2

