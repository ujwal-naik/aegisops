import uvicorn
import argparse
import sys
import os
from aegisops.database import store
from simulator.seed_disaster import load_mock_scenario

def main():
    parser = argparse.ArgumentParser(description="AegisOps Incident Command Engine")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--no-seed", action="store_true", help="Do not preload mock disaster scenario")
    args = parser.parse_args()

    # Preload mock scenario if store is empty and not disabled
    if not args.no_seed and len(store.incidents) == 0:
        print("[INIT] Preloading 'Operation CoastalShield' disaster scenario into local store...")
        count = load_mock_scenario(store)
        print(f"[INIT] Loaded {count} disaster incidents and tactical rescue units.")

    print(f"\n=======================================================")
    print(f"  AEGISOPS DISASTER COORDINATION ENGINE ACTIVE")
    print(f"  Tactical Web Dashboard: http://{args.host}:{args.port}")
    print(f"  Interactive OpenAPI:    http://{args.host}:{args.port}/docs")
    print(f"=======================================================\n")

    uvicorn.run("aegisops.api:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()
