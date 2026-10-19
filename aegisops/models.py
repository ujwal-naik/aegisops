from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time
import uuid

class TriageCategory(str, Enum):
    RED = "RED"         # Immediate: Life-threatening, requires immediate intervention
    YELLOW = "YELLOW"   # Delayed: Serious condition, stable for 1-2 hours
    GREEN = "GREEN"     # Minor: Walking wounded, superficial injuries
    BLACK = "BLACK"     # Deceased / Expectant: Palliative care / fatal trauma
    PENDING = "PENDING" # Raw feed awaiting automated or human triage

class IncidentStatus(str, Enum):
    REPORTED = "REPORTED"
    VERIFIED = "VERIFIED"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    RESOLVED = "RESOLVED"
    DUPLICATE = "DUPLICATE"

class UnitType(str, Enum):
    AMBULANCE = "AMBULANCE"
    WATER_RESCUE = "WATER_RESCUE"
    HEAVY_SAR = "HEAVY_SAR"
    AERIAL_DRONE = "AERIAL_DRONE"
    MEDICAL_STRIKE = "MEDICAL_STRIKE"
    GENERAL_EVAC = "GENERAL_EVAC"

class UnitStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"
    ON_SCENE = "ON_SCENE"
    RETURNING = "RETURNING"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"

class Incident(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    latitude: float
    longitude: float
    location_name: str
    raw_report: str
    triage_level: TriageCategory = TriageCategory.PENDING
    urgency_score: float = 0.0  # Normalized 0 - 100
    survivor_count: int = 1
    trapped_count: int = 0
    hazards: List[str] = Field(default_factory=list)
    required_unit_type: UnitType = UnitType.GENERAL_EVAC
    status: IncidentStatus = IncidentStatus.REPORTED
    assigned_unit_id: Optional[str] = None
    duplicate_of: Optional[str] = None
    duplicate_reports: List[str] = Field(default_factory=list)
    origin_node_id: str = "node-alpha"
    vector_clock: int = 1

class RescueUnit(BaseModel):
    id: str
    name: str
    unit_type: UnitType
    latitude: float
    longitude: float
    status: UnitStatus = UnitStatus.AVAILABLE
    current_incident_id: Optional[str] = None
    capacity: int = 4
    fuel_pct: int = 100
    speed_kmh: float = 40.0
    contact_callsign: str

class EvacuationZone(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    capacity: int
    current_occupancy: int = 0
    is_safe: bool = True
    notes: str = ""

class MeshNode(BaseModel):
    node_id: str
    node_name: str
    last_seen: float = Field(default_factory=time.time)
    hop_count: int = 0
    is_gateway: bool = False
    pending_sync_count: int = 0

class SyncPayload(BaseModel):
    sender_node_id: str
    sent_at: float = Field(default_factory=time.time)
    incidents: List[Incident] = Field(default_factory=list)
    unit_updates: List[RescueUnit] = Field(default_factory=list)
