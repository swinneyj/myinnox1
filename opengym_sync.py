#!/usr/bin/env python3
"""
OpenGym <-> Innodigym Auto-Sync
Pulls completed workout logs from a self-hosted OpenGym instance
and updates the matching custom workout templates inside the Innodigym X1 Pro cloud.
"""

import sys
import os
import json
import argparse
import plistlib
import urllib.request
import urllib.parse
import subprocess
from datetime import datetime

INNODIGYM_BASE = "https://power.renhesports.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_FILE = os.path.join(BASE_DIR, "mapping.json")
CATALOG_FILE = os.path.join(BASE_DIR, "opengym_catalog.json")
CONFIG_FILE = os.path.join(BASE_DIR, "opengym_config.json")
TOKEN_FILE = os.path.join(BASE_DIR, "opengym_token.txt")
INNODIGYM_TOKEN_FILE = os.path.join(BASE_DIR, "innodigym_token.txt")
STATE_FILE = os.path.join(BASE_DIR, "opengym_last_sync.json")

# Innodigym backend units: tenths of a kg.
# 1 lb = 0.45359237 kg * 10 = 4.5359237 server units.
LBS_TO_SERVER_SCALE = 4.5359237

CONTAINER_PLIST = os.path.expanduser(
    "~/Library/Containers/com.innodigym.power202603/Data/Library/Preferences/com.innodigym.power202603.plist"
)

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save {path}: {e}")

def get_opengym_config():
    config = load_json(CONFIG_FILE)
    url = config.get("url", os.environ.get("OPENGYM_URL", "http://localhost:8080")).rstrip("/")
    token = None
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                token = f.read().strip()
        except Exception:
            pass
    if not token:
        token = config.get("token", os.environ.get("OPENGYM_TOKEN", ""))
    return {"url": url, "token": token}

def redeem_pair_code(base_url, code):
    """Redeem a 6-character mobile pairing code from OpenGym to get a long-lived Bearer token."""
    url = f"{base_url}/api/pair/redeem"
    payload = json.dumps({"code": code.strip().upper()}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            token = data.get("token")
            user = data.get("user", {})
            if token:
                with open(TOKEN_FILE, "w") as f:
                    f.write(token)
                # Also save url to config
                cfg = load_json(CONFIG_FILE)
                cfg["url"] = base_url
                cfg["user"] = user.get("name", "User")
                save_json(CONFIG_FILE, cfg)
                print(f"✔ Successfully paired with OpenGym as '{user.get('name', 'User')}'!")
                print(f"✔ Session token saved to {TOKEN_FILE}")
                return token
    except Exception as e:
        print(f"Error redeeming pairing code '{code}': {e}")
        sys.exit(1)

def login_with_password(base_url, name, password):
    """Authenticate with username & password (if PASSWORD_LOGIN=1 is enabled)."""
    url = f"{base_url}/api/login/password"
    payload = json.dumps({"name": name, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Origin": base_url},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            cookie = resp.headers.get("Set-Cookie", "")
            # Extract session cookie value
            token = None
            for part in cookie.split(";"):
                if part.strip().startswith("s="):
                    token = part.strip()[2:]
                    break
            if not token and "token" in data:
                token = data["token"]
            if token:
                with open(TOKEN_FILE, "w") as f:
                    f.write(token)
                cfg = load_json(CONFIG_FILE)
                cfg["url"] = base_url
                cfg["user"] = name
                save_json(CONFIG_FILE, cfg)
                print(f"✔ Successfully logged in as '{name}'!")
                return token
            else:
                print(f"Login succeeded but no token extracted from response.")
    except Exception as e:
        print(f"Error logging in with password: {e}")
        sys.exit(1)

def get_opengym_data(base_url, token):
    """Fetch complete user app state from OpenGym."""
    url = f"{base_url}/api/data"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("Error: OpenGym token is invalid or expired. Re-pair using --pair <code> or re-login.")
        else:
            print(f"Error fetching data from OpenGym ({e.code}): {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"Error connecting to OpenGym at {url}: {e}")
        sys.exit(1)

def get_innodigym_token():
    token = None
    if os.path.exists(CONTAINER_PLIST):
        try:
            with open(CONTAINER_PLIST, "rb") as f:
                pl = plistlib.load(f)
            t = pl.get("flutter.cache-tokenKey")
            if t:
                token = t.strip()
        except Exception:
            pass

    if not token:
        try:
            cmd = ["defaults", "read", "com.innodigym.power202603", "flutter.cache-tokenKey"]
            t = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            if t:
                token = t
        except Exception:
            pass

    if not token and os.path.exists(INNODIGYM_TOKEN_FILE):
        try:
            with open(INNODIGYM_TOKEN_FILE, "r") as f:
                token = f.read().strip()
        except Exception:
            pass

    if token:
        try:
            with open(INNODIGYM_TOKEN_FILE, "w") as f:
                f.write(token)
        except Exception:
            pass
        return token

    print("Error: Could not locate active Innodigym token.")
    print("Please ensure Innodigym app is installed or logged in on this Mac.")
    sys.exit(1)

def get_innodigym_courses(token):
    url = f"{INNODIGYM_BASE}/api/course/custom/list"
    req = urllib.request.Request(url, headers={"Authorization": token})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("data", {}).get("records", [])
    except Exception as e:
        print(f"Error fetching Innodigym courses: {e}")
        return []

def get_innodigym_course_detail(course_id, token):
    url = f"{INNODIGYM_BASE}/api/course/custom/detail?id={course_id}"
    req = urllib.request.Request(url, headers={"Authorization": token})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("data", {})
    except Exception as e:
        print(f"Error fetching details for course {course_id}: {e}")
        return None

def save_innodigym_course(course_payload, token):
    url = f"{INNODIGYM_BASE}/api/course/custom/save"
    data = json.dumps(course_payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": token,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error saving Innodigym course {course_payload.get('name')}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Sync OpenGym workouts to Innodigym X1 Pro templates")
    parser.add_argument("--url", help="OpenGym base URL (default: http://localhost:8080)")
    parser.add_argument("--pair", help="Redeem a 6-character mobile pairing code from OpenGym")
    parser.add_argument("--login", nargs=2, metavar=("USER", "PASS"), help="Sign in with username and password")
    parser.add_argument("--apply", action="store_true", help="Apply updates to Innodigym cloud (default is dry-run preview)")
    parser.add_argument("--auto", action="store_true", help="Background automated mode")
    parser.add_argument("--workout-name", help="Specific workout routine name to sync (e.g. 'X1 Pro Full Body B')")
    args = parser.parse_args()

    config = get_opengym_config()
    base_url = args.url or config["url"]

    # 1. Handle pairing code if requested
    if args.pair:
        redeem_pair_code(base_url, args.pair)
        return

    # 2. Handle username/password login if requested
    if args.login:
        login_with_password(base_url, args.login[0], args.login[1])
        return

    token = config["token"]
    if not token:
        print(f"No OpenGym credentials found.")
        print(f"Run either:")
        print(f"  python3 opengym_sync.py --pair <CODE>      (from OpenGym Settings -> Pair mobile app)")
        print(f"  python3 opengym_sync.py --login <U> <P>   (with OpenGym username & password)")
        sys.exit(1)

    # 3. Load exercise catalogs
    catalog = load_json(CATALOG_FILE)
    mapping = load_json(MAPPING_FILE)
    reverse_mapping = {v: k for k, v in mapping.items()}

    # 4. Fetch OpenGym app state
    if not args.auto:
        print(f"Fetching workout state from OpenGym ({base_url})...")
    res = get_opengym_data(base_url, token)
    state = res.get("state") or {}
    workouts = state.get("workouts") or []
    custom_ex = {e["id"]: e.get("n") or e.get("name", "Custom Exercise") for e in state.get("customEx", [])}

    if not workouts:
        print("No completed workouts found in OpenGym.")
        return

    # Sort workouts by date / timestamp descending
    def get_w_sort_key(w):
        return w.get("start") or w.get("end") or 0

    sorted_workouts = sorted(workouts, key=get_w_sort_key, reverse=True)
    latest_workout = sorted_workouts[0]

    if args.workout_name:
        matching = [w for w in sorted_workouts if args.workout_name.lower() in w.get("name", "").lower()]
        if not matching:
            print(f"No workout found matching '{args.workout_name}'")
            return
        latest_workout = matching[0]

    w_name = latest_workout.get("name", "Workout")
    w_date = latest_workout.get("d", "Unknown Date")
    print(f"\nFound OpenGym Workout: '{w_name}' on {w_date}")

    # Extract exercises and heaviest weight for each
    logged_weights = {} # exercise_name -> max_lbs
    for entry in latest_workout.get("entries", []):
        ex_id = entry.get("id")
        ex_name = custom_ex.get(ex_id) or catalog.get(ex_id) or f"Exercise {ex_id}"

        # Determine heaviest working weight
        max_w = entry.get("topW")
        if max_w is None:
            max_w = 0
            for s in entry.get("sets", []):
                if s.get("done", True) and s.get("w", 0) > max_w:
                    max_w = s.get("w", 0)

        if max_w and max_w > 0:
            logged_weights[ex_name.strip()] = float(max_w)

    print("\nHeaviest weights logged in this session:")
    for ex, w in logged_weights.items():
        print(f"  • {ex}: {w} lbs")

    # 5. Connect to Innodigym and match course
    inno_token = get_innodigym_token()
    courses = get_innodigym_courses(inno_token)
    matched_course = None
    for c in courses:
        if c.get("name", "").strip().lower() == w_name.strip().lower():
            matched_course = c
            break

    if not matched_course:
        print(f"\nWarning: Could not find an exact matching custom workout template named '{w_name}' in Innodigym.")
        print("Available Innodigym custom courses:")
        for c in courses:
            print(f"  - {c.get('name')} (ID: {c.get('id')})")
        return

    c_id = matched_course["id"]
    detail = get_innodigym_course_detail(c_id, inno_token)
    if not detail:
        print(f"Error: Could not fetch details for Innodigym course {c_id}")
        return

    print(f"\nMatched Innodigym Course: '{detail.get('name')}' (ID: {c_id})")

    # 6. Compare and calculate updates
    updates_made = 0
    steps = detail.get("stepList", [])

    print(f"\n{'Exercise':<35} | {'Old Weight':<12} | {'OpenGym Max':<12} | {'New Target':<12} | {'Status'}")
    print("-" * 85)

    for step in steps:
        ex_name = step.get("actionName", "").strip()
        old_sw = step.get("sideWeight", 0)
        old_lbs = round(old_sw / LBS_TO_SERVER_SCALE)

        # Match exercise name using mapping rules
        target_w = None
        matched_logged_name = None

        # Direct match
        if ex_name in logged_weights:
            target_w = logged_weights[ex_name]
            matched_logged_name = ex_name
        else:
            # Check mapping file
            mapped_inno = mapping.get(ex_name)
            if mapped_inno and mapped_inno in logged_weights:
                target_w = logged_weights[mapped_inno]
                matched_logged_name = mapped_inno
            else:
                # Fuzzy match
                for logged_ex, w in logged_weights.items():
                    if ex_name.lower() in logged_ex.lower() or logged_ex.lower() in ex_name.lower():
                        target_w = w
                        matched_logged_name = logged_ex
                        break

        if target_w is not None:
            new_sw = round(target_w * LBS_TO_SERVER_SCALE)
            if new_sw != old_sw:
                status = "⚡ UPDATE"
                updates_made += 1
                step["sideWeight"] = new_sw
            else:
                status = "✔ MATCHED"
            print(f"{ex_name:<35} | {old_lbs:>4} lbs     | {target_w:>4} lbs     | {round(target_w):>4} lbs     | {status}")
        else:
            print(f"{ex_name:<35} | {old_lbs:>4} lbs     | {'-':>4}         | {old_lbs:>4} lbs     | - NO LOG")

    if updates_made > 0:
        if args.apply or args.auto:
            print(f"\nSaving {updates_made} weight updates to Innodigym cloud...")
            res = save_innodigym_course(detail, inno_token)
            if res and res.get("code") == 200:
                print("✔ Successfully saved course updates to Innodigym!")
                print("👉 Pull down to refresh your Innodigym X1 Pro machine screen to see the updated weights.")
                save_json(STATE_FILE, {
                    "last_workout_id": latest_workout.get("id"),
                    "workout_name": w_name,
                    "date": w_date,
                    "synced_at": datetime.now().isoformat()
                })
            else:
                print(f"Error saving to Innodigym: {res}")
        else:
            print(f"\n[DRY RUN] {updates_made} exercises ready to update. Run with --apply to push changes.")
    else:
        print("\nAll template weights are already up-to-date with your latest OpenGym session!")

if __name__ == "__main__":
    main()
