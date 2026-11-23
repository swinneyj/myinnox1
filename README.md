# InnoStudio

An enhanced, local-first web client and automation suite for INNODIGYM fitness equipment (X1 / X1 Pro).

Originally inspired by and based upon the work of [dalocar/myinnox1](https://github.com/dalocar/myinnox1).

---

## Key Features

- **Apple HIG & Mobile-Optimized Interface**: Polished, responsive layout tailored for phones, tablets, and desktop browsers with dark/light modes.
- **Smart Power Automation (Tapo P110M / Matter)**:
  - Turns on the equipment when routines are pushed or launched.
  - Real-time wattage and kilowatt-hour (kWh) telemetry monitoring.
  - Auto shutoff when machine is idle (configurable timers for pre-workout and post-workout).
- **OpenGym & Hevy Bridge**:
  - Bi-directional synchronization between INNODIGYM custom routines and self-hosted [OpenGym](https://github.com/duartesantos8/opengym).
  - Routine and exercise translation utilities with Hevy workout mapping.
- **Local-First & Private**:
  - Runs directly on your local network or server.
  - Credentials and tokens stay stored locally in your browser and on your own machine.

---

## Architecture Overview

- **`myinnox1-local/`**: The client web application (HTML/CSS/JS) containing the program builder, movement browser, activity history, and settings.
- **`serve_innox1.py`**: Lightweight local Python server providing reverse-proxy support for the equipment API, OpenGym endpoints, and Tapo telemetry.
- **`power_automation.py` & `tapo_manager.py`**: Background power watchdog and smart plug control layer.
- **`opengym_sync.py` & `sync.py`**: Automation scripts for syncing routine templates and weights with OpenGym.

---

## Quick Start

### 1. Requirements
- Python 3.9+
- Optional: `kasa-python` (if using Tapo / Kasa smart plug automation)

```bash
pip install -r requirements.txt # or install python-kasa if using smart power features
```

### 2. Configuration (Optional)

Copy the example configuration files if you plan to use smart plugs or OpenGym:

```bash
# For smart plug power management:
cp tapo_config.example.json tapo_config.json

# For self-hosted OpenGym integration:
cp opengym_config.example.json opengym_config.json

# For custom power idle timeout settings:
cp power_settings.example.json power_settings.json
```

### 3. Run Locally

```bash
python3 serve_innox1.py
```

Open your browser to `http://localhost:8085`.

---

## Docker Deployment

You can run the web client or a full OpenGym stack using Docker Compose:

```bash
# Run the InnoStudio web interface
docker compose -f docker-compose.innox1.yml up -d

# Run a paired local OpenGym instance
docker compose -f docker-compose.opengym.yml up -d
```

---

## Acknowledgments & License

- Built upon the open-source client foundation created by [@dalocar](https://github.com/dalocar/myinnox1).
- Distributed under the MIT License.
