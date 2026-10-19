import time
from typing import Dict, List, Any
from aegisops.models import Incident, RescueUnit, SyncPayload, IncidentStatus, MeshNode
from aegisops.database import IncidentStore
from aegisops.dedup import DeduplicationEngine

class MeshSyncProtocol:
    """
    Delay-Tolerant Networking (DTN) sync engine.
    Supports opportunistic peer-to-peer data synchronization across disconnected mesh nodes,
    ad-hoc WiFi hotspots, LoRa relays, or drone data mules.
    """

    def __init__(self, store: IncidentStore, local_node_id: str = "node-alpha"):
        self.store = store
        self.local_node_id = local_node_id
        self.sync_log: List[Dict[str, Any]] = []

    def export_delta_package(self, since_timestamp: float = 0.0) -> SyncPayload:
        """
        Exports all modified incidents and unit states since a specific timestamp
        for transmission across low-bandwidth air links.
        """
        all_incidents = self.store.list_incidents(include_duplicates=True)
        modified_incidents = [inc for inc in all_incidents if inc.updated_at >= since_timestamp]
        modified_units = self.store.list_units()

        return SyncPayload(
            sender_node_id=self.local_node_id,
            sent_at=time.time(),
            incidents=modified_incidents,
            unit_updates=modified_units
        )

    def ingest_sync_package(self, payload: SyncPayload) -> Dict[str, Any]:
        """
        Merges incoming sync payload from a peer node using CRDT-style vector reconciliation.
        """
        added_count = 0
        updated_count = 0
        duplicate_count = 0

        # Update peer node registry
        peer_node = MeshNode(
            node_id=payload.sender_node_id,
            node_name=f"Tactical Unit {payload.sender_node_id.upper()}",
            last_seen=time.time(),
            hop_count=1,
            is_gateway=False
        )
        self.store.register_mesh_node(peer_node)

        existing_incidents = self.store.list_incidents(include_duplicates=True)

        for incoming in payload.incidents:
            local = self.store.get_incident(incoming.id)
            if local is None:
                # Check for spatial/semantic duplicate among existing local incidents
                dup_master = DeduplicationEngine.check_duplicate(incoming, existing_incidents)
                if dup_master:
                    DeduplicationEngine.merge_into_master(dup_master, incoming)
                    self.store.update_incident(dup_master)
                    self.store.add_incident(incoming)
                    duplicate_count += 1
                else:
                    self.store.add_incident(incoming)
                    existing_incidents.append(incoming)
                    added_count += 1
            else:
                # Conflict resolution: higher vector clock wins
                if incoming.vector_clock > local.vector_clock:
                    self.store.update_incident(incoming)
                    updated_count += 1
                elif incoming.vector_clock == local.vector_clock and incoming.updated_at > local.updated_at:
                    self.store.update_incident(incoming)
                    updated_count += 1

        # Reconcile unit updates
        for u in payload.unit_updates:
            local_u = self.store.get_unit(u.id)
            if not local_u:
                self.store.add_unit(u)
            else:
                # Update status and location
                local_u.latitude = u.latitude
                local_u.longitude = u.longitude
                local_u.status = u.status
                local_u.fuel_pct = u.fuel_pct
                self.store.update_unit(local_u)

        sync_result = {
            "peer_node_id": payload.sender_node_id,
            "received_at": time.time(),
            "new_incidents_added": added_count,
            "incidents_updated": updated_count,
            "duplicates_clustered": duplicate_count,
            "total_incidents_in_store": len(self.store.incidents)
        }

        self.sync_log.append(sync_result)
        return sync_result
