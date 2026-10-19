from typing import List, Dict, Optional, Tuple
from aegisops.models import Incident, RescueUnit, IncidentStatus, UnitStatus, TriageCategory, UnitType
from aegisops.dedup import haversine_distance_meters

class DispatchOptimizer:
    """
    Automated ICS-204 Resource Allocation Engine.
    Matches critical triage incidents with nearest capable rescue units.
    """

    @classmethod
    def find_best_unit(cls, incident: Incident, units: List[RescueUnit]) -> Optional[Tuple[RescueUnit, float, float]]:
        """
        Finds the single best available unit for an incident.
        Returns: (best_unit, distance_km, eta_minutes) or None
        """
        available_units = [u for u in units if u.status == UnitStatus.AVAILABLE and u.fuel_pct > 15]
        if not available_units:
            return None

        # Filter by unit capability match
        compatible = [u for u in available_units if u.unit_type == incident.required_unit_type]
        if not compatible:
            # Fallback to general rescue or ambulance if specific type not available
            compatible = [u for u in available_units if u.unit_type in (UnitType.AMBULANCE, UnitType.GENERAL_EVAC)]
            if not compatible:
                compatible = available_units

        best_unit = None
        min_eta = float("inf")
        best_dist_km = 0.0

        for unit in compatible:
            dist_m = haversine_distance_meters(incident.latitude, incident.longitude, unit.latitude, unit.longitude)
            dist_km = dist_m / 1000.0
            speed_kmh = max(unit.speed_kmh, 10.0)
            eta_minutes = (dist_km / speed_kmh) * 60.0

            if eta_minutes < min_eta:
                min_eta = eta_minutes
                best_unit = unit
                best_dist_km = dist_km

        if best_unit:
            return best_unit, round(best_dist_km, 2), round(min_eta, 1)
        return None

    @classmethod
    def auto_dispatch_all(cls, incidents: List[Incident], units: List[RescueUnit]) -> List[Dict]:
        """
        Batch dispatches available units to highest-priority pending incidents.
        Priority: RED (Immediate) -> YELLOW (Delayed) -> GREEN (Minor)
        """
        dispatches = []
        # Sort incidents: highest urgency first
        pending = [
            inc for inc in incidents
            if inc.status in (IncidentStatus.REPORTED, IncidentStatus.VERIFIED)
            and inc.assigned_unit_id is None
        ]
        pending.sort(key=lambda x: (x.triage_level == TriageCategory.RED, x.urgency_score), reverse=True)

        assigned_unit_ids = set()

        for incident in pending:
            # Filter out units already assigned in this batch
            current_available = [u for u in units if u.id not in assigned_unit_ids]
            match = cls.find_best_unit(incident, current_available)
            if match:
                unit, dist_km, eta_min = match
                assigned_unit_ids.add(unit.id)

                incident.status = IncidentStatus.DISPATCHED
                incident.assigned_unit_id = unit.id

                unit.status = UnitStatus.DISPATCHED
                unit.current_incident_id = incident.id

                dispatches.append({
                    "incident_id": incident.id,
                    "incident_name": incident.location_name,
                    "triage_level": incident.triage_level.value,
                    "unit_id": unit.id,
                    "unit_name": unit.name,
                    "unit_type": unit.unit_type.value,
                    "distance_km": dist_km,
                    "eta_minutes": eta_min
                })

        return dispatches
