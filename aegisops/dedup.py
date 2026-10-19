import math
import re
from typing import Optional, List, Set
from aegisops.models import Incident, IncidentStatus

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two coordinates in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def tokenize(text: str) -> Set[str]:
    words = re.findall(r"\w{3,}", text.lower())
    stop_words = {"the", "and", "for", "with", "this", "that", "from", "are", "have", "been"}
    return set(w for w in words if w not in stop_words)

def jaccard_similarity(text1: str, text2: str) -> float:
    set1 = tokenize(text1)
    set2 = tokenize(text2)
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

class DeduplicationEngine:
    """
    Intelligent incident deduplication engine combining geospatial proximity
    and semantic description overlap to prevent emergency dispatcher fatigue.
    """
    SPATIAL_RADIUS_METERS = 200.0  # 200 meter radius for duplicate clustering
    TEMPORAL_WINDOW_SECONDS = 7200.0  # 2 hours
    SEMANTIC_THRESHOLD = 0.35  # Jaccard threshold

    @classmethod
    def check_duplicate(cls, new_incident: Incident, existing_incidents: List[Incident]) -> Optional[Incident]:
        """
        Checks if the new incident is a duplicate of an existing active incident.
        Returns the existing master Incident if duplicate, else None.
        """
        for candidate in existing_incidents:
            if candidate.status in (IncidentStatus.RESOLVED, IncidentStatus.DUPLICATE):
                continue

            dist = haversine_distance_meters(
                new_incident.latitude, new_incident.longitude,
                candidate.latitude, candidate.longitude
            )

            time_diff = abs(new_incident.timestamp - candidate.timestamp)

            if dist <= cls.SPATIAL_RADIUS_METERS and time_diff <= cls.TEMPORAL_WINDOW_SECONDS:
                similarity = jaccard_similarity(new_incident.raw_report, candidate.raw_report)
                # Strong geographic proximity with moderate text similarity OR exact same address
                if similarity >= cls.SEMANTIC_THRESHOLD or dist < 50.0:
                    return candidate

        return None

    @classmethod
    def merge_into_master(cls, master: Incident, duplicate: Incident) -> Incident:
        """
        Merges duplicate details into master incident without losing critical data.
        """
        master.survivor_count = max(master.survivor_count, duplicate.survivor_count)
        master.trapped_count = max(master.trapped_count, duplicate.trapped_count)

        # Merge hazards
        combined_hazards = list(set(master.hazards + duplicate.hazards))
        master.hazards = combined_hazards

        # Boost urgency if multiple citizens report the same critical event
        master.urgency_score = min(master.urgency_score + 3.0, 100.0)

        # Record secondary report
        snippet = f"[{duplicate.origin_node_id}] {duplicate.raw_report}"
        if snippet not in master.duplicate_reports:
            master.duplicate_reports.append(snippet)

        duplicate.status = IncidentStatus.DUPLICATE
        duplicate.duplicate_of = master.id
        return master
