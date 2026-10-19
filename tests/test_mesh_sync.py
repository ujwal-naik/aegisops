import pytest
import time
from aegisops.database import IncidentStore
from aegisops.models import Incident, TriageCategory, SyncPayload
from aegisops.mesh_sync import MeshSyncProtocol

def test_mesh_export_and_ingest():
    store_a = IncidentStore(persistence_path="test_store_a.json")
    store_a.clear()
    proto_a = MeshSyncProtocol(store_a, local_node_id="node-alpha")

    # Add incident in Node A
    inc1 = Incident(
        id="inc-test-1",
        latitude=12.8700,
        longitude=74.8500,
        location_name="Node A Site",
        raw_report="Flooded ground floor",
        triage_level=TriageCategory.YELLOW,
        urgency_score=60.0,
        vector_clock=1
    )
    store_a.add_incident(inc1)

    # Node A exports sync payload
    payload = proto_a.export_delta_package(since_timestamp=0.0)
    assert len(payload.incidents) == 1
    assert payload.sender_node_id == "node-alpha"

    # Node B receives payload
    store_b = IncidentStore(persistence_path="test_store_b.json")
    store_b.clear()
    proto_b = MeshSyncProtocol(store_b, local_node_id="node-bravo")

    res = proto_b.ingest_sync_package(payload)
    assert res["new_incidents_added"] == 1

    stored_b = store_b.get_incident("inc-test-1")
    assert stored_b is not None
    assert stored_b.location_name == "Node A Site"

    # Clean up test stores
    store_a.clear()
    store_b.clear()
