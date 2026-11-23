/**
 * Tapo P110M Smart Power & Automation Widget for InnoStudio
 * Controls machine power, displays real-time wattage / energy,
 * and provides quick-settings popover for auto-power-on and idle auto-off.
 */
(function() {
  "use strict";

  const btnGroup = document.getElementById("power-btn-group");
  const btn = document.getElementById("machine-power-btn");
  const label = document.getElementById("machine-power-label");
  const watts = document.getElementById("machine-power-watts");
  const optsBtn = document.getElementById("machine-power-opts-btn");
  const popover = document.getElementById("machine-power-popover");

  // Popover elements
  const popoverStatus = document.getElementById("power-popover-status");
  const optAutoOn = document.getElementById("power-opt-auto-on");
  const optAutoOff = document.getElementById("power-opt-auto-off");
  const optIdleNoWorkout = document.getElementById("power-opt-idle-no-workout");
  const optIdlePostWorkout = document.getElementById("power-opt-idle-post-workout");
  const popoverCountdown = document.getElementById("power-popover-countdown");
  const popoverKwh = document.getElementById("power-popover-kwh");

  if (!btn) return;

  const apiBase = window.location.pathname.includes("/gym") ? "/gym/api" : "/api";

  let pollTimer = null;
  let isToggling = false;
  let isSavingSettings = false;

  function formatTime(seconds) {
    if (seconds == null || isNaN(seconds)) return "--";
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s < 10 ? "0" : ""}${s}s`;
  }

  function updateUI(data) {
    if (btnGroup) btnGroup.classList.remove("power-loading");
    if (btn) btn.classList.remove("power-loading");

    if (!data || !data.success) {
      if (label) label.textContent = "X1 Disconnected";
      if (watts) watts.textContent = "--";
      if (btnGroup) btnGroup.className = "power-btn-group power-off";
      btn.title = data && data.error ? `Error: ${data.error}` : "Plug not responding";
      if (popoverStatus) {
        popoverStatus.textContent = "Offline";
        popoverStatus.className = "power-popover-status";
      }
      if (popoverCountdown) popoverCountdown.textContent = "Auto-off: --";
      return;
    }

    // Power & Lifting states
    if (data.is_on) {
      if (data.is_active_lifting) {
        if (btnGroup) btnGroup.className = "power-btn-group power-lifting";
        if (label) label.textContent = "X1 Lifting";
        if (watts) watts.textContent = `${data.power_w}W 🔥`;
        btn.title = `InnoX1 is Active (${data.power_w}W) - Click to turn OFF`;
        if (popoverStatus) {
          popoverStatus.textContent = "Lifting 🔥";
          popoverStatus.className = "power-popover-status lifting";
        }
      } else {
        if (btnGroup) btnGroup.className = "power-btn-group power-on";
        if (label) label.textContent = "X1 Ready";
        if (watts) watts.textContent = `${data.power_w}W`;
        btn.title = `InnoX1 is ON (Standby ${data.power_w}W) - Click to turn OFF`;
        if (popoverStatus) {
          popoverStatus.textContent = data.active_workout ? "Workout Active 🏋️" : "Standby";
          popoverStatus.className = "power-popover-status active";
        }
      }
    } else {
      if (btnGroup) btnGroup.className = "power-btn-group power-off";
      if (label) label.textContent = "X1 Off";
      if (watts) watts.textContent = "0W";
      btn.title = "InnoX1 is OFF - Click to turn ON";
      if (popoverStatus) {
        popoverStatus.textContent = "Powered Off";
        popoverStatus.className = "power-popover-status";
      }
    }

    // Update settings controls (only if user isn't currently interacting with them)
    if (!isSavingSettings) {
      if (optAutoOn && document.activeElement !== optAutoOn && data.auto_power_on !== undefined) {
        optAutoOn.checked = Boolean(data.auto_power_on);
      }
      if (optAutoOff && document.activeElement !== optAutoOff && data.auto_power_off !== undefined) {
        optAutoOff.checked = Boolean(data.auto_power_off);
      }
      if (optIdleNoWorkout && document.activeElement !== optIdleNoWorkout && data.idle_timeout_no_workout_min) {
        optIdleNoWorkout.value = String(data.idle_timeout_no_workout_min);
      }
      if (optIdlePostWorkout && document.activeElement !== optIdlePostWorkout && data.idle_timeout_post_workout_min) {
        optIdlePostWorkout.value = String(data.idle_timeout_post_workout_min);
      }
    }

    // Auto-off countdown
    if (popoverCountdown) {
      if (!data.is_on) {
        popoverCountdown.textContent = "Auto-off: Machine is Off";
      } else if (!data.auto_power_off) {
        popoverCountdown.textContent = "Auto-off: Disabled";
      } else if (data.is_active_lifting) {
        popoverCountdown.textContent = "Auto-off: Paused (Lifting 🔥)";
      } else if (data.active_workout) {
        popoverCountdown.textContent = "Auto-off: Paused (Workout Active)";
      } else if (data.remaining_seconds != null) {
        const tStr = formatTime(data.remaining_seconds);
        popoverCountdown.textContent = `⏳ Auto-off in ${tStr}`;
      } else {
        popoverCountdown.textContent = "Auto-off: Active";
      }
    }

    // Energy display
    if (popoverKwh) {
      const today = data.today_kwh != null ? data.today_kwh : 0.0;
      popoverKwh.textContent = `Today: ${today} kWh`;
    }
  }

  async function fetchStatus() {
    if (isToggling) return;
    try {
      const res = await fetch(apiBase + "/power/status");
      const data = await res.json();
      updateUI(data);
      return data;
    } catch (e) {
      updateUI({ success: false, error: e.message });
    }
  }

  async function togglePower() {
    if (isToggling) return;
    isToggling = true;
    if (btnGroup) btnGroup.classList.add("power-loading");
    if (label) label.textContent = "Switching…";
    try {
      const res = await fetch(apiBase + "/power/toggle", { method: "POST" });
      const data = await res.json();
      updateUI(data);
    } catch (e) {
      alert("Failed to toggle power: " + e.message);
      await fetchStatus();
    } finally {
      isToggling = false;
    }
  }

  async function turnOn() {
    isToggling = true;
    if (btnGroup) btnGroup.classList.add("power-loading");
    try {
      const res = await fetch(apiBase + "/power/on", { method: "POST" });
      const data = await res.json();
      updateUI(data);
      return data;
    } finally {
      isToggling = false;
    }
  }

  async function turnOff() {
    isToggling = true;
    if (btnGroup) btnGroup.classList.add("power-loading");
    try {
      const res = await fetch(apiBase + "/power/off", { method: "POST" });
      const data = await res.json();
      updateUI(data);
      return data;
    } finally {
      isToggling = false;
    }
  }

  async function saveSettings(updates) {
    isSavingSettings = true;
    try {
      const res = await fetch(apiBase + "/power/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates)
      });
      const data = await res.json();
      await fetchStatus();
      return data;
    } catch (e) {
      console.error("Failed to update power settings:", e);
    } finally {
      isSavingSettings = false;
    }
  }

  // --- Popover Interactions ---
  function openPopover() {
    if (!popover) return;
    popover.hidden = false;
    if (optsBtn) optsBtn.setAttribute("aria-expanded", "true");
    fetchStatus();
  }

  function closePopover() {
    if (!popover) return;
    popover.hidden = true;
    if (optsBtn) optsBtn.setAttribute("aria-expanded", "false");
  }

  function togglePopover(e) {
    e.stopPropagation();
    if (popover && !popover.hidden) {
      closePopover();
    } else {
      openPopover();
    }
  }

  if (optsBtn) {
    optsBtn.addEventListener("click", togglePopover);
  }

  // Close popover when clicking outside
  document.addEventListener("click", function(e) {
    if (!popover || popover.hidden) return;
    if (!popover.contains(e.target) && !optsBtn.contains(e.target)) {
      closePopover();
    }
  });

  // Close popover on Escape
  document.addEventListener("keydown", function(e) {
    if (e.key === "Escape" && popover && !popover.hidden) {
      closePopover();
    }
  });

  // Settings form bindings
  if (optAutoOn) {
    optAutoOn.addEventListener("change", () => saveSettings({ auto_power_on: optAutoOn.checked }));
  }
  if (optAutoOff) {
    optAutoOff.addEventListener("change", () => saveSettings({ auto_power_off: optAutoOff.checked }));
  }
  if (optIdleNoWorkout) {
    optIdleNoWorkout.addEventListener("change", () => saveSettings({ idle_timeout_no_workout_min: parseInt(optIdleNoWorkout.value, 10) }));
  }
  if (optIdlePostWorkout) {
    optIdlePostWorkout.addEventListener("change", () => saveSettings({ idle_timeout_post_workout_min: parseInt(optIdlePostWorkout.value, 10) }));
  }

  btn.addEventListener("click", togglePower);

  // Initial poll and recurring poll every 3 seconds
  fetchStatus();
  pollTimer = setInterval(fetchStatus, 3000);

  // Expose API for automations
  window.InnoPower = {
    getStatus: fetchStatus,
    turnOn,
    turnOff,
    toggle: togglePower,
    saveSettings
  };
})();
