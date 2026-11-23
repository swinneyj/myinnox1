#!/usr/bin/env python3
"""
Generates a polished, professional PDF guide for the Hevy <-> Innodigym X1 Pro Sync System.
Generic, clean typography, print-optimized CSS, and cross-platform instructions (Mac & Windows).
"""

import os
import subprocess

OUTPUT_HTML = "/tmp/hevy_innodigym_guide.html"
OUTPUT_PDF = "/Users/theitguru/Documents/antigravity/keen-einstein/Hevy_Innodigym_Sync_Guide.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Hevy to Innodigym X1 Pro Integration Guide</title>
<style>
  @page {
    size: letter;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: counter(page);
      font-size: 9pt;
      color: #64748b;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
  }

  /* Header Cover Area */
  .header-container {
    border-bottom: 2px solid #0284c7;
    padding-bottom: 16px;
    margin-bottom: 24px;
  }
  .title {
    font-size: 24pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
  }
  .subtitle {
    font-size: 12pt;
    color: #475569;
    margin: 0 0 12px 0;
  }
  .badge-row {
    display: flex;
    gap: 8px;
    margin-top: 8px;
  }
  .badge {
    background: #e0f2fe;
    color: #0369a1;
    font-size: 8pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 3px 8px;
    border-radius: 4px;
  }
  .badge-dark {
    background: #f1f5f9;
    color: #334155;
  }

  h2 {
    font-size: 14pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 26px;
    margin-bottom: 12px;
    page-break-after: avoid;
  }

  h3 {
    font-size: 11pt;
    font-weight: 700;
    color: #1e293b;
    margin-top: 16px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 10px 0;
  }

  /* Flow Diagram */
  .diagram-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 16px 0;
    font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
    font-size: 8.5pt;
    line-height: 1.4;
    color: #0f172a;
    page-break-inside: avoid;
  }

  /* Code Blocks */
  pre {
    background: #0f172a;
    color: #f8fafc;
    border-radius: 6px;
    padding: 12px 14px;
    font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
    font-size: 8pt;
    line-height: 1.45;
    overflow-x: auto;
    margin: 10px 0 14px 0;
    page-break-inside: avoid;
  }
  code {
    font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    color: #0f172a;
    padding: 2px 4px;
    border-radius: 3px;
  }
  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }
  th {
    background: #f1f5f9;
    color: #1e293b;
    font-weight: 700;
    text-align: left;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
  }
  td {
    padding: 7px 10px;
    border: 1px solid #e2e8f0;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }

  /* Callout Boxes */
  .callout {
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    margin: 14px 0;
    page-break-inside: avoid;
  }
  .callout-title {
    font-weight: 700;
    color: #15803d;
    margin-bottom: 4px;
    font-size: 9pt;
  }
  .callout-warn {
    background: #fffbeb;
    border-left-color: #d97706;
  }
  .callout-warn .callout-title {
    color: #b45309;
  }

  .step-number {
    display: inline-block;
    background: #0284c7;
    color: #ffffff;
    font-size: 8.5pt;
    font-weight: 700;
    width: 20px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    border-radius: 50%;
    margin-right: 6px;
  }

  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

<div class="header-container">
  <div class="title">Hevy &harr; Innodigym X1 Pro Sync System</div>
  <div class="subtitle">Complete Architecture, Automated Progression, and Cross-Platform Setup Guide</div>
  <div class="badge-row">
    <span class="badge">Cross-Platform</span>
    <span class="badge badge-dark">REST API Cloud-to-Cloud</span>
    <span class="badge badge-dark">Automated Progression</span>
    <span class="badge badge-dark">macOS &bull; Windows &bull; Linux</span>
  </div>
</div>

<h2>1. Executive Summary &amp; Architecture</h2>
<p>
  This integration bridges <strong>Hevy</strong> (where workout sets, reps, and weights are tracked on your phone, watch, or PC) with the <strong>Innodigym X1 Pro</strong> digital resistance station. 
  When you finish a workout in Hevy, your heaviest lifted working weights automatically sync into your custom routines inside Innodigym's cloud backend.
</p>

<div class="diagram-box">
[Finish Workout in Hevy]  (Logged on Mobile, Windows, or Watch)
           &DownArrow;
  [Hevy Public REST API]   (api.hevyapp.com/v1)
           &DownArrow;
   [Python Sync Bridge]    (Runs in background on macOS or Windows)
    &bull; Extracts heaviest working set per movement
    &bull; Maps exercise names via mapping.json
    &bull; Converts weight units to Innodigym internal precision
           &DownArrow;
 [Innodigym Cloud Backend] (power.renhesports.com)
    &bull; Persists updated routine targets (/api/course/custom/save)
           &DownArrow;
 [Innodigym X1 Pro Machine] (Pull down to refresh &rarr; new weights active)
</div>

<div class="callout">
  <div class="callout-title">Platform Independence</div>
  Both Hevy and Innodigym operate via HTTPS REST cloud backends. The sync script does not require UI clicks, screen scraping, or AppleScript. It can run seamlessly on <strong>macOS, Windows 10/11, Linux, Raspberry Pi, or Docker</strong>.
</div>

<h2>2. The Critical Weight Scale Discovery</h2>
<p>
  The Innodigym cloud API internally stores resistance targets in <strong>tenths of a kilogram</strong> (<code>10 &times; kg</code>), regardless of what unit is displayed in the user interface:
</p>
<ul>
  <li><code>1 lb = 0.45359237 kg</code> &rarr; in tenths of a kg: <strong><code>1 lb = 4.5359237 server units</code></strong>.</li>
  <li>To display <strong>74.0 lbs</strong> in the app, the server must store <code>74 &times; 4.5359237 = 336</code>.</li>
  <li>To display <strong>110.0 lbs</strong> in the app, the server must store <code>110 &times; 4.5359237 = 499</code>.</li>
</ul>
<p>
  Without this exact conversion factor, saving raw pounds causes the app to divide the number twice, resulting in fractional per-cable values. Our bridge automatically handles this precision scaling.
</p>

<h2>3. macOS vs. Windows Comparison</h2>
<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>macOS Environment</th>
      <th>Windows Environment</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Innodigym Auth Token</strong></td>
      <td>Auto-read directly from native app container: <code>com.innodigym.power202603.plist</code></td>
      <td>Copied once from mobile app network capture into <code>innodigym_token.txt</code></td>
    </tr>
    <tr>
      <td><strong>Hevy API Key Storage</strong></td>
      <td>macOS Keychain (<code>security find-generic-password</code>)</td>
      <td>Plaintext config (<code>config.json</code>) or Windows Credential Manager</td>
    </tr>
    <tr>
      <td><strong>Background Daemon</strong></td>
      <td>macOS <code>launchd</code> LaunchAgent (runs every 10 min)</td>
      <td>Windows <strong>Task Scheduler</strong> (runs every 10 min)</td>
    </tr>
    <tr>
      <td><strong>Machine Refresh</strong></td>
      <td>Pull-down to refresh on X1 Pro console</td>
      <td>Pull-down to refresh on X1 Pro console</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>4. Step-by-Step Setup Guide</h2>

<h3><span class="step-number">1</span> Generate Hevy API Key</h3>
<ol>
  <li>Log into your account at <a href="https://hevy.com/settings?developer">hevy.com/settings?developer</a> (requires Hevy Pro).</li>
  <li>Click <strong>Generate API Key</strong> and copy the generated key.</li>
</ol>

<h3><span class="step-number">2</span> Obtain Innodigym Auth Token</h3>
<p>
  Innodigym uses a JWT token passed in the <code>Authorization: &lt;token&gt;</code> HTTP header.
</p>
<ul>
  <li><strong>On macOS:</strong> Install the Innodigym app from the Mac App Store and log in once. The script will automatically retrieve the token from your preferences.</li>
  <li><strong>On Windows:</strong> Because there is no native Windows app, intercept your mobile app traffic once using <strong>PCAPdroid</strong> (Android) or <strong>mitmproxy / Proxyman</strong> (iOS/Windows), copy the token, and save it to a file named <code>innodigym_token.txt</code> in the script directory.</li>
</ul>

<h3><span class="step-number">3</span> Exercise Name Mapping (<code>mapping.json</code>)</h3>
<p>
  Create a file named <code>mapping.json</code> in the same folder as the script. This maps your Hevy exercise titles to the corresponding Innodigym movement names:
</p>
<pre><code>{
  "hip thrust (belt)": "Belt Hip Thrust",
  "incline chest press (cable)": "Incline Bench Press (Bar)",
  "seated cable row - bar grip": "Seated Row",
  "reverse lunge (dumbbell)": "Weighted Reverse Lunge",
  "standing calf raise (cable)": "Weighted Calf Raise",
  "belt squat (machine)": "Belt Squat",
  "bench press (cable)": "Seated Chest Press",
  "lat pulldown (cable)": "Close-Grip Reverse Pulldown",
  "seated chest flys (cable)": "Seated Chest Fly",
  "seated shoulder cable press": "Seated Alternating Shoulder Press",
  "face pull": "Face Pull"
}</code></pre>

<h3><span class="step-number">4</span> Cross-Platform Sync Script (<code>sync.py</code>)</h3>
<p>
  Save the following complete Python script as <code>sync.py</code>. It automatically selects the optimal credential source for macOS or Windows:
</p>
<pre><code>#!/usr/bin/env python3
import sys, os, json, plistlib, urllib.request, subprocess
from datetime import datetime

INNODIGYM_BASE = "https://power.renhesports.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_FILE = os.path.join(BASE_DIR, "mapping.json")
STATE_FILE = os.path.join(BASE_DIR, "last_sync.json")
TOKEN_FILE = os.path.join(BASE_DIR, "innodigym_token.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
LBS_TO_SERVER_SCALE = 4.5359237

def get_credentials():
    hevy_key = os.environ.get("HEVY_API_KEY")
    innodigym_token = os.environ.get("INNODIGYM_TOKEN")

    # macOS Keychain &amp; Container Plist extraction
    if sys.platform == "darwin":
        if not hevy_key:
            try:
                cmd = ["security", "find-generic-password", "-s", "Hevy API", "-w"]
                hevy_key = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            except Exception: pass
        if not innodigym_token:
            plist = os.path.expanduser("~/Library/Containers/com.innodigym.power202603/Data/Library/Preferences/com.innodigym.power202603.plist")
            if os.path.exists(plist):
                try:
                    with open(plist, "rb") as f:
                        innodigym_token = plistlib.load(f).get("flutter.cache-tokenKey")
                except Exception: pass

    # Windows / Fallback: config.json or token file
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
                hevy_key = hevy_key or cfg.get("hevy_api_key")
                innodigym_token = innodigym_token or cfg.get("innodigym_token")
        except Exception: pass

    if not innodigym_token and os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f: innodigym_token = f.read().strip()
        except Exception: pass

    if not hevy_key or not innodigym_token:
        print("Error: Missing credentials. Provide them in config.json or environment variables.")
        sys.exit(1)
    return hevy_key, innodigym_token

def sync():
    hevy_key, token = get_credentials()
    mapping = {}
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE) as f: mapping = json.load(f)

    # 1. Fetch latest workout from Hevy
    req = urllib.request.Request("https://api.hevyapp.com/v1/workouts?pageSize=1", headers={"api-key": hevy_key})
    with urllib.request.urlopen(req) as resp:
        workouts = json.loads(resp.read().decode()).get("workouts", [])
    if not workouts: return
    workout = workouts[0]

    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f: state = json.load(f)
    if state.get("last_id") == workout["id"]:
        return  # Workout already processed

    # 2. Extract max working weight in lbs
    hevy_weights = {}
    for ex in workout.get("exercises", []):
        max_kg = max([s.get("weight_kg", 0) or 0 for s in ex.get("sets", [])] + [0])
        if max_kg &gt; 0:
            hevy_weights[ex["title"].strip()] = round(max_kg / 0.45359237)

    # 3. Match with Innodigym custom template
    headers = {"Authorization": token, "Content-Type": "application/json"}
    req = urllib.request.Request(f"{INNODIGYM_BASE}/api/course/custom/list", headers=headers)
    with urllib.request.urlopen(req) as resp:
        templates = json.loads(resp.read().decode()).get("data", [])

    matched = next((t for t in templates if t["name"].strip().lower() == workout["title"].strip().lower()), None)
    if not matched: return

    # 4. Fetch detail, scale weights, and push update
    req = urllib.request.Request(f"{INNODIGYM_BASE}/api/course/custom/detail?id={matched['id']}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        detail = json.loads(resp.read().decode())["data"]

    for step in detail.get("mainStepList", []):
        name = step["actionName"]
        for h_name, weight_lbs in hevy_weights.items():
            if h_name.lower() == name.lower() or mapping.get(h_name.lower(), "").lower() == name.lower():
                step["sideWeight"] = round(weight_lbs * LBS_TO_SERVER_SCALE)

    save_req = urllib.request.Request(f"{INNODIGYM_BASE}/api/course/custom/save", data=json.dumps(detail).encode(), headers=headers)
    with urllib.request.urlopen(save_req) as resp:
        res = json.loads(resp.read().decode())
        print(f"Updated {matched['name']}:", res)

    state["last_id"] = workout["id"]
    state["last_sync"] = datetime.now().isoformat()
    with open(STATE_FILE, "w") as f: json.dump(state, f, indent=2)

if __name__ == "__main__":
    sync()
</code></pre>

<div class="page-break"></div>

<h3><span class="step-number">5</span> Configuring Background Automation</h3>

<h4>A. macOS Setup (via <code>launchd</code>)</h4>
<ol>
  <li>Place <code>sync.py</code> and <code>mapping.json</code> in <code>~/.hevy-innodigym/</code>.</li>
  <li>Create <code>~/Library/LaunchAgents/com.sync.hevy-innodigym.plist</code>:</li>
</ol>
<pre><code>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;Label&lt;/key&gt;
    &lt;string&gt;com.sync.hevy-innodigym&lt;/string&gt;
    &lt;key&gt;ProgramArguments&lt;/key&gt;
    &lt;array&gt;
        &lt;string&gt;/usr/bin/python3&lt;/string&gt;
        &lt;string&gt;/Users/&lt;your-user&gt;/.hevy-innodigym/sync.py&lt;/string&gt;
    &lt;/array&gt;
    &lt;key&gt;StartInterval&lt;/key&gt;
    &lt;integer&gt;600&lt;/integer&gt;
    &lt;key&gt;RunAtLoad&lt;/key&gt;
    &lt;true/&gt;
&lt;/dict&gt;
&lt;/plist&gt;</code></pre>
<ol start="3">
  <li>Activate the daemon:
    <pre><code>launchctl load ~/Library/LaunchAgents/com.sync.hevy-innodigym.plist</code></pre>
  </li>
</ol>

<h4>B. Windows Setup (via Task Scheduler)</h4>
<ol>
  <li>Place <code>sync.py</code>, <code>mapping.json</code>, and <code>config.json</code> in <code>C:\HevySync\</code>.</li>
  <li>Open <strong>Task Scheduler</strong> (<code>taskschd.msc</code>) and select <strong>Create Basic Task</strong>.</li>
  <li><strong>Name:</strong> <code>Hevy Innodigym Sync</code>.</li>
  <li><strong>Trigger:</strong> Select <strong>Daily</strong>, then configure <em>Repeat task every</em> <strong>10 minutes</strong> indefinitely.</li>
  <li><strong>Action:</strong> Select <strong>Start a program</strong>:
    <ul>
      <li><strong>Program/script:</strong> <code>python.exe</code> (or full path, e.g. <code>C:\Python312\python.exe</code>)</li>
      <li><strong>Arguments:</strong> <code>C:\HevySync\sync.py</code></li>
      <li><strong>Start in:</strong> <code>C:\HevySync\</code></li>
    </ul>
  </li>
  <li>Check <strong>Run whether user is logged on or not</strong> and click <strong>Finish</strong>.</li>
</ol>

<h2>5. Daily Usage &amp; Machine Operation</h2>
<ol>
  <li><strong>Work out as normal:</strong> Log sets, reps, and weights in Hevy (on your phone, watch, or PC).</li>
  <li><strong>Finish Workout:</strong> Once completed, Hevy saves the session to its cloud.</li>
  <li><strong>Automatic Background Bridge:</strong> Within 10 minutes, the background sync detects the new session, extracts your heaviest sets, scales them to combined poundage, and updates the Innodigym cloud.</li>
  <li><strong>On the Innodigym X1 Pro Machine:</strong>
    <ul>
      <li>Navigate to your custom routine screen.</li>
      <li><strong>Pull down on the screen to refresh.</strong></li>
      <li>The updated progression weights will instantly display on the dials ready for your next session.</li>
    </ul>
  </li>
</ol>

<div class="callout callout-warn">
  <div class="callout-title">UI Cache Note</div>
  If the desktop or mobile Innodigym app was already open on a specific workout detail screen when the background sync occurred, tap the back arrow (&larr;) and reopen the routine (or restart the app) to see the fresh cloud values. The physical X1 Pro console reloads immediately on pull-to-refresh.
</div>

</body>
</html>
"""

with open(OUTPUT_HTML, "w") as f:
    f.write(html_content)

chrome_cmd = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUTPUT_PDF}",
    f"file://{OUTPUT_HTML}"
]

res = subprocess.run(chrome_cmd, capture_output=True, text=True)
print("Chrome return code:", res.returncode)
if os.path.exists(OUTPUT_PDF):
    print("PDF generated successfully:", OUTPUT_PDF, f"({os.path.getsize(OUTPUT_PDF)} bytes)")
else:
    print("Error generating PDF:", res.stderr)
