#!/usr/bin/env python3
"""
OpenGym Bridge for InnoStudio.
Handles bi-directional communication between InnoStudio and OpenGym:
- Live status checks
- On-demand weight synchronization
- Push Innodigym programs into OpenGym routines
- List OpenGym routines
"""

import os
import sys
import json
import time
import uuid
import subprocess
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "opengym_config.json")
TOKEN_FILE = os.path.join(BASE_DIR, "opengym_token.txt")
CATALOG_FILE = os.path.join(BASE_DIR, "opengym_catalog.json")
MAPPING_FILE = os.path.join(BASE_DIR, "mapping.json")
INNODIGYM_TOKEN_FILE = os.path.join(BASE_DIR, "innodigym_token.txt")
SYNC_SCRIPT = os.path.join(BASE_DIR, "sync.py")

LBS_TO_SERVER_SCALE = 4.5359237

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

def get_innodigym_token():
    if os.path.exists(INNODIGYM_TOKEN_FILE):
        try:
            with open(INNODIGYM_TOKEN_FILE) as f:
                return f.read().strip()
        except Exception:
            pass
    return None

def fetch_opengym_data():
    url, token = get_opengym_auth()
    if not token:
        raise ValueError("No OpenGym authentication token found")
    req = urllib.request.Request(f"{url}/api/data", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())

def save_opengym_data(state, base_rev):
    url, token = get_opengym_auth()
    payload = json.dumps({"state": state, "baseRev": base_rev}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/api/data",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="PUT"
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status == 200

def get_status():
    url, token = get_opengym_auth()
    configured = os.path.exists(CONFIG_FILE) or os.path.exists(TOKEN_FILE)
    result = {
        "configured": configured,
        "connected": False,
        "url": url,
        "routines_count": 0,
        "last_sync": None,
        "recent_syncs": [],
        "error": None
    }
    
    # Check last sync and history files
    last_sync_file = os.path.join(BASE_DIR, "last_sync.json")
    if os.path.exists(last_sync_file):
        try:
            with open(last_sync_file) as f:
                result["last_sync"] = json.load(f)
        except Exception:
            pass
            
    history_file = os.path.join(BASE_DIR, "sync_history.json")
    if os.path.exists(history_file):
        try:
            with open(history_file) as f:
                result["recent_syncs"] = json.load(f)
        except Exception:
            pass

    try:
        data = fetch_opengym_data()
        state = data.get("state", {})
        result["connected"] = True
        result["routines_count"] = len(state.get("routines", []))
    except Exception as e:
        result["error"] = str(e)
        
    return result

def get_sync_history():
    history_file = os.path.join(BASE_DIR, "sync_history.json")
    if os.path.exists(history_file):
        try:
            with open(history_file) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def get_routines():
    data = fetch_opengym_data()
    state = data.get("state", {})
    routines = []
    for r in state.get("routines", []):
        routines.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "emoji": r.get("emoji", "figureStrength"),
            "exercise_count": len(r.get("ex", []))
        })
    return routines

def trigger_weight_sync():
    """Run the dual sync script to update machine weights from latest Hevy/OpenGym workout."""
    if not os.path.exists(SYNC_SCRIPT):
        return {"success": False, "error": "sync.py not found"}
    try:
        proc = subprocess.run(
            ["/usr/bin/python3", SYNC_SCRIPT, "--apply"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": proc.returncode == 0,
            "output": proc.stdout.strip(),
            "error": proc.stderr.strip() if proc.returncode != 0 else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def push_course_to_opengym(course_id):
    """Pushes an Innodigym custom course into OpenGym as a workout routine."""
    inno_token = get_innodigym_token()
    if not inno_token:
        raise ValueError("Innodigym token missing")

    # 1. Fetch Innodigym Course Details
    detail_url = f"https://power.renhesports.com/api/course/custom/detail?id={course_id}&languageId=en"
    req = urllib.request.Request(detail_url, headers={"Authorization": inno_token})
    with urllib.request.urlopen(req, timeout=8) as resp:
        course_data = json.loads(resp.read().decode()).get("data", {})

    course_name = course_data.get("name", f"Course #{course_id}")
    steps = course_data.get("mainStepList", [])
    if not steps:
        raise ValueError(f"Course '{course_name}' has no exercises in mainStepList")

    # 2. Fetch current OpenGym state
    og_data = fetch_opengym_data()
    state = og_data.get("state", {})
    base_rev = og_data.get("rev", 0)
    existing_routines = state.get("routines", [])
    existing_custom = state.get("customEx", [])

    # Load catalogue and mapping
    catalogue = {}
    if os.path.exists(CATALOG_FILE):
        try:
            with open(CATALOG_FILE) as f:
                catalogue = json.load(f)
        except Exception:
            pass

    # Reverse catalogue index (lower-case name -> id)
    cat_by_name = {name.lower().strip(): cat_id for cat_id, name in catalogue.items()}

    mapping = {}
    if os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE) as f:
                mapping = json.load(f)
        except Exception:
            pass

    # Reverse mapping (Innodigym actionName -> OpenGym name)
    reverse_map = {v.lower().strip(): k for k, v in mapping.items()}

    og_exercises = []
    for step in steps:
        action_name = step.get("actionName", "Exercise").strip()
        group_num = step.get("groupNum") or 3
        reps = step.get("count") or 10
        side_weight = step.get("sideWeight", 0)
        side_num = step.get("sideNum")
        if side_weight:
            per_cable_lb = side_weight / LBS_TO_SERVER_SCALE
            if side_num == 2:
                # Combined: both cables work at once -> total load in OpenGym is 2x
                weight_lb = round(per_cable_lb * 2)
            elif side_num == 0:
                weight_lb = 0
            else:
                weight_lb = round(per_cable_lb)
        else:
            weight_lb = 0 if side_num == 0 else 50

        # Try mapping to OpenGym catalog ID
        target_name = reverse_map.get(action_name.lower(), action_name).lower()
        target_id = cat_by_name.get(target_name)

        if not target_id:
            # Check or create custom exercise in OpenGym
            custom_match = next((c for c in existing_custom if (c.get("n") or c.get("name", "")).lower() == action_name.lower()), None)
            if custom_match:
                target_id = custom_match["id"]
            else:
                target_id = "c_" + uuid.uuid4().hex[:8]
                existing_custom.append({
                    "id": target_id,
                    "n": action_name,
                    "name": action_name,
                    "custom": True,
                    "bp": "upper",
                    "_ts": int(time.time() * 1000)
                })

        og_exercises.append({
            "id": target_id,
            "sets": int(group_num),
            "reps": int(reps),
            "weight": int(weight_lb),
            "mode": "reps",
            "r": int(reps),
            "w": int(weight_lb)
        })

    # Check if routine already exists by name
    existing_routine = next((r for r in existing_routines if r.get("name", "").strip().lower() == course_name.strip().lower()), None)
    if existing_routine:
        existing_routine["ex"] = og_exercises
        existing_routine["_ts"] = int(time.time() * 1000)
        routine_id = existing_routine["id"]
        action_taken = "updated"
    else:
        routine_id = uuid.uuid4().hex[:12]
        new_routine = {
            "id": routine_id,
            "name": course_name,
            "emoji": "figureStrength",
            "ex": og_exercises,
            "_ts": int(time.time() * 1000)
        }
        existing_routines.append(new_routine)
        action_taken = "created"

    state["routines"] = existing_routines
    state["customEx"] = existing_custom

    # Save back to OpenGym
    save_opengym_data(state, base_rev)

    return {
        "success": True,
        "action": action_taken,
        "routine_name": course_name,
        "routine_id": routine_id,
        "exercises_count": len(og_exercises)
    }

def import_routine_to_innodigym(routine_id):
    """Imports an OpenGym routine into Innodigym as a machine-ready custom program."""
    inno_token = get_innodigym_token()
    if not inno_token:
        raise ValueError("Innodigym token missing")

    og_data = fetch_opengym_data()
    state = og_data.get("state", {})
    routines = state.get("routines", [])
    custom_ex = {c["id"]: c.get("n") or c.get("name", "Exercise") for c in state.get("customEx", [])}

    catalogue = {}
    if os.path.exists(CATALOG_FILE):
        try:
            with open(CATALOG_FILE) as f:
                catalogue = json.load(f)
        except Exception:
            pass

    routine = next((r for r in routines if r.get("id") == routine_id), None)
    if not routine:
        raise ValueError(f"OpenGym routine '{routine_id}' not found")

    routine_name = routine.get("name", "OpenGym Workout")
    og_exercises = routine.get("ex", [])
    if not og_exercises:
        raise ValueError(f"Routine '{routine_name}' has no exercises")

    # Fetch Innodigym actions
    action_url = "https://power.renhesports.com/api/action/list?deviceCategory=7&languageId=en"
    req = urllib.request.Request(action_url, headers={"Authorization": inno_token})
    with urllib.request.urlopen(req, timeout=10) as resp:
        actions_list = json.loads(resp.read().decode()).get("data", [])

    actions_by_name = {a.get("name", "").strip().lower(): a for a in actions_list}

    # Load mapping
    mapping = {}
    if os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE) as f:
                mapping = json.load(f)
        except Exception:
            pass
    mapping_lower = {k.strip().lower(): v.strip().lower() for k, v in mapping.items()}

    main_step_list = []
    sort_idx = 1
    for ex in og_exercises:
        ex_id = str(ex.get("id"))
        ex_name = catalogue.get(ex_id) or custom_ex.get(ex_id) or f"Exercise {ex_id}"

        target_name = mapping_lower.get(ex_name.lower(), ex_name.lower())
        matched_action = actions_by_name.get(target_name)

        if not matched_action:
            for aname, act in actions_by_name.items():
                if aname in target_name or target_name in aname:
                    matched_action = act
                    break
        if not matched_action:
            matched_action = actions_list[0]

        sets = ex.get("sets", 3)
        reps = ex.get("reps") or ex.get("r", 10)
        weight_lbs = ex.get("weight") if ex.get("weight") is not None else ex.get("w", 50)

        action_side_num = matched_action.get("sideNum", 2)
        if action_side_num == 2:
            # Combined exercise: OpenGym total weight is divided by 2 for per-cable machine weight
            side_weight = round((weight_lbs / 2.0) * LBS_TO_SERVER_SCALE)
        elif action_side_num == 0:
            side_weight = 0
        else:
            side_weight = round(weight_lbs * LBS_TO_SERVER_SCALE)

        step = {
            "sort": sort_idx,
            "actionLibraryId": matched_action["id"],
            "actionName": matched_action["name"],
            "actionNo": matched_action.get("actionNo", ""),
            "actionType": matched_action.get("actionType", 1),
            "picUrl": matched_action.get("picUrl", ""),
            "stage": 2,
            "count": int(reps),
            "sideWeight": int(side_weight),
            "groupNum": int(sets),
            "restTime": 60,
            "sideNum": int(action_side_num),
            "countType": 1,
            "mode": 0,
            "modeParam": "{}",
            "duration": 12
        }
        main_step_list.append(step)
        sort_idx += 1

    course_payload = {
        "name": routine_name,
        "level": 1,
        "courseType": 1,
        "smallImg": "https://power.renhesports.com/filestore/power/course/COVER_RACK_1_4.jpg",
        "detailsImg": "https://power.renhesports.com/filestore/power/course/COVER_RACK_1_4.jpg",
        "deviceCategory": 7,
        "sportType": 2,
        "muscleParts": "1",
        "duration": len(main_step_list) * 4,
        "capacity": 100,
        "heartRateMin": 0,
        "heartRateMax": 0,
        "deviceTypeList": ["35"],
        "partsList": ["1"],
        "warmUpStepList": [],
        "mainStepList": main_step_list,
        "relaxStepList": []
    }

    save_url = "https://power.renhesports.com/api/course/custom/save"
    save_req = urllib.request.Request(
        save_url,
        data=json.dumps(course_payload).encode("utf-8"),
        headers={
            "Authorization": inno_token,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(save_req, timeout=10) as resp:
        res_data = json.loads(resp.read().decode())

    return {
        "success": True,
        "course_name": routine_name,
        "exercises_count": len(main_step_list)
    }

if __name__ == "__main__":
    st = get_status()
    print("Status:", st)
