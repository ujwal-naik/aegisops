import time
from aegisops.models import Incident, RescueUnit, EvacuationZone, MeshNode, UnitType, UnitStatus
from aegisops.database import IncidentStore
from aegisops.triage import TriageEngine
from aegisops.dedup import DeduplicationEngine

def load_mock_scenario(store: IncidentStore) -> int:
    """
    Populates store with realistic disaster scenario:
    'Operation CoastalShield' - Severe Category 4 Cyclone landfall and Flash Flood.
    Centered around coordinates (12.9141, 74.8560).
    """
    store.clear()

    # 1. Evacuation Zones
    evac_zones = [
        EvacuationZone(
            id="EZ-01",
            name="City Indoor Stadium (Shelter Alpha)",
            latitude=12.8710,
            longitude=74.8450,
            capacity=1000,
            current_occupancy=280,
            is_safe=True,
            notes="Equipped with backup diesel generator and clean water purification."
        ),
        EvacuationZone(
            id="EZ-02",
            name="St. Aloysius Higher Ground Relief Camp",
            latitude=12.8765,
            longitude=74.8580,
            capacity=600,
            current_occupancy=195,
            is_safe=True,
            notes="Medical triage station and baby supplies available."
        ),
        EvacuationZone(
            id="EZ-03",
            name="Hilltop Community Center",
            latitude=12.9050,
            longitude=74.8720,
            capacity=400,
            current_occupancy=85,
            is_safe=True,
            notes="High elevation staging area for helicopter airlifts."
        )
    ]
    for zone in evac_zones:
        store.add_evac_zone(zone)

    # 2. Rescue Fleet Units
    rescue_units = [
        RescueUnit(
            id="UNIT-BOAT-01",
            name="NDRF Zodiac Swift Boat 1",
            unit_type=UnitType.WATER_RESCUE,
            latitude=12.8800,
            longitude=74.8400,
            status=UnitStatus.AVAILABLE,
            capacity=8,
            fuel_pct=90,
            speed_kmh=35.0,
            contact_callsign="ZODIAC-ALPHA"
        ),
        RescueUnit(
            id="UNIT-BOAT-02",
            name="Coast Guard Inflatable Rescue 2",
            unit_type=UnitType.WATER_RESCUE,
            latitude=12.8650,
            longitude=74.8350,
            status=UnitStatus.AVAILABLE,
            capacity=6,
            fuel_pct=85,
            speed_kmh=40.0,
            contact_callsign="COASTAL-BRAVO"
        ),
        RescueUnit(
            id="UNIT-SAR-01",
            name="Heavy Urban Search & Rescue Squad 3",
            unit_type=UnitType.HEAVY_SAR,
            latitude=12.8820,
            longitude=74.8510,
            status=UnitStatus.AVAILABLE,
            capacity=5,
            fuel_pct=75,
            speed_kmh=30.0,
            contact_callsign="TITAN-RESCUE"
        ),
        RescueUnit(
            id="UNIT-AMB-01",
            name="Advanced Life Support Ambulance 09",
            unit_type=UnitType.AMBULANCE,
            latitude=12.8730,
            longitude=74.8480,
            status=UnitStatus.AVAILABLE,
            capacity=2,
            fuel_pct=95,
            speed_kmh=50.0,
            contact_callsign="MEDIC-NINE"
        ),
        RescueUnit(
            id="UNIT-MED-01",
            name="Red Cross Mobile Trauma Strike Unit",
            unit_type=UnitType.MEDICAL_STRIKE,
            latitude=12.8790,
            longitude=74.8620,
            status=UnitStatus.AVAILABLE,
            capacity=4,
            fuel_pct=80,
            speed_kmh=45.0,
            contact_callsign="TRIAGE-DOCTOR-1"
        ),
        RescueUnit(
            id="UNIT-DRONE-01",
            name="SkyScan Thermal Recon Drone",
            unit_type=UnitType.AERIAL_DRONE,
            latitude=12.8850,
            longitude=74.8500,
            status=UnitStatus.AVAILABLE,
            capacity=0,
            fuel_pct=92,
            speed_kmh=65.0,
            contact_callsign="SKYEYE-ONE"
        )
    ]
    for unit in rescue_units:
        store.add_unit(unit)

    # 3. Mesh Nodes
    nodes = [
        MeshNode(node_id="node-alpha-command", node_name="Incident Command Center", hop_count=0, is_gateway=True),
        MeshNode(node_id="node-bravo-relay", node_name="Mobile Command Van (NH-66)", hop_count=1, is_gateway=False),
        MeshNode(node_id="node-drone-mule", node_name="Tethered Aerial LoRa Hub", hop_count=2, is_gateway=False)
    ]
    for n in nodes:
        store.register_mesh_node(n)

    # 4. Realistic Raw Emergency Reports
    raw_scenarios = [
        {
            "loc": "Riverview Senior Living, Jeppu",
            "lat": 12.8620, "lon": 74.8490,
            "text": "Basement and ground floor submerged in water rising rapidly! 8 elderly people trapped on first floor, 2 unconscious and need oxygen urgently, water waist high!"
        },
        {
            "loc": "Market Road Complex, Block C",
            "lat": 12.8795, "lon": 74.8475,
            "text": "Building partially collapsed into rubble. 4 family members pinned under concrete slab. Strong hissing gas smell, danger of fire!"
        },
        {
            "loc": "Market Road commercial lane",
            "lat": 12.8792, "lon": 74.8478,
            "text": "Collapse on Market road! People pinned under debris and shouting for help, strong smell of cooking gas leak!"
        }, # Intentional duplicate near (12.8795, 74.8475) to demonstrate deduplication!
        {
            "loc": "Bolar Old Port Jetty",
            "lat": 12.8550, "lon": 74.8380,
            "text": "Boat overturned in storm surge. 3 fishermen clinging to wooden pillar, water current strong, drowning risk!"
        },
        {
            "loc": "NH-66 Causeway Underpass",
            "lat": 12.8900, "lon": 74.8620,
            "text": "SUV completely submerged up to windows. Driver trapped inside, water neck deep, cannot break glass!"
        },
        {
            "loc": "Kodialbail Primary School",
            "lat": 12.8830, "lon": 74.8560,
            "text": "Community shelter with 40 people. Everyone walking and stable, but drinking water ran out, need food and blankets."
        },
        {
            "loc": "Car Street Ayurvedic Center",
            "lat": 12.8715, "lon": 74.8430,
            "text": "Elderly diabetic patient collapsed, need insulin urgently. Another young volunteer has a broken bone fracture in left leg."
        },
        {
            "loc": "Kadri Hills 4th Cross",
            "lat": 12.8910, "lon": 74.8670,
            "text": "High voltage power line snapped and sparking in water pool on main road. Pedestrians cannot pass, severe electrocution hazard."
        },
        {
            "loc": "Mangaladevi Temple lane",
            "lat": 12.8590, "lon": 74.8530,
            "text": "Pregnant woman in late third trimester active labor pains. Road flooded, no vehicle can reach."
        },
        {
            "loc": "Bunder Wharf Warehouse",
            "lat": 12.8680, "lon": 74.8390,
            "text": "Tin roof blown off. 2 workers have deep laceration cuts on arms, moderate bleeding, stable and conscious, need wound dressing."
        }
    ]

    for item in raw_scenarios:
        triage_eval = TriageEngine.evaluate(item["text"])
        inc = Incident(
            latitude=item["lat"],
            longitude=item["lon"],
            location_name=item["loc"],
            raw_report=item["text"],
            triage_level=triage_eval["triage_level"],
            urgency_score=triage_eval["urgency_score"],
            survivor_count=triage_eval["survivor_count"],
            trapped_count=triage_eval["trapped_count"],
            hazards=triage_eval["hazards"],
            required_unit_type=triage_eval["required_unit_type"],
            origin_node_id="mesh-relay-bravo"
        )

        existing = store.list_incidents(include_duplicates=True)
        dup = DeduplicationEngine.check_duplicate(inc, existing)
        if dup:
            DeduplicationEngine.merge_into_master(dup, inc)
            store.update_incident(dup)
            store.add_incident(inc)
        else:
            store.add_incident(inc)

    return len(store.incidents)
