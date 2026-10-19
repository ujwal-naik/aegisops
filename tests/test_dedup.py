import pytest
import time
from aegisops.models import Incident, TriageCategory, IncidentStatus
from aegisops.dedup import haversine_distance_meters, DeduplicationEngine

def test_haversine_calculation():
    # Mangalore points ~ 1km apart
    dist = haversine_distance_meters(12.8700, 74.8500, 12.8790, 74.8500)
    assert 950.0 < dist < 1050.0

def test_deduplication_clustering():
    base_time = time.time()
    inc1 = Incident(
        id="inc-orig",
        timestamp=base_time,
        latitude=12.8795,
        longitude=74.8475,
        location_name="Market Road Complex",
        raw_report="Building collapsed into rubble, family pinned under slab, gas leak!",
        triage_level=TriageCategory.RED,
        urgency_score=90.0,
        survivor_count=3,
        trapped_count=3,
        hazards=["structural_collapse", "gas_leak"]
    )

    # 40 meters away, 5 minutes later, same collapse reported by neighbour
    inc2 = Incident(
        id="inc-dup",
        timestamp=base_time + 300,
        latitude=12.8792,
        longitude=74.8478,
        location_name="Market Road side lane",
        raw_report="Apartment building collapsed on Market Road, people trapped under debris!",
        triage_level=TriageCategory.RED,
        urgency_score=85.0,
        survivor_count=4,
        trapped_count=4,
        hazards=["structural_collapse"]
    )

    dup = DeduplicationEngine.check_duplicate(inc2, [inc1])
    assert dup is not None
    assert dup.id == "inc-orig"

    # Merge
    merged = DeduplicationEngine.merge_into_master(inc1, inc2)
    assert inc2.status == IncidentStatus.DUPLICATE
    assert inc2.duplicate_of == "inc-orig"
    assert merged.survivor_count == 4  # Upgraded to higher victim count
    assert len(merged.duplicate_reports) == 1
