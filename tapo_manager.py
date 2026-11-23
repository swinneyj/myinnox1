#!/usr/bin/env python3
"""
Tapo P110M Local Manager for InnoStudio.
Connects directly to the Tapo P110M plug via local KLAP protocol.
Supports secure macOS Keychain password storage and live energy monitoring (W, kWh).
"""

import os
import sys
import json
import asyncio
import subprocess
from kasa import Discover

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tapo_config.json")
KEYCHAIN_SERVICE = "tapo_p110m"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def get_keychain_password(service: str, account: str = None) -> str:
    """Retrieve password securely from macOS Keychain."""
    cmd = ["security", "find-generic-password", "-s", service]
    if account:
        cmd.extend(["-a", account])
    cmd.append("-w")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except Exception:
        # Fall back to finding any password for the service
        if account:
            try:
                proc = subprocess.run(["security", "find-generic-password", "-s", service, "-w"], capture_output=True, text=True, check=True)
                return proc.stdout.strip()
            except Exception:
                return None
        return None

async def _get_device():
    cfg = load_config()
    host = cfg.get("host") or os.environ.get("TAPO_HOST")
    username = cfg.get("username") or os.environ.get("TAPO_USERNAME")

    if not host or not username:
        raise ValueError(
            "Tapo smart plug configuration not found.\n"
            "Please create 'tapo_config.json' with 'host' and 'username' (see tapo_config.example.json)\n"
            "or set TAPO_HOST and TAPO_USERNAME environment variables."
        )

    password = get_keychain_password(KEYCHAIN_SERVICE, username)
    if not password:
        password = cfg.get("password") or os.environ.get("TAPO_PASSWORD")

    if not password:
        raise ValueError(
            f"No password found for service '{KEYCHAIN_SERVICE}' or user '{username}'.\n"
            f"Run: security add-generic-password -U -s \"{KEYCHAIN_SERVICE}\" -a \"{username}\" -w \"YOUR_PASSWORD\"\n"
            f"or specify 'password' in tapo_config.json / TAPO_PASSWORD env var."
        )
        
    dev = await Discover.discover_single(
        host,
        username=username,
        password=password,
        discovery_timeout=4
    )
    if not dev:
        raise RuntimeError(f"Could not connect to Tapo plug at {host}")
        
    if "type" not in dev._info:
        dev._info["type"] = dev._info.get("device_type", "SMART.TAPOPLUG")
        
    await dev.update()
    return dev

async def get_status_async():
    dev = None
    try:
        dev = await _get_device()
        is_on = dev.is_on
        power_w = 0.0
        today_kwh = 0.0
        month_kwh = 0.0
        
        energy = dev.modules.get("Energy")
        if energy:
            power_w = round(float(getattr(energy, "current_consumption", 0.0) or 0.0), 1)
            today_kwh = round(float(getattr(energy, "consumption_today", 0.0) or 0.0), 3)
            month_kwh = round(float(getattr(energy, "consumption_this_month", 0.0) or 0.0), 3)

        result = {
            "success": True,
            "connected": True,
            "host": dev.host,
            "alias": dev.alias,
            "model": dev.model,
            "is_on": is_on,
            "power_w": power_w,
            "today_kwh": today_kwh,
            "month_kwh": month_kwh,
            "is_active_lifting": power_w >= 30.0,
            "is_idle": is_on and power_w < 28.0
        }
        if dev.protocol:
            await dev.protocol.close()
        return result
    except Exception as e:
        if dev and dev.protocol:
            try:
                await dev.protocol.close()
            except Exception:
                pass
        return {
            "success": False,
            "connected": False,
            "error": str(e)
        }

async def set_power_async(turn_on: bool):
    dev = None
    try:
        dev = await _get_device()
        if turn_on:
            await dev.turn_on()
        else:
            await dev.turn_off()
        await dev.update()
        res = await get_status_async()
        if dev.protocol:
            await dev.protocol.close()
        return res
    except Exception as e:
        if dev and dev.protocol:
            try:
                await dev.protocol.close()
            except Exception:
                pass
        is_unconfigured = "not found" in str(e).lower()
        return {
            "success": False,
            "configured": not is_unconfigured,
            "error": str(e)
        }

async def toggle_power_async():
    dev = None
    try:
        dev = await _get_device()
        if dev.is_on:
            await dev.turn_off()
        else:
            await dev.turn_on()
        await dev.update()
        res = await get_status_async()
        if dev.protocol:
            await dev.protocol.close()
        return res
    except Exception as e:
        if dev and dev.protocol:
            try:
                await dev.protocol.close()
            except Exception:
                pass
        is_unconfigured = "not found" in str(e).lower()
        return {
            "success": False,
            "configured": not is_unconfigured,
            "error": str(e)
        }

def get_status():
    return asyncio.run(get_status_async())

def set_power(turn_on: bool):
    return asyncio.run(set_power_async(turn_on))

def toggle_power():
    return asyncio.run(toggle_power_async())

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "on":
        res = set_power(True)
    elif action == "off":
        res = set_power(False)
    elif action == "toggle":
        res = toggle_power()
    else:
        res = get_status()
    print(json.dumps(res, indent=2))
