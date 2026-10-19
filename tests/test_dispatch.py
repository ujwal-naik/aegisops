import pytest
from aegisops.models import Incident, RescueUnit, TriageCategory, UnitType, UnitStatus, IncidentStatus
from aegisops.dispatch import DispatchOptimizer

def test_dispatch_capability_and_proximity():
    # Flood incident requiring WATER_RESCUE
    flood_inc = Incident(
        id="inc-flood",
        latitude=12.8600,
        longitude=74.8400,
        location_name="Inundated Jetty",
        raw_report="People stranded on jetty, water rising",
        triage_level=TriageCategory.RED,
        urgency_score=95.0,
        required_unit_type=UnitType.WATER_RESCUE
    )

    # 1 Water Rescue boat close by, 1 Ambulance closer
    boat = RescueUnit(
        id="boat-1",
        name="Zodiac 1",
        unit_type=UnitType.WATER_RESCUE,
        latitude=12.8620,
        longitude=74.8410,
        status=UnitStatus.AVAILABLE,
        speed_kmh=30.0,
        contact_callsign="Z-1"
    )

    amb = RescueUnit(
        id="amb-1",
        name="Ambulance 1",
        unit_type=UnitType.AMBULANCE,
        latitude=12.8605,
        longitude=74.8405,
        status=UnitStatus.AVAILABLE,
        speed_kmh=50.0,
        contact_callsign="A-1"
    )

    match = DispatchOptimizer.find_best_unit(flood_inc, [boat, amb])
    assert match is not None
    best_unit, dist_km, eta_min = match
    # Must pick boat because capability matches WATER_RESCUE
    assert best_unit.id == "boat-1"

def test_auto_dispatch_prioritizes_red():
    red_inc = Incident(
        id="inc-red",
        latitude=12.8700,
        longitude=74.8500,
        location_name="Critical Collapse",
        raw_report="Pinned victims, heavy bleeding",
        triage_level=TriageCategory.RED,
        urgency_score=98.0,
        required_unit_type=UnitType.AMBULANCE
    )

    green_inc = Incident(
        id="inc-green",
        latitude=12.8710,
        longitude=74.8510,
        location_name="Minor Shelter Needs",
        raw_report="Need blankets",
        triage_level=TriageCategory.GREEN,
        urgency_score=20.0,
        required_unit_type=UnitType.AMBULANCE
    )

    amb = RescueUnit(
        id="amb-solo",
        name="Solo Ambulance",
        unit_type=UnitType.AMBULANCE,
        latitude=12.8705,
        longitude=74.8505,
        status=UnitStatus.AVAILABLE,
        contact_callsign="SOLO"
    )

    dispatches = DispatchOptimizer.auto_dispatch_all([green_inc, red_inc], [amb])
    assert len(dispatches) == 1
    # Must allocate the single ambulance to the RED incident first
    assert dispatches[0]["incident_id"] == "inc-red"
    assert dispatches[0]["unit_id"] == "amb-solo"
