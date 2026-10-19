import time
import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from aegisops.models import (
    Incident, RescueUnit, EvacuationZone, TriageCategory,
    IncidentStatus, UnitStatus, SyncPayload
)
from aegisops.database import store
from aegisops.triage import TriageEngine
from aegisops.dedup import DeduplicationEngine
from aegisops.dispatch import DispatchOptimizer
from aegisops.mesh_sync import MeshSyncProtocol

app = FastAPI(
    title="AegisOps Disaster Coordination Engine",
    description="Offline-first tactical emergency coordination, START triage, and mesh sync API.",
    version="1.0.0"
)

# Initialize mesh sync protocol instance
mesh_protocol = MeshSyncProtocol(store, local_node_id="node-alpha-command")

# Pydantic schemas for requests
class ReportCreateRequest(BaseModel):
    raw_report: str
    latitude: float
    longitude: float
    location_name: str
    origin_node_id: Optional[str] = "field-reporter"

class ManualDispatchRequest(BaseModel):
    incident_id: str
    unit_id: str

class TriageOverrideRequest(BaseModel):
    triage_level: TriageCategory
    notes: Optional[str] = None

@app.get("/api/status")
def get_system_status():
    triage_counts = store.get_triage_summary()
    units = store.list_units()
    available_units = sum(1 for u in units if u.status == UnitStatus.AVAILABLE)

    return {
        "status": "OPERATIONAL",
        "node_id": mesh_protocol.local_node_id,
        "timestamp": time.time(),
        "triage_summary": triage_counts,
        "fleet": {
            "total_units": len(units),
            "available_units": available_units,
            "dispatched_units": len(units) - available_units
        },
        "mesh_nodes_connected": len(store.list_mesh_nodes())
    }

@app.get("/api/incidents")
def get_incidents(
    triage: Optional[str] = None,
    status: Optional[str] = None,
    include_duplicates: bool = False
):
    incidents = store.list_incidents(include_duplicates=include_duplicates)

    if triage and triage.upper() != "ALL":
        incidents = [inc for inc in incidents if inc.triage_level.value == triage.upper()]

    if status:
        incidents = [inc for inc in incidents if inc.status.value == status.upper()]

    return {"count": len(incidents), "incidents": incidents}

@app.post("/api/incidents")
def create_incident(report: ReportCreateRequest):
    """
    Submits a new emergency report.
    Automatically executes NLP triage assessment and spatial deduplication.
    """
    # 1. Evaluate triage via START protocol
    triage_result = TriageEngine.evaluate(report.raw_report)

    # 2. Build Incident entity
    incident = Incident(
        latitude=report.latitude,
        longitude=report.longitude,
        location_name=report.location_name,
        raw_report=report.raw_report,
        triage_level=triage_result["triage_level"],
        urgency_score=triage_result["urgency_score"],
        survivor_count=triage_result["survivor_count"],
        trapped_count=triage_result["trapped_count"],
        hazards=triage_result["hazards"],
        required_unit_type=triage_result["required_unit_type"],
        origin_node_id=report.origin_node_id or "field-reporter"
    )

    # 3. Check for duplicates
    existing = store.list_incidents(include_duplicates=True)
    duplicate_master = DeduplicationEngine.check_duplicate(incident, existing)

    if duplicate_master:
        DeduplicationEngine.merge_into_master(duplicate_master, incident)
        store.update_incident(duplicate_master)
        store.add_incident(incident)
        return {
            "status": "DUPLICATE_CLUSTERED",
            "message": f"Clustered as duplicate of existing incident {duplicate_master.id} ({duplicate_master.location_name})",
            "incident": incident,
            "master_incident": duplicate_master
        }

    store.add_incident(incident)
    return {
        "status": "CREATED",
        "incident": incident,
        "triage_summary": triage_result
    }

@app.post("/api/incidents/{incident_id}/triage")
def override_triage(incident_id: str, req: TriageOverrideRequest):
    inc = store.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    inc.triage_level = req.triage_level
    inc.status = IncidentStatus.VERIFIED
    inc.updated_at = time.time()
    store.update_incident(inc)
    return {"message": "Triage updated", "incident": inc}

@app.post("/api/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str):
    inc = store.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    inc.status = IncidentStatus.RESOLVED
    inc.updated_at = time.time()

    # Free up assigned unit if any
    if inc.assigned_unit_id:
        unit = store.get_unit(inc.assigned_unit_id)
        if unit:
            unit.status = UnitStatus.AVAILABLE
            unit.current_incident_id = None
            store.update_unit(unit)

    store.update_incident(inc)
    return {"message": "Incident marked as resolved", "incident": inc}

@app.get("/api/units")
def get_units():
    return {"units": store.list_units()}

@app.post("/api/dispatch/auto")
def auto_dispatch():
    """
    Executes automated ICS-204 resource assignment across all pending incidents.
    """
    incidents = store.list_incidents()
    units = store.list_units()
    dispatches = DispatchOptimizer.auto_dispatch_all(incidents, units)

    # Persist updates
    for d in dispatches:
        inc = store.get_incident(d["incident_id"])
        if inc:
            store.update_incident(inc)
        u = store.get_unit(d["unit_id"])
        if u:
            store.update_unit(u)

    return {
        "dispatches_created": len(dispatches),
        "assignments": dispatches
    }

@app.post("/api/dispatch/manual")
def manual_dispatch(req: ManualDispatchRequest):
    inc = store.get_incident(req.incident_id)
    unit = store.get_unit(req.unit_id)

    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    inc.assigned_unit_id = unit.id
    inc.status = IncidentStatus.DISPATCHED
    inc.updated_at = time.time()
    store.update_incident(inc)

    unit.status = UnitStatus.DISPATCHED
    unit.current_incident_id = inc.id
    store.update_unit(unit)

    return {"message": f"Unit {unit.name} dispatched to {inc.location_name}", "incident": inc, "unit": unit}

@app.post("/api/mesh/sync")
def sync_mesh_package(payload: SyncPayload):
    """Ingests sync payload from a peer mesh node or offline courier."""
    result = mesh_protocol.ingest_sync_package(payload)
    return result

@app.get("/api/mesh/export")
def export_mesh_package(since: float = 0.0):
    """Exports sync payload for transmission over air link or storage medium."""
    pkg = mesh_protocol.export_delta_package(since_timestamp=since)
    return pkg

@app.get("/api/geojson")
def get_tactical_geojson():
    """Returns real-time GeoJSON FeatureCollection for GIS mapping."""
    features = []

    # 1. Incidents
    for inc in store.list_incidents():
        color_map = {
            TriageCategory.RED: "#ef4444",
            TriageCategory.YELLOW: "#f59e0b",
            TriageCategory.GREEN: "#10b981",
            TriageCategory.BLACK: "#1f2937",
            TriageCategory.PENDING: "#9ca3af"
        }
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [inc.longitude, inc.latitude]
            },
            "properties": {
                "entity_type": "INCIDENT",
                "id": inc.id,
                "location_name": inc.location_name,
                "triage_level": inc.triage_level.value,
                "urgency_score": inc.urgency_score,
                "survivor_count": inc.survivor_count,
                "trapped_count": inc.trapped_count,
                "hazards": inc.hazards,
                "status": inc.status.value,
                "assigned_unit_id": inc.assigned_unit_id,
                "marker_color": color_map.get(inc.triage_level, "#3b82f6")
            }
        })

    # 2. Rescue Units
    for unit in store.list_units():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [unit.longitude, unit.latitude]
            },
            "properties": {
                "entity_type": "RESCUE_UNIT",
                "id": unit.id,
                "name": unit.name,
                "unit_type": unit.unit_type.value,
                "status": unit.status.value,
                "callsign": unit.contact_callsign,
                "marker_color": "#38bdf8"
            }
        })

    # 3. Evacuation Safe Zones
    for zone in store.list_evac_zones():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [zone.longitude, zone.latitude]
            },
            "properties": {
                "entity_type": "EVAC_ZONE",
                "id": zone.id,
                "name": zone.name,
                "capacity": zone.capacity,
                "occupancy": zone.current_occupancy,
                "marker_color": "#22c55e"
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.post("/api/simulation/seed")
def seed_simulation():
    from simulator.seed_disaster import load_mock_scenario
    count = load_mock_scenario(store)
    return {"message": "Disaster scenario loaded", "incidents_created": count}

@app.post("/api/simulation/reset")
def reset_simulation():
    store.clear()
    return {"message": "System state reset"}

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "AegisOps API is running. Static frontend not yet compiled."}
