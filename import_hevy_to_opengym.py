#!/usr/bin/env python3
"""
Import all Hevy routines directly into self-hosted OpenGym.
"""

import sys
import os
import json
import uuid
import subprocess
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEVY_MAP_FILE = os.path.join(BASE_DIR, "hevy_id_map.json")
CATALOG_FILE = os.path.join(BASE_DIR, "opengym_catalog.json")
CONFIG_FILE = os.path.join(BASE_DIR, "opengym_config.json")
TOKEN_FILE = os.path.join(BASE_DIR, "opengym_token.txt")

def get_keychain_hevy_key():
    cmd = ["security", "find-generic-password", "-s", "Hevy API", "-a", "theitguru", "-w"]
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
    except Exception as e:
        print(f"Error fetching Hevy API key from Keychain: {e}")
        sys.exit(1)

def get_opengym_auth():
    url = os.environ.get("OPENGYM_URL", "http://localhost:8080")
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
                url = cfg.get("url", url).rstrip("/")
        except Exception:
            pass
    token = None
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                token = f.read().strip()
        except Exception:
            pass
    return url, token

def fetch_hevy_routines(hevy_key):
    routines = []
    page = 1
    while True:
        url = f"https://api.hevyapp.com/v1/routines?page={page}&pageSize=10"
        req = urllib.request.Request(url, headers={"api-key": hevy_key})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                batch = data.get("routines", [])
                if not batch:
                    break
                routines.extend(batch)
                page_count = data.get("page_count", 1)
                if page >= page_count:
                    break
                page += 1
        except Exception as e:
            print(f"Error fetching routines from Hevy: {e}")
            break
    return routines

def main():
    print("=" * 60)
    print("      HEVY -> OPENGYM ROUTINES MIGRATION ENGINE")
    print("=" * 60)

    # 1. OpenGym Auth check
    og_url, og_token = get_opengym_auth()
    if not og_token:
        print(f"No OpenGym session token found.")
        print(f"Please link OpenGym first by running:")
        print(f"  python3 opengym_sync.py --pair <CODE>")
        print(f"  (Get code from OpenGym: Settings -> Pair the mobile app)")
        sys.exit(1)

    # 2. Fetch Hevy routines
    print(f"\n1. Fetching routines from Hevy API...")
    hevy_key = get_keychain_hevy_key()
    hevy_routines = fetch_hevy_routines(hevy_key)
    print(f"✔ Found {len(hevy_routines)} routines in Hevy:")
    for r in hevy_routines:
        print(f"   • {r.get('title')} ({len(r.get('exercises', []))} exercises)")

    # 3. Load mapping tables
    hevy_map = {}
    if os.path.exists(HEVY_MAP_FILE):
        with open(HEVY_MAP_FILE) as f:
            hevy_map = json.load(f)

    catalog = {}
    if os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE) as f:
            catalog = json.load(f)

    # 4. Fetch current OpenGym state
    print(f"\n2. Fetching current OpenGym profile from {og_url}...")
    req = urllib.request.Request(f"{og_url}/api/data", headers={"Authorization": f"Bearer {og_token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            state = data.get("state") or {}
            rev = data.get("rev", 0)
    except Exception as e:
        print(f"Error connecting to OpenGym at {og_url}: {e}")
        sys.exit(1)

    state.setdefault("routines", [])
    state.setdefault("customEx", [])
    state.setdefault("unit", "lb")

    existing_routines = state.get("routines", [])
    existing_custom = state.get("customEx", [])

    print(f"✔ Current OpenGym profile has {len(existing_routines)} routines and {len(existing_custom)} custom exercises.")

    # 5. Build and convert routines
    print(f"\n3. Converting Hevy routines into OpenGym format...")
    added_count = 0
    updated_count = 0

    for hr in hevy_routines:
        title = hr.get("title", "Imported Routine").strip()
        exercises = []

        for he in hr.get("exercises", []):
            tpl_id = he.get("exercise_template_id")
            ex_title = he.get("title", "Exercise").strip()

            # Map template ID to OpenGym catalogue ID
            target_id = hevy_map.get(tpl_id)

            if not target_id:
                # Find or create custom exercise in OpenGym
                custom_match = next((c for c in existing_custom if (c.get("n") or c.get("name", "")).lower() == ex_title.lower()), None)
                if custom_match:
                    target_id = custom_match["id"]
                else:
                    target_id = "c_" + uuid.uuid4().hex[:8]
                    new_custom = {
                        "id": target_id,
                        "n": ex_title,
                        "name": ex_title,
                        "custom": True,
                        "bp": "upper legs", # generic fallback
                        "_ts": int(time.time() * 1000)
                    }
                    existing_custom.append(new_custom)

            # Build sets configuration
            sets = he.get("sets", [])
            work_sets = [s for s in sets if s.get("type") != "warmup"]
            sample_set = work_sets[0] if work_sets else (sets[0] if sets else {})

            reps = sample_set.get("reps") or 10
            weight_kg = sample_set.get("weight_kg")
            weight_lb = round(weight_kg * 2.20462) if weight_kg else 50
            num_sets = max(1, len(work_sets) if work_sets else len(sets))

            exercises.append({
                "id": target_id,
                "sets": num_sets,
                "reps": reps,
                "weight": weight_lb,
                "mode": "reps",
                "r": reps,
                "w": weight_lb
            })

        # Check if routine already exists in OpenGym
        existing_r = next((r for r in existing_routines if r.get("name", "").lower() == title.lower()), None)
        if existing_r:
            existing_r["ex"] = exercises
            updated_count += 1
            print(f"   ⚡ Updated existing routine: '{title}' ({len(exercises)} exercises)")
        else:
            new_r = {
                "id": uuid.uuid4().hex[:12],
                "name": title,
                "emoji": "figureStrength",
                "ex": exercises
            }
            existing_routines.append(new_r)
            added_count += 1
            print(f"   ➕ Added new routine: '{title}' ({len(exercises)} exercises)")

    # 6. Save updated state back to OpenGym
    print(f"\n4. Uploading updated routines to OpenGym...")
    state["routines"] = existing_routines
    state["customEx"] = existing_custom

    payload = json.dumps({"state": state, "baseRev": rev}).encode("utf-8")
    save_req = urllib.request.Request(
        f"{og_url}/api/data",
        data=payload,
        headers={
            "Authorization": f"Bearer {og_token}",
            "Content-Type": "application/json"
        },
        method="PUT"
    )

    try:
        with urllib.request.urlopen(save_req) as resp:
            print(f"\n🎉 SUCCESS! All routines populated into OpenGym!")
            print(f"   • {added_count} new routines added")
            print(f"   • {updated_count} routines updated")
            print(f"\nOpen {url} to view your full routine library in OpenGym.")
    except urllib.error.HTTPError as e:
        print(f"Error saving to OpenGym ({e.code}): {e.read().decode()}")
    except Exception as e:
        print(f"Error saving to OpenGym: {e}")

if __name__ == "__main__":
    main()
