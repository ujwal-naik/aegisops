import json
import os
import threading
from typing import Dict, List, Optional
from aegisops.models import Incident, RescueUnit, EvacuationZone, MeshNode, TriageCategory, IncidentStatus, UnitStatus

DB_FILE = os.environ.get("AEGISOPS_DB", "aegisops_state.json")

class IncidentStore:
    """
    Lightweight, thread-safe in-memory store with periodic JSON state dump
    for rapid crash recovery in offline field environments.
    """
    def __init__(self, persistence_path: str = DB_FILE):
        self.persistence_path = persistence_path
        self._lock = threading.RLock()
        self.incidents: Dict[str, Incident] = {}
        self.rescue_units: Dict[str, RescueUnit] = {}
        self.evac_zones: Dict[str, EvacuationZone] = {}
        self.mesh_nodes: Dict[str, MeshNode] = {}
        self.node_id: str = "node-alpha"
        self.load_state()

    def add_incident(self, incident: Incident) -> Incident:
        with self._lock:
            self.incidents[incident.id] = incident
            self.persist_state()
            return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        with self._lock:
            return self.incidents.get(incident_id)

    def list_incidents(self, include_duplicates: bool = False) -> List[Incident]:
        with self._lock:
            results = list(self.incidents.values())
            if not include_duplicates:
                results = [inc for inc in results if inc.status != IncidentStatus.DUPLICATE]
            return sorted(results, key=lambda x: (x.urgency_score, -x.timestamp), reverse=True)

    def update_incident(self, incident: Incident) -> Incident:
        with self._lock:
            incident.vector_clock += 1
            self.incidents[incident.id] = incident
            self.persist_state()
            return incident

    def add_unit(self, unit: RescueUnit) -> RescueUnit:
        with self._lock:
            self.rescue_units[unit.id] = unit
            self.persist_state()
            return unit

    def get_unit(self, unit_id: str) -> Optional[RescueUnit]:
        with self._lock:
            return self.rescue_units.get(unit_id)

    def list_units(self) -> List[RescueUnit]:
        with self._lock:
            return list(self.rescue_units.values())

    def update_unit(self, unit: RescueUnit) -> RescueUnit:
        with self._lock:
            self.rescue_units[unit.id] = unit
            self.persist_state()
            return unit

    def add_evac_zone(self, zone: EvacuationZone):
        with self._lock:
            self.evac_zones[zone.id] = zone
            self.persist_state()

    def list_evac_zones(self) -> List[EvacuationZone]:
        with self._lock:
            return list(self.evac_zones.values())

    def register_mesh_node(self, node: MeshNode):
        with self._lock:
            self.mesh_nodes[node.node_id] = node

    def list_mesh_nodes(self) -> List[MeshNode]:
        with self._lock:
            return list(self.mesh_nodes.values())

    def get_triage_summary(self) -> Dict[str, int]:
        with self._lock:
            summary = {
                "RED": 0,
                "YELLOW": 0,
                "GREEN": 0,
                "BLACK": 0,
                "PENDING": 0,
                "TOTAL_ACTIVE": 0,
                "RESOLVED": 0
            }
            for inc in self.incidents.values():
                if inc.status == IncidentStatus.DUPLICATE:
                    continue
                if inc.status == IncidentStatus.RESOLVED:
                    summary["RESOLVED"] += 1
                else:
                    summary["TOTAL_ACTIVE"] += 1
                    triage_key = inc.triage_level.value
                    if triage_key in summary:
                        summary[triage_key] += 1
            return summary

    def clear(self):
        with self._lock:
            self.incidents.clear()
            self.rescue_units.clear()
            self.evac_zones.clear()
            self.mesh_nodes.clear()
            if os.path.exists(self.persistence_path):
                try:
                    os.remove(self.persistence_path)
                except OSError:
                    pass

    def persist_state(self):
        with self._lock:
            try:
                data = {
                    "incidents": [inc.model_dump() for inc in self.incidents.values()],
                    "units": [u.model_dump() for u in self.rescue_units.values()],
                    "evac_zones": [z.model_dump() for z in self.evac_zones.values()],
                    "mesh_nodes": [n.model_dump() for n in self.mesh_nodes.values()]
                }
                with open(self.persistence_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                pass  # Graceful fallback in read-only / restricted storage

    def load_state(self):
        with self._lock:
            if not os.path.exists(self.persistence_path):
                return
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for inc_raw in data.get("incidents", []):
                    inc = Incident(**inc_raw)
                    self.incidents[inc.id] = inc
                for u_raw in data.get("units", []):
                    u = RescueUnit(**u_raw)
                    self.rescue_units[u.id] = u
                for z_raw in data.get("evac_zones", []):
                    z = EvacuationZone(**z_raw)
                    self.evac_zones[z.id] = z
                for n_raw in data.get("mesh_nodes", []):
                    n = MeshNode(**n_raw)
                    self.mesh_nodes[n.node_id] = n
            except Exception:
                pass

# Global singleton
store = IncidentStore()
