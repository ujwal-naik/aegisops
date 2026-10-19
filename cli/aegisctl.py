import argparse
import sys
import json
import requests

DEFAULT_API = "http://127.0.0.1:8000"

def get_status(base_url: str):
    try:
        r = requests.get(f"{base_url}/api/status", timeout=5)
        data = r.json()
        print("\n==========================================")
        print("  AEGISOPS TACTICAL INCIDENT COMMAND")
        print("==========================================")
        print(f"Node ID:          {data.get('node_id')}")
        print(f"System State:     {data.get('status')}")
        ts = data.get("triage_summary", {})
        print(f"Active Incidents: {ts.get('TOTAL_ACTIVE', 0)} (Resolved: {ts.get('RESOLVED', 0)})")
        print(f"  - RED (Immediate):   {ts.get('RED', 0)}")
        print(f"  - YELLOW (Delayed):  {ts.get('YELLOW', 0)}")
        print(f"  - GREEN (Minor):     {ts.get('GREEN', 0)}")
        fleet = data.get("fleet", {})
        print(f"Fleet Status:     {fleet.get('available_units', 0)}/{fleet.get('total_units', 0)} Units Ready")
        print(f"Mesh Nodes Seen:  {data.get('mesh_nodes_connected', 0)}")
        print("==========================================\n")
    except Exception as e:
        print(f"[ERROR] Failed to connect to AegisOps daemon at {base_url}: {e}")

def list_incidents(base_url: str, triage: str):
    try:
        params = {}
        if triage:
            params["triage"] = triage.upper()
        r = requests.get(f"{base_url}/api/incidents", params=params, timeout=5)
        data = r.json()
        incidents = data.get("incidents", [])
        print(f"\nFound {len(incidents)} active incidents:")
        print(f"{'ID':<10} {'TRIAGE':<8} {'URG%':<6} {'STATUS':<12} {'LOCATION':<28} {'HAZARDS'}")
        print("-" * 75)
        for inc in incidents:
            hazards_str = ",".join(inc.get("hazards", []))
            print(f"{inc['id']:<10} {inc['triage_level']:<8} {inc['urgency_score']:<6.1f} {inc['status']:<12} {inc['location_name'][:26]:<28} {hazards_str}")
        print()
    except Exception as e:
        print(f"[ERROR] {e}")

def submit_report(base_url: str, text: str, location: str, lat: float, lon: float):
    try:
        payload = {
            "location_name": location,
            "latitude": lat,
            "longitude": lon,
            "raw_report": text,
            "origin_node_id": "aegisctl-cli"
        }
        r = requests.post(f"{base_url}/api/incidents", json=payload, timeout=5)
        res = r.json()
        print("\n[SUCCESS] Field report submitted successfully!")
        print(f"Result Status:   {res.get('status')}")
        inc = res.get("incident", {})
        print(f"Incident ID:     {inc.get('id')}")
        print(f"Assessed Triage: {inc.get('triage_level')} (Urgency: {inc.get('urgency_score')}%)")
        print(f"Required Unit:   {inc.get('required_unit_type')}")
        print(f"Survivors:       {inc.get('survivor_count')} (Trapped: {inc.get('trapped_count')})")
        print()
    except Exception as e:
        print(f"[ERROR] {e}")

def run_dispatch(base_url: str):
    try:
        r = requests.post(f"{base_url}/api/dispatch/auto", timeout=5)
        res = r.json()
        dispatches = res.get("assignments", [])
        print(f"\n[ICS DISPATCH] Created {len(dispatches)} automated mission dispatches:")
        for d in dispatches:
            print(f" -> Assigned {d['unit_name']} ({d['unit_type']}) to Incident [{d['triage_level']}] {d['incident_name']} (ETA: {d['eta_minutes']} min, {d['distance_km']} km)")
        print()
    except Exception as e:
        print(f"[ERROR] {e}")

def seed_demo(base_url: str):
    try:
        r = requests.post(f"{base_url}/api/simulation/seed", timeout=5)
        res = r.json()
        print(f"[SUCCESS] {res.get('message')} ({res.get('incidents_created')} incidents loaded)")
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    parser = argparse.ArgumentParser(description="AegisOps Tactical Field CLI")
    parser.add_argument("--url", default=DEFAULT_API, help="Base URL of AegisOps server")
    subparsers = parser.add_subparsers(dest="command")

    # Status
    subparsers.add_parser("status", help="Get tactical status overview")

    # List
    list_p = subparsers.add_parser("list", help="List active incidents")
    list_p.add_argument("--triage", choices=["RED", "YELLOW", "GREEN", "ALL"], default="ALL")

    # Report
    rep_p = subparsers.add_parser("report", help="Submit new emergency witness/radio report")
    rep_p.add_argument("text", help="Raw transmission text")
    rep_p.add_argument("--location", required=True, help="Location name or landmark")
    rep_p.add_argument("--lat", type=float, default=12.875, help="Latitude")
    rep_p.add_argument("--lon", type=float, default=74.852, help="Longitude")

    # Dispatch
    subparsers.add_parser("dispatch", help="Trigger automated ICS resource dispatch")

    # Seed
    subparsers.add_parser("seed", help="Seed realistic disaster simulation scenario")

    args = parser.parse_args()

    if args.command == "status":
        get_status(args.url)
    elif args.command == "list":
        list_incidents(args.url, args.triage)
    elif args.command == "report":
        submit_report(args.url, args.text, args.location, args.lat, args.lon)
    elif args.command == "dispatch":
        run_dispatch(args.url)
    elif args.command == "seed":
        seed_demo(args.url)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
