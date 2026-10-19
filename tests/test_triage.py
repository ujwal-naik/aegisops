import pytest
from aegisops.models import TriageCategory, UnitType
from aegisops.triage import TriageEngine

def test_triage_critical_red_drowning():
    text = "Basement submerged, water waist high! 4 people trapped, one is unconscious and not breathing!"
    res = TriageEngine.evaluate(text)

    assert res["triage_level"] == TriageCategory.RED
    assert res["urgency_score"] >= 85.0
    assert "flood_water" in res["hazards"]
    assert res["required_unit_type"] == UnitType.WATER_RESCUE
    assert res["trapped_count"] == 4

def test_triage_structural_collapse():
    text = "Building collapsed into rubble, 2 victims pinned under concrete beam with heavy bleeding and gas smell."
    res = TriageEngine.evaluate(text)

    assert res["triage_level"] == TriageCategory.RED
    assert "structural_collapse" in res["hazards"]
    assert "gas_leak" in res["hazards"]
    assert res["required_unit_type"] == UnitType.WATER_RESCUE or res["required_unit_type"] == UnitType.HEAVY_SAR

def test_triage_delayed_yellow_fracture():
    text = "Volunteer fell and has a severe leg fracture and broken bone. Immobile but alert and breathing normally."
    res = TriageEngine.evaluate(text)

    assert res["triage_level"] == TriageCategory.YELLOW
    assert 50.0 <= res["urgency_score"] < 85.0

def test_triage_minor_green():
    text = "School shelter has 20 people walking wounded, mild scratches, need drinking water and blankets."
    res = TriageEngine.evaluate(text)

    assert res["triage_level"] == TriageCategory.GREEN
    assert res["urgency_score"] < 50.0

def test_triage_deceased_black():
    text = "Single victim found with no pulse, cold and stiff, fatal trauma."
    res = TriageEngine.evaluate(text)

    assert res["triage_level"] == TriageCategory.BLACK
    assert res["survivor_count"] == 0
