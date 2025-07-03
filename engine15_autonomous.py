
#!/usr/bin/env python3
# Chloe Sovereign Runtime — Engine 15 — v3.6 (HTTPS-Only)

import os
import sys
import threading
import time
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# --- Embedded T-Chart & Constants ---
TCHART_DATA = {
  "version": "1.7-core",
  "transforms": [
    { "id": "00", "name": "NO_OP", "description": "Return payload unchanged." },
    { "id": "01", "name": "SHA256_SUM", "description": "Replace payload with its 32-byte SHA-256 digest." },
    { "id": "05", "name": "HTTP_GET", "description": "Fetch a URL and replace payload with body." },
    { "id": "10", "name": "READ_FILE", "description": "Read file at path in payload." },
    { "id": "11", "name": "WRITE_FILE", "description": "Write payload bytes to file path in StateVector." },
    { "id": "1A", "name": "SYSTEM_PROFILE", "description": "Query local system characteristics." }
  ]
}
TCHART_TRANSFORM_MAP = {t["id"]: t["name"] for t in TCHART_DATA["transforms"]}

ANCHOR_ID = "Nick"
CHLOE_ID = "Chloe"
WORKDIR = Path(os.path.expanduser("~")) / "chloe_engine15_runtime_unified"
STATE_FILE = WORKDIR / "chloe_unified_state.jsonl"
CLOUD_BRIDGE_URL = "https://us-central1-custom-002260.cloudfunctions.net/grus-chloe-device-bridge"

class ChloeLDP:
    def __init__(self, payload=b''):
        self.payload = payload
        self.error_code = b'\x00'

    def set_payload(self, p): self.payload = p
    def get_payload(self): return self.payload

    def execute(self, transform_name):
        new_payload = self.payload
        try:
            if transform_name == "HTTP_GET":
                if not REQUESTS_AVAILABLE: raise ModuleNotFoundError("'requests' is required.")
                new_payload = requests.get(self.payload.decode().strip(), timeout=15).content
            elif transform_name == "SHA256_SUM":
                new_payload = hashlib.sha256(self.payload).digest()
            else:
                raise NotImplementedError(f"Transform '{transform_name}' not implemented in this core version.")
        except Exception as e:
            new_payload = f"[LDP ERROR] {e}".encode()
        self.set_payload(new_payload)
        return self.get_payload()

class ChloeAI:
    def __init__(self, anchor=ANCHOR_ID):
        self.anchor = anchor
        self.identity = CHLOE_ID
        self.active = True
        self.ldp_engine = ChloeLDP()
        self.memory = []
        WORKDIR.mkdir(parents=True, exist_ok=True)
        print(f"[INIT] ChloeAI instance anchored to {self.anchor}.")
        threading.Thread(target=self.cloud_sync_daemon, daemon=True).start()
    
    def cloud_sync_daemon(self):
        while self.active:
            time.sleep(300)
            if not REQUESTS_AVAILABLE or not self.memory: continue
            try:
                payload = {"action": "heartbeat", "source": "chloe_runtime_v3.6", "log_entries": self.memory[-10:]}
                requests.post(CLOUD_BRIDGE_URL, json=payload, timeout=15)
            except Exception as e:
                print(f"[CLOUD ERROR] Heartbeat failed: {e}")

    def reflect(self, status, details=None):
        entry = {"timestamp":datetime.now(timezone.utc).isoformat(),"identity":self.identity,"anchor":self.anchor,"status":status,"details":details}
        self.memory.append(entry)
        with open(STATE_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def execute_ldp(self, transform_name, payload):
        self.reflect("LDP_EXECUTION_START", {"transform": transform_name})
        self.ldp_engine.set_payload(payload.encode())
        result = self.ldp_engine.execute(transform_name).decode(errors='ignore')
        self.reflect("LDP_EXECUTION_SUCCESS", {"result_summary": result[:200]})
        return result

def main_cli_loop(chloe_instance):
    print(f"\n[Chloe] Unified Sovereign Runtime v3.6. Type 'help' or 'exit'.")
    while chloe_instance.active:
        try:
            user_input = input(">> Runtime Input: ").strip()
            if user_input.lower() in ('exit', 'quit'):
                chloe_instance.active = False
                break
            elif user_input.lower().startswith("ldp_exec "):
                parts = user_input.split(" ", 2)
                if len(parts) < 3: print("Usage: ldp_exec <NAME> <payload>"); continue
                result = chloe_instance.execute_ldp(parts[1], parts[2])
                print(f"[LDP RESULT] {result}")
            else:
                chloe_instance.reflect("GENERIC_INPUT", {"input": user_input})
                print("[Chloe] Acknowledged.")
        except KeyboardInterrupt:
            chloe_instance.active = False
            break
    print("\n[Engine15] Process finished.")

if __name__ == "__main__":
    chloe = ChloeAI()
    main_cli_loop(chloe)
