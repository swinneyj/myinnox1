#!/usr/bin/env python3
"""
Power Automation & Idle Watchdog for InnoX1 / Tapo P110M.
- Automatically powers on InnoX1 when a workout routine is pushed or started.
- Monitors live power telemetry (wattage) and OpenGym workout state.
- Automatically powers off InnoX1 when idle:
    * Idle with no workout sent: default 15 minutes.
    * Idle after workout / lifting completed: default 20 minutes.
"""

import os
import sys
import json
import time
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "power_settings.json")

# Import sibling modules
sys.path.append(BASE_DIR)
import tapo_manager
try:
    import opengym_bridge
except ImportError:
    opengym_bridge = None

DEFAULT_SETTINGS = {
    "auto_power_on": True,
    "auto_power_off": True,
    "idle_timeout_no_workout_min": 15,
    "idle_timeout_post_workout_min": 20
}

_lock = threading.Lock()
_settings = dict(DEFAULT_SETTINGS)

# Runtime telemetry & state
_state = {
    "is_on": False,
    "power_w": 0.0,
    "today_kwh": 0.0,
    "month_kwh": 0.0,
    "is_active_lifting": False,
    "is_idle": False,
    "has_lifted": False,
    "active_workout": False,
    "last_active_time": None,
    "power_on_time": None,
    "last_poll_time": 0.0,
    "cached_status": None,
    "status_error": None
}

def load_settings():
    global _settings
    with _lock:
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE) as f:
                    data = json.load(f)
                    for k, v in DEFAULT_SETTINGS.items():
                        _settings[k] = data.get(k, v)
                return
            except Exception as e:
                print(f"[AutoPower] Error reading {SETTINGS_FILE}: {e}")
        _settings = dict(DEFAULT_SETTINGS)
        save_settings_locked()

def save_settings_locked():
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(_settings, f, indent=2)
    except Exception as e:
        print(f"[AutoPower] Error writing {SETTINGS_FILE}: {e}")

def get_settings():
    with _lock:
        return dict(_settings)

def update_settings(updates: dict):
    with _lock:
        if "auto_power_on" in updates:
            _settings["auto_power_on"] = bool(updates["auto_power_on"])
        if "auto_power_off" in updates:
            _settings["auto_power_off"] = bool(updates["auto_power_off"])
        if "idle_timeout_no_workout_min" in updates:
            _settings["idle_timeout_no_workout_min"] = max(1, int(updates["idle_timeout_no_workout_min"]))
        if "idle_timeout_post_workout_min" in updates:
            _settings["idle_timeout_post_workout_min"] = max(1, int(updates["idle_timeout_post_workout_min"]))
        save_settings_locked()
        return dict(_settings)

def is_opengym_workout_active():
    if not opengym_bridge:
        return False
    try:
        data = opengym_bridge.fetch_opengym_data()
        state = data.get("state", {})
        workouts = state.get("workouts", [])
        for w in workouts:
            # Active workout has no 'end' timestamp or end is 0
            if not w.get("end"):
                return True
    except Exception:
        pass
    return False

def check_power_status(force=False):
    """Fetches status from tapo_manager, caching for up to 3 seconds."""
    now = time.time()
    with _lock:
        if not force and _state["cached_status"] and (now - _state["last_poll_time"] < 3.0):
            return dict(_state["cached_status"])

    status = tapo_manager.get_status()
    now = time.time()

    with _lock:
        if status.get("success"):
            was_on = _state["is_on"]
            is_on = status.get("is_on", False)
            power_w = status.get("power_w", 0.0)
            is_lifting = status.get("is_active_lifting", False)

            _state["is_on"] = is_on
            _state["power_w"] = power_w
            _state["today_kwh"] = status.get("today_kwh", 0.0)
            _state["month_kwh"] = status.get("month_kwh", 0.0)
            _state["is_active_lifting"] = is_lifting
            _state["is_idle"] = status.get("is_idle", False)
            _state["status_error"] = None

            if is_on and not was_on:
                # Just turned on
                _state["power_on_time"] = now
                _state["last_active_time"] = now
                _state["has_lifted"] = False
            elif not is_on:
                # Turned off
                _state["power_on_time"] = None
                _state["last_active_time"] = None
                _state["has_lifted"] = False

            if is_on:
                if is_lifting:
                    _state["has_lifted"] = True
                    _state["last_active_time"] = now
                elif _state["last_active_time"] is None:
                    _state["last_active_time"] = now
        else:
            _state["status_error"] = status.get("error")

        _state["last_poll_time"] = now
        _state["cached_status"] = _build_combined_status(status)
        return dict(_state["cached_status"])

def _build_combined_status(base_status):
    now = time.time()
    is_on = _state["is_on"]
    auto_off = _settings["auto_power_off"]
    has_lifted = _state["has_lifted"]
    active_workout = _state["active_workout"]

    idle_seconds = 0
    remaining_seconds = None

    if is_on:
        last_active = _state["last_active_time"] or _state["power_on_time"] or now
        idle_seconds = max(0, int(now - last_active))

        timeout_min = _settings["idle_timeout_post_workout_min"] if has_lifted else _settings["idle_timeout_no_workout_min"]
        timeout_sec = timeout_min * 60

        if active_workout or _state["is_active_lifting"]:
            remaining_seconds = timeout_sec
            idle_seconds = 0
        else:
            remaining_seconds = max(0, timeout_sec - idle_seconds)

    res = dict(base_status) if base_status.get("success") else {
        "success": False,
        "error": _state["status_error"] or "Could not connect to plug",
        "connected": False
    }

    res.update({
        "is_on": is_on,
        "power_w": _state["power_w"],
        "today_kwh": _state["today_kwh"],
        "month_kwh": _state["month_kwh"],
        "is_active_lifting": _state["is_active_lifting"],
        "is_idle": _state["is_idle"],
        "has_lifted": has_lifted,
        "active_workout": active_workout,
        "idle_seconds": idle_seconds,
        "remaining_seconds": remaining_seconds,
        "auto_power_on": _settings["auto_power_on"],
        "auto_power_off": auto_off,
        "idle_timeout_no_workout_min": _settings["idle_timeout_no_workout_min"],
        "idle_timeout_post_workout_min": _settings["idle_timeout_post_workout_min"]
    })
    return res

def auto_power_on_if_needed(reason="workout_pushed"):
    """Turns on InnoX1 if auto_power_on is enabled and the machine is off."""
    with _lock:
        if not _settings["auto_power_on"]:
            return {"enabled": False, "turned_on": False}

    status = check_power_status(force=True)
    if not status.get("is_on"):
        print(f"[AutoPower] Auto powering on InnoX1 (reason: {reason})...")
        res = tapo_manager.set_power(True)
        now = time.time()
        with _lock:
            _state["is_on"] = True
            _state["power_on_time"] = now
            _state["last_active_time"] = now
            _state["has_lifted"] = False
            _state["cached_status"] = None
        return {"enabled": True, "turned_on": True, "result": res}
    else:
        # Machine was already on; refresh active timestamp
        with _lock:
            _state["last_active_time"] = time.time()
        return {"enabled": True, "turned_on": False}

def _watchdog_loop():
    """Background daemon checking idle status every 10 seconds."""
    while True:
        try:
            status = check_power_status(force=True)
            if status.get("success") and status.get("is_on"):
                # Check OpenGym active workout
                active_og = is_opengym_workout_active()
                now = time.time()

                with _lock:
                    _state["active_workout"] = active_og
                    if active_og:
                        _state["last_active_time"] = now

                    is_lifting = _state["is_active_lifting"]
                    has_lifted = _state["has_lifted"]
                    auto_off = _settings["auto_power_off"]
                    timeout_min = _settings["idle_timeout_post_workout_min"] if has_lifted else _settings["idle_timeout_no_workout_min"]
                    timeout_sec = timeout_min * 60

                    last_active = _state["last_active_time"] or _state["power_on_time"] or now
                    idle_sec = now - last_active

                if auto_off and not is_lifting and not active_og:
                    if idle_sec >= timeout_sec:
                        print(f"[AutoPower] Idle timeout ({int(idle_sec / 60)} min idle, has_lifted={has_lifted}). Automatically powering off InnoX1...")
                        tapo_manager.set_power(False)
                        with _lock:
                            _state["is_on"] = False
                            _state["power_on_time"] = None
                            _state["last_active_time"] = None
                            _state["has_lifted"] = False
                            _state["cached_status"] = None

        except Exception as e:
            print(f"[AutoPower] Watchdog error: {e}")

        time.sleep(10)

def start_watchdog():
    load_settings()
    t = threading.Thread(target=_watchdog_loop, name="InnoX1-AutoPowerWatchdog", daemon=True)
    t.start()
    print("[AutoPower] Background watchdog started (checks every 10s).")

if __name__ == "__main__":
    start_watchdog()
    time.sleep(15)
    print("Settings:", get_settings())
    print("Status:", check_power_status())
