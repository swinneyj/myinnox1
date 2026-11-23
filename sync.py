#!/usr/bin/env python3
"""
Unified Workout <-> Innodigym Auto-Sync (Hevy & OpenGym)
Automatically pulls your latest workout weights from either Hevy or OpenGym
(whichever was completed most recently) and updates the matching custom workout
template inside the Innodigym X1 Pro cloud backend.
"""

import sys
import os
import json
import plistlib
import urllib.request
import urllib.error
import subprocess
from datetime import datetime

INNODIGYM_BASE = "https://power.renhesports.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_FILE = os.path.join(BASE_DIR, "mapping.json")
STATE_FILE = os.path.join(BASE_DIR, "last_sync.json")
TOKEN_FILE = os.path.join(BASE_DIR, "innodigym_token.txt")
OPENGYM_TOKEN_FILE = os.path.join(BASE_DIR, "opengym_token.txt")
OPENGYM_CONFIG_FILE = os.path.join(BASE_DIR, "opengym_config.json")
OPENGYM_CATALOG_FILE = os.path.join(BASE_DIR, "opengym_catalog.json")

# Innodigym backend units: tenths of a kg.
# 1 lb = 0.45359237 kg * 10 = 4.5359237 server units.
LBS_TO_SERVER_SCALE = 4.5359237

CONTAINER_PLIST = os.path.expanduser(
    "~/Library/Containers/com.innodigym.power202603/Data/Library/Preferences/com.innodigym.power202603.plist"
)
OPENGYM_REMOTE_PLIST = os.path.expanduser(
    "~/Library/Containers/ch.opengym.app/Data/Library/NoCloud/opengym-remote.json"
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

def get_keychain_hevy_key():
    """Retrieve Hevy API key stored in macOS Keychain."""
    cmd = ["security", "find-generic-password", "-s", "Hevy API", "-w"]
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None

def get_opengym_credentials():
    """Retrieve OpenGym URL and Bearer token."""
    # Check local files first
    token = None
    if os.path.exists(OPENGYM_TOKEN_FILE):
        try:
            with open(OPENGYM_TOKEN_FILE) as f:
                token = f.read().strip()
        except Exception:
            pass

    url = os.environ.get("OPENGYM_URL", "http://localhost:8080")
    if os.path.exists(OPENGYM_CONFIG_FILE):
        try:
            with open(OPENGYM_CONFIG_FILE) as f:
                cfg = json.load(f)
                url = cfg.get("url", url).rstrip("/")
        except Exception:
            pass

    # Fallback to local container if available
    if not token and os.path.exists(OPENGYM_REMOTE_PLIST):
        try:
            with open(OPENGYM_REMOTE_PLIST) as f:
                rem = json.load(f)
                token = rem.get("token")
                url = rem.get("base", url).rstrip("/")
        except Exception:
            pass

    return url, token

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

    if not token and os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                token = f.read().strip()
        except Exception:
            pass

    if token:
        try:
            with open(TOKEN_FILE, "w") as f:
                f.write(token)
            web_dir = os.path.join(BASE_DIR, "myinnox1-local")
            if os.path.exists(web_dir):
                with open(os.path.join(web_dir, "token.js"), "w") as f:
                    f.write(f'window.INNO_TOKEN = {json.dumps(token)};\nwindow.INNO_EMAIL = "TheITGuru";\n')
                with open(os.path.join(web_dir, "token.json"), "w") as f:
                    json.dump({"token": token, "email": "TheITGuru"}, f)
        except Exception:
            pass
        return token

    print("Error: Could not locate active Innodigym token.")
    sys.exit(1)

def get_innodigym_templates(token):
    url = f"{INNODIGYM_BASE}/api/course/custom/list"
    req = urllib.request.Request(url, headers={"Authorization": token})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            res_data = data.get("data", [])
            if isinstance(res_data, list):
                return res_data
            elif isinstance(res_data, dict):
                return res_data.get("records", [])
            return []
    except Exception as e:
        print(f"Error fetching Innodigym templates: {e}")
        return []

def get_innodigym_template_detail(token, course_id):
    url = f"{INNODIGYM_BASE}/api/course/custom/detail?id={course_id}"
    req = urllib.request.Request(url, headers={"Authorization": token})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("data", {})
    except Exception as e:
        print(f"Error fetching course detail {course_id}: {e}")
        return None

def save_innodigym_template(token, payload):
    url = f"{INNODIGYM_BASE}/api/course/custom/save"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Authorization": token, "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error saving Innodigym course {payload.get('name')}: {e}")
        return {}

def fetch_latest_hevy_workout(api_key):
    """Fetch the latest workout from Hevy API."""
    if not api_key:
        return None
    url = "https://api.hevyapp.com/v1/workouts?page=1&pageSize=1"
    req = urllib.request.Request(url, headers={"api-key": api_key})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            workouts = data.get("workouts", [])
            if not workouts:
                return None
            w = workouts[0]
            # Normalize timestamp
            end_time_str = w.get("end_time") or w.get("updated_at") or w.get("start_time")
            ts = datetime.fromisoformat(end_time_str.replace("Z", "+00:00")).timestamp() if end_time_str else 0
            
            # Extract exercise weights (in combined lbs)
            weights = {}
            for ex in w.get("exercises", []):
                title = ex.get("title", "").strip()
                max_lbs = 0.0
                for s in ex.get("sets", []):
                    w_kg = s.get("weight_kg")
                    if w_kg is not None:
                        w_lbs = float(w_kg) * 2.20462
                        if w_lbs > max_lbs:
                            max_lbs = w_lbs
                if max_lbs > 0:
                    weights[title] = round(max_lbs, 1)

            return {
                "source": "hevy",
                "id": w.get("id"),
                "name": w.get("title", "Workout"),
                "timestamp": ts,
                "date_display": end_time_str[:10] if end_time_str else "Unknown",
                "weights": weights
            }
    except Exception as e:
        return None

def fetch_latest_opengym_workout(url, token):
    """Fetch the latest workout from OpenGym API."""
    if not token or not url:
        return None
    req = urllib.request.Request(f"{url}/api/data", headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            state = data.get("state") or {}
            workouts = state.get("workouts") or []
            if not workouts:
                return None
            
            # Sort descending by end / start
            sorted_w = sorted(workouts, key=lambda x: x.get("end") or x.get("start") or 0, reverse=True)
            w = sorted_w[0]
            ms = w.get("end") or w.get("start") or 0
            ts = ms / 1000.0 if ms else 0

            # Catalog & custom exercises for name lookup
            catalog = load_json(OPENGYM_CATALOG_FILE)
            custom_ex = {e["id"]: e.get("n") or e.get("name", "Custom") for e in state.get("customEx", [])}

            weights = {}
            for entry in w.get("entries", []):
                ex_id = entry.get("id")
                ex_name = custom_ex.get(ex_id) or catalog.get(ex_id) or f"Exercise {ex_id}"
                max_w = entry.get("topW")
                if max_w is None:
                    max_w = 0.0
                    for s in entry.get("sets", []):
                        if s.get("done", True) and s.get("w", 0) > max_w:
                            max_w = float(s.get("w", 0))
                if max_w and max_w > 0:
                    weights[ex_name.strip()] = round(float(max_w), 1)

            return {
                "source": "opengym",
                "id": w.get("id"),
                "name": w.get("name", "Workout"),
                "timestamp": ts,
                "date_display": w.get("d", "Unknown"),
                "weights": weights
            }
    except Exception:
        return None

def sync_unified_workout(workout, templates, token, mapping, dry_run=True):
    w_name = workout["name"]
    source = workout["source"].upper()
    logged_weights = workout["weights"]

    # Match routine title with Innodigym custom courses
    matched = None
    for t in templates:
        t_name = t.get("name", "").strip()
        if t_name.lower() == w_name.lower() or w_name.lower() in t_name.lower():
            matched = t
            break

    if not matched:
        print(f"[{source}] No matching Innodigym custom course found for \"{w_name}\".")
        return False

    c_id = matched["id"]
    detail = get_innodigym_template_detail(token, c_id)
    if not detail:
        return False

    steps = detail.get("mainStepList") or detail.get("stepList") or []
    updates_made = 0
    updates_list = []

    print(f"\n🔄 Syncing {source} Workout \"{w_name}\" ({workout['date_display']}) -> Innodigym \"{matched.get('name')}\"")
    print(f"{'Exercise':<35} | {'Old Weight':<12} | {'Logged Max':<12} | {'New Target':<12} | {'Status'}")
    print("-" * 85)

    for step in steps:
        ex_name = step.get("actionName", "").strip()
        side_num = step.get("sideNum")
        old_sw = step.get("sideWeight", 0)
        
        # In OpenGym / Hevy, weights are logged as total lifted load.
        # Combined exercises (sideNum == 2) use both cables, so machine stores half (per cable).
        is_combined = (side_num == 2)
        old_lbs = round((old_sw / LBS_TO_SERVER_SCALE) * 2) if is_combined else round(old_sw / LBS_TO_SERVER_SCALE)

        target_w = None
        for log_name, w in logged_weights.items():
            if log_name.lower() == ex_name.lower():
                target_w = w
                break
            if mapping.get(log_name.lower()) == ex_name or mapping.get(ex_name.lower()) == log_name:
                target_w = w
                break
            if ex_name.lower() in log_name.lower() or log_name.lower() in ex_name.lower():
                target_w = w
                break

        if target_w is not None:
            new_sw = round((target_w / 2.0) * LBS_TO_SERVER_SCALE) if is_combined else round(target_w * LBS_TO_SERVER_SCALE)
            if new_sw != old_sw:
                status = "⚡ UPDATE"
                updates_made += 1
                step["sideWeight"] = new_sw
                updates_list.append({
                    "name": ex_name,
                    "old_lbs": old_lbs,
                    "new_lbs": round(target_w)
                })
            else:
                status = "✔ MATCHED"
            print(f"{ex_name:<35} | {old_lbs:>4} lbs     | {target_w:>4} lbs     | {round(target_w):>4} lbs     | {status}")
        else:
            print(f"{ex_name:<35} | {old_lbs:>4} lbs     | {'-':>4}         | {old_lbs:>4} lbs     | - NO LOG")

    if updates_made == 0:
        print(f"✔ All template weights are already up-to-date with your {source} workout.")
        return True, updates_list

    if dry_run:
        print(f"\n[DRY RUN] {updates_made} exercises ready to update. Run with --apply to push.")
    else:
        print(f"\nSaving {updates_made} updates to Innodigym cloud...")
        res = save_innodigym_template(token, detail)
        if res.get("code") == 200 or res.get("success"):
            print("🎉 Successfully updated weights in Innodigym!")
            print("👉 Pull down to refresh your Innodigym X1 Pro machine screen to see updated weights.")
        else:
            print(f"Failed to save: {res}")
            return False, []
    return True, updates_list

def record_sync_success(latest, updates_list):
    now = datetime.now()
    record = {
        "id": latest["id"],
        "workout_name": latest["name"],
        "source": latest["source"].capitalize(),
        "date_display": latest.get("date_display"),
        "timestamp": latest["timestamp"],
        "synced_at": now.isoformat(),
        "sync_time": now.strftime("%b %d, %Y %I:%M %p"),
        "updates_count": len(updates_list),
        "updates": updates_list
    }
    save_json(STATE_FILE, {
        "last_workout_id": latest["id"],
        "last_source": latest["source"].capitalize(),
        "workout_name": latest["name"],
        "date_display": latest.get("date_display"),
        "last_timestamp": latest["timestamp"],
        "last_synced_at": now.isoformat(),
        "last_sync_time": now.strftime("%b %d, %Y %I:%M %p"),
        "updates_count": len(updates_list),
        "updates": updates_list
    })
    history_file = os.path.join(BASE_DIR, "sync_history.json")
    history = load_json(history_file)
    if not isinstance(history, list):
        history = []
    history = [h for h in history if h.get("id") != latest["id"]]
    history.insert(0, record)
    save_json(history_file, history[:20])

def main():
    apply_changes = "--apply" in sys.argv or "--auto" in sys.argv
    is_auto = "--auto" in sys.argv

    hevy_key = get_keychain_hevy_key()
    og_url, og_token = get_opengym_credentials()
    inno_token = get_innodigym_token()
    mapping = load_json(MAPPING_FILE)
    state = load_json(STATE_FILE)

    # 1. Fetch from both sources
    hevy_w = fetch_latest_hevy_workout(hevy_key)
    og_w = fetch_latest_opengym_workout(og_url, og_token)

    # 2. Pick the newest completed workout
    candidates = [w for w in (hevy_w, og_w) if w is not None]
    if not candidates:
        if not is_auto:
            print("No workouts found on either Hevy or OpenGym.")
        return

    # Sort descending by completion timestamp
    candidates.sort(key=lambda x: x["timestamp"], reverse=True)
    latest = candidates[0]

    # In background auto mode: check if this exact workout was already synced
    if is_auto:
        last_id = state.get("last_workout_id")
        last_ts = state.get("last_timestamp")
        if last_id == latest["id"] and last_ts == latest["timestamp"]:
            return  # Already up to date

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-sync triggered for new {latest['source'].upper()} workout ({latest['id']})")
        templates = get_innodigym_templates(inno_token)
        success, updates_list = sync_unified_workout(latest, templates, inno_token, mapping, dry_run=False)
        if success:
            record_sync_success(latest, updates_list)
        return

    # Interactive manual mode
    print("=" * 60)
    print("  Unified Workout -> Innodigym Weight Auto-Sync")
    print(f"  Mode: {'APPLY (live cloud update)' if apply_changes else 'DRY RUN (preview only)'}")
    print("=" * 60)
    print(f"Latest activity detected: {latest['source'].upper()} workout \"{latest['name']}\" on {latest['date_display']}")
    if len(candidates) > 1:
        other = candidates[1]
        print(f"(Previous activity: {other['source'].upper()} \"{other['name']}\" on {other['date_display']})")

    templates = get_innodigym_templates(inno_token)
    success, updates_list = sync_unified_workout(latest, templates, inno_token, mapping, dry_run=not apply_changes)
    if apply_changes and success:
        record_sync_success(latest, updates_list)

if __name__ == "__main__":
    main()
