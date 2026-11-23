#!/usr/bin/env python3
"""
Generates the Complete, Privacy-Clean Ecosystem Guide for InnoStudio, OpenGym, and Innodigym X1 Pro.
100% Generic - Zero personal emails, account names, IPs, or private tokens.
"""

import os
import html
import subprocess

BASE_DIR = "/Users/theitguru/Documents/antigravity/keen-einstein"
OUTPUT_HTML = "/tmp/innostudio_opengym_ecosystem_guide.html"
OUTPUT_PDF = os.path.join(BASE_DIR, "InnoStudio_OpenGym_Ecosystem_Guide.pdf")

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>InnoStudio & OpenGym: Complete Self-Hosted Ecosystem Guide</title>
<style>
  @page {
    size: letter;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: "Page " counter(page) " of " counter(pages);
      font-size: 8.5pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #64748b;
    }
    @bottom-left {
      content: "InnoStudio & OpenGym Complete Ecosystem Guide";
      font-size: 8.5pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #64748b;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
  }

  .cover {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 85vh;
    padding: 40px 20px;
    border-left: 6px solid #0d9488;
    background: linear-gradient(to bottom right, #f8fafc, #f1f5f9);
    border-radius: 0 16px 16px 0;
  }

  .badge-tag {
    display: inline-block;
    background: #0d9488;
    color: #ffffff;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 6px;
    margin-bottom: 20px;
    width: fit-content;
  }

  h1.cover-title {
    font-size: 28pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
    margin: 0 0 14px 0;
    letter-spacing: -0.02em;
  }

  p.cover-subtitle {
    font-size: 13pt;
    color: #475569;
    margin: 0 0 30px 0;
    line-height: 1.45;
  }

  .cover-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 30px;
    margin-bottom: 40px;
  }

  .cover-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 14px 18px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  }

  .cover-card h4 {
    margin: 0 0 4px 0;
    font-size: 10.5pt;
    color: #0d9488;
  }

  .cover-card p {
    margin: 0;
    font-size: 8.5pt;
    color: #64748b;
  }

  .cover-meta {
    font-size: 9pt;
    color: #64748b;
    border-top: 1px solid #cbd5e1;
    padding-top: 18px;
  }

  h2 {
    font-size: 15pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 1.5px solid #0d9488;
    padding-bottom: 5px;
    margin-top: 26pt;
    margin-bottom: 12pt;
    page-break-after: avoid;
    break-after: avoid;
  }

  h3 {
    font-size: 11.5pt;
    font-weight: 600;
    color: #1e293b;
    margin-top: 14pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
    break-after: avoid;
  }

  p {
    margin: 0 0 9pt 0;
  }

  ul, ol {
    margin: 0 0 10pt 0;
    padding-left: 20px;
  }

  li {
    margin-bottom: 4pt;
  }

  code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    color: #0f766e;
    padding: 1.5px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }

  pre {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 8pt;
    background: #0f172a;
    color: #f8fafc;
    padding: 12px 14px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 0 0 12pt 0;
    line-height: 1.45;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
  }

  .alert {
    padding: 10px 14px;
    border-radius: 8px;
    margin: 10pt 0;
    font-size: 9pt;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .alert.note {
    background: #f0fdfa;
    border-left: 4px solid #0d9488;
    color: #134e4a;
  }

  .alert.tip {
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    color: #14532d;
  }

  .alert.warning {
    background: #fffbeb;
    border-left: 4px solid #d97706;
    color: #78350f;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0 14pt 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  th {
    background: #0f172a;
    color: #ffffff;
    text-align: left;
    padding: 7px 10px;
    font-weight: 600;
  }

  td {
    padding: 6px 10px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }

  tr:nth-child(even) td {
    background: #f8fafc;
  }

  .diagram-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 14px;
    margin: 12pt 0;
    font-family: "SFMono-Regular", Consolas, monospace;
    font-size: 8pt;
    line-height: 1.4;
    color: #334155;
    white-space: pre;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .page-break {
    page-break-after: always;
    break-after: always;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <div class="badge-tag">Production Reference Architecture</div>
  <h1 class="cover-title">InnoStudio & OpenGym<br>Ecosystem Guide</h1>
  <p class="cover-subtitle">Complete Implementation Blueprint for Self-Hosted Program Management, Multi-App Workout Tracking, and Motor Resistance Cloud Synchronization on the Innodigym X1 Pro.</p>

  <div class="cover-grid">
    <div class="cover-card">
      <h4>1. InnoStudio Console</h4>
      <p>Self-hosted private web client, zero-password token injection, multi-week planner, 83 CDN covers, and fullscreen preview.</p>
    </div>
    <div class="cover-card">
      <h4>2. OpenGym Self-Hosted</h4>
      <p>Independent Docker workout logger with Apple Watch support, multi-device sync, and zero cloud lock-in.</p>
    </div>
    <div class="cover-card">
      <h4>3. Dual Auto-Sync Daemon</h4>
      <p>Concurrent monitoring of Hevy & OpenGym with automatic working weight extraction and motor resistance scaling.</p>
    </div>
    <div class="cover-card">
      <h4>4. Port 443 Tailnet Mesh</h4>
      <p>Encrypted cellular & Wi-Fi access via Tailscale Serve without custom port filtering or open firewall ports.</p>
    </div>
  </div>

  <div class="cover-meta">
    <strong>Author:</strong> Independent Hardware & Software Engineering Reference<br>
    <strong>Target Hardware:</strong> Innodigym X1 Pro / P1 Max | UGREEN / Synology NAS | macOS / Linux / Windows<br>
    <strong>Confidentiality:</strong> 100% Generic & Privacy-Sanitized (Zero hardcoded credentials or IP addresses)
  </div>
</div>

<!-- SECTION 1: ARCHITECTURE OVERVIEW -->
<h2>1. Architectural Overview & System Design</h2>

<p>The official Innodigym ecosystem imposes several critical operational limitations: custom workout programs cannot be edited once saved (requiring full deletion and recreation), the training calendar only allows scheduling Day 1 of a multi-day split, and workout weights must be manually dialed into the machine every single workout. Furthermore, third-party cloud web clients often route raw user credentials through intermediate edge proxies.</p>

<p>This reference architecture establishes a <strong>100% private, self-hosted smart home gym stack</strong> comprising four tightly integrated components:</p>

<div class="diagram-box">
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                    USER INTERFACES                                     │
│                                                                                        │
│   ┌───────────────────────────────┐               ┌────────────────────────────────┐   │
│   │   InnoStudio Web Console      │               │   OpenGym Mobile & Watch App   │   │
│   │   • Visual Drag-and-Drop      │               │   • Live Gym Floor Logging     │   │
│   │   • 83 Machine Covers (Zoom)  │               │   • Apple Watch Complications  │   │
│   │   • Multi-Week Program Blocks │               │   • Set, Rep, and RPE Tracking │   │
│   └──────────────┬────────────────┘               └───────────────┬────────────────┘   │
└──────────────────┼────────────────────────────────────────────────┼────────────────────┘
                   │                                                │
┌──────────────────▼────────────────────────────────────────────────▼────────────────────┐
│                              LOCAL SERVICES & STORAGE                                  │
│                                                                                        │
│   ┌───────────────────────────────┐               ┌────────────────────────────────┐   │
│   │   InnoStudio Proxy Server     │◄─────────────►│   OpenGym Docker Service       │   │
│   │   • Port 8085 / LaunchAgent   │  Bridge API   │   • Port 8080 (Docker on NAS)  │   │
│   │   • Auto-Token Injection      │               │   • SQLite / JSON State Store  │   │
│   └──────────────┬────────────────┘               └───────────────┬────────────────┘   │
│                  │                                                │                    │
│                  │         ┌───────────────────────────────┐      │                    │
│                  │         │   Dual Auto-Sync Engine       │◄─────┘                    │
│                  └────────►│   • Monitors Hevy & OpenGym   │                           │
│                            │   • Calculates Motor Units    │                           │
│                            └──────────────┬────────────────┘                           │
└───────────────────────────────────────────┼────────────────────────────────────────────┘
                                            │ Direct HTTPS
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                                 HARDWARE CLOUD                                         │
│                                                                                        │
│                     Innodigym Renhe Cloud (power.renhesports.com)                      │
│                                           │                                            │
│                                           ▼ Pull-down Sync                             │
│                     Physical Innodigym X1 Pro Machine Console                          │
│                     • Dual Motors Automatically Set to Working Weights                 │
└────────────────────────────────────────────────────────────────────────────────────────┘
</div>

<div class="alert note">
  <strong>Security Guarantee:</strong> All communication with the Innodigym API occurs directly between your local host machine and the official endpoint (<code>power.renhesports.com</code>). Zero credentials, tokens, or workout telemetry ever traverse third-party servers.
</div>

<div class="page-break"></div>

<!-- SECTION 2: OPENGYM SETUP -->
<h2>2. OpenGym: Self-Hosted Docker Deployment</h2>

<p>OpenGym provides a fast, lightweight, and independent workout logging platform with full PWA and Apple Watch support. It runs as a self-contained container on your NAS or local server.</p>

<h3>2.1 Docker Compose Specification</h3>
<p>Create a directory on your NAS or server (e.g., <code>/volume1/docker/opengym</code>) and save the following <code>docker-compose.yml</code>:</p>

<pre><code>version: "3.8"

services:
  opengym:
    image: ghcr.io/opengym-app/opengym:latest
    container_name: opengym
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./data:/app/data
    environment:
      - TZ=America/New_York
      # Optional: set a passphrase for local LAN multi-user separation
      # - OPENGYM_PASSPHRASE=&lt;OPTIONAL_PASSPHRASE&gt;
</code></pre>

<h3>2.2 Deploying the Container</h3>
<pre><code># Start the stack in background mode
docker compose up -d

# Verify container status
docker ps --filter "name=opengym"
</code></pre>

<h3>2.3 Mobile Pairing & API Authentication</h3>
<p>To enable automated synchronization scripts to interact with OpenGym without hardcoded passwords, OpenGym uses a short pairing code exchanged for a persistent Bearer token:</p>
<ol>
  <li>Open your browser to <code>http://&lt;NAS_IP&gt;:8080</code>.</li>
  <li>Navigate to <strong>Settings</strong> &rarr; <strong>Pair the mobile app</strong>.</li>
  <li>Note the temporary 6-letter pairing code (e.g., <code>K8X2W9</code>).</li>
  <li>Exchange the code for a permanent session token using Python or curl:</li>
</ol>

<pre><code># Exchange 6-letter code for persistent token
curl -X POST "http://&lt;NAS_IP&gt;:8080/api/pair" \
     -H "Content-Type: application/json" \
     -d '{"code":"K8X2W9"}'
</code></pre>

<p>Save the resulting token string into <code>opengym_token.txt</code> alongside a configuration file <code>opengym_config.json</code>:</p>

<pre><code>{
  "url": "http://&lt;NAS_IP&gt;:8080"
}
</code></pre>

<!-- SECTION 3: INNOSTUDIO SETUP -->
<h2>3. InnoStudio: Private Web Console & Reverse Proxy</h2>

<p>InnoStudio is a clean, client-side web application coupled with a local Python micro-server that gives you complete control over your X1 Pro custom programs, exercises, and multi-week plans.</p>

<h3>3.1 Core Capabilities</h3>
<ul>
  <li><strong>Full Program Editing:</strong> Modify sets, reps, rest timers, and weights on existing routines without recreating them.</li>
  <li><strong>Automatic Authentication:</strong> Automatically reads your cached JWT token from <code>token.json</code> upon page load—no login credentials required.</li>
  <li><strong>83 Machine-Supported Covers:</strong> Seamlessly switch between the 8 official high-resolution room setups and all 75 movement artwork covers with real-time fullscreen zoom.</li>
  <li><strong>OpenGym Bridge:</strong> 1-click routine export to OpenGym and live weight synchronization triggers.</li>
</ul>

<h3>3.2 Directory Layout</h3>
<pre><code>~/.innox1/
├── innodigym_token.txt      # Raw Innodigym JWT token
├── opengym_token.txt        # OpenGym Bearer session token
├── opengym_config.json      # Endpoint configuration ({"url":"http://&lt;NAS_IP&gt;:8080"})
├── opengym_catalog.json     # OpenGym 5,600+ exercise taxonomy database
├── mapping.json             # Exercise name translation dictionary
├── sync.py                  # Dual Hevy + OpenGym auto-sync engine
├── opengym_bridge.py        # Bridge API module
├── serve_innox1.py          # Local web server & proxy daemon
└── myinnox1-local/          # Web frontend static assets (HTML, CSS, JS, vendor)
</code></pre>

<div class="page-break"></div>

<!-- SECTION 4: TAILSCALE PORT 443 -->
<h2>4. Secure Remote Access: Tailscale Serve on Port 443</h2>

<p>Accessing self-hosted gym tools outside the home typically introduces complex hurdles: router port forwarding exposes attack surfaces, dynamic DNS updates fail, and cellular carriers frequently filter non-standard high ports (e.g., <code>:8085</code>, <code>:8089</code>), causing mobile Safari to drop connections.</p>

<p>Tailscale Serve solves this by routing traffic over your private WireGuard mesh on <strong>Standard HTTPS Port 443</strong> under a dedicated subpath.</p>

<div class="diagram-box">
iPhone (Cellular / Anywhere)
  │  https://&lt;NODE_NAME&gt;.ts.net/gym/
  │  (Standard Port 443 · WireGuard Encrypted · Valid Let's Encrypt SSL)
  ▼
Tailscale Network Extension on Host Machine
  │
  ├─ Path /    ──► Forward to Service A (e.g., 127.0.0.1:54450)
  └─ Path /gym ──► Forward to InnoStudio (127.0.0.1:8085)
                     │
                     ▼
             Direct Cloud API to Innodigym (power.renhesports.com)
</div>

<h3>4.1 Configuring the Subpath Proxy</h3>
<p>Execute the following command on the host running InnoStudio (e.g., your Mac mini or home server):</p>

<pre><code># Map incoming HTTPS port 443 /gym requests to local port 8085
tailscale serve --set-path=/gym --bg 8085

# Verify active serve configuration
tailscale serve status
</code></pre>

<p>The status command will confirm the multiplexed path:</p>
<pre><code>https://&lt;YOUR_NODE&gt;.tailxxxxxx.ts.net/
|-- /    proxy http://127.0.0.1:&lt;EXISTING_SERVICE&gt;
|-- /gym proxy http://127.0.0.1:8085
</code></pre>

<h3>4.2 Installing as an iOS Progressive Web App (PWA)</h3>
<ol>
  <li>Ensure the <strong>Tailscale app</strong> is installed and connected on your iPhone.</li>
  <li>Open Safari and navigate to: <code>https://&lt;YOUR_NODE&gt;.tailxxxxxx.ts.net/gym/</code></li>
  <li>Tap the <strong>Share</strong> icon (square with arrow pointing up).</li>
  <li>Scroll down and tap <strong>Add to Home Screen</strong>.</li>
  <li>Confirm the title (e.g., <em>InnoStudio</em>). The app now launches full-screen with native gestures and zero browser chrome.</li>
</ol>

<!-- SECTION 5: OPENGYM BRIDGE -->
<h2>5. The InnoStudio & OpenGym Bridge Integration</h2>

<p>Because InnoStudio's micro-server runs locally on your machine, it exposes custom bridge endpoints that unify your workout lifecycle.</p>

<div class="diagram-box">
┌────────────────────────────────────────────────────────────────────────┐
│                        WORKOUT LIFECYCLE                               │
│                                                                        │
│   1. PLAN & ORGANIZE:  InnoStudio Web Console                          │
│      Build routines visually, drag-and-drop steps, select cover art.   │
│                                                                        │
│   2. 1-CLICK PUSH:     Tap "📲 OpenGym" in InnoStudio                  │
│      Routine templates & target reps push instantly into OpenGym.      │
│                                                                        │
│   3. TRAIN & LOG:      OpenGym on Apple Watch / iPhone                 │
│      Log working sets, RPE, and heaviest weights on the gym floor.     │
│                                                                        │
│   4. AUTO-SYNC:        Background Sync Daemon (Every 5 mins)           │
│      Extracts completed session weights and pushes to X1 Pro motors.   │
└────────────────────────────────────────────────────────────────────────┘
</div>

<h3>5.1 Bridge REST Endpoints</h3>
<table>
  <thead>
    <tr>
      <th>Endpoint</th>
      <th>Method</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>/api/opengym/status</code></td>
      <td><code>GET</code></td>
      <td>Pings the OpenGym Docker instance and returns connection status, routine count, and last sync timestamp.</td>
    </tr>
    <tr>
      <td><code>/api/opengym/routines</code></td>
      <td><code>GET</code></td>
      <td>Fetches all routine definitions from OpenGym's JSON state store.</td>
    </tr>
    <tr>
      <td><code>/api/opengym/push-course</code></td>
      <td><code>POST</code></td>
      <td>Takes <code>{"courseId": &lt;ID&gt;}</code>, maps exercises to OpenGym taxonomy, and inserts/updates the routine in OpenGym.</td>
    </tr>
    <tr>
      <td><code>/api/opengym/import-routine</code></td>
      <td><code>POST</code></td>
      <td>Takes <code>{"routineId": &lt;ID&gt;}</code>, converts OpenGym exercises, sets, reps, and weights into an Innodigym custom course, and uploads it directly to the machine console via <code>/api/course/custom/save</code>.</td>
    </tr>
    <tr>
      <td><code>/api/opengym/sync-weights</code></td>
      <td><code>POST</code></td>
      <td>Executes <code>sync.py --apply</code> immediately on demand, returning updated exercise resistances.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 6: DUAL SYNC ENGINE -->
<h2>6. The Dual Background Auto-Sync Engine</h2>

<p>The background sync daemon operates as an autonomous reconciliation engine. It monitors both Hevy and OpenGym, determines which workout was completed most recently, extracts the heaviest working sets, and updates the Innodigym cloud template.</p>

<h3>6.1 The Innodigym Resistance Formula</h3>
<p>The Innodigym backend stores motor resistance in tenths of a kilogram (server units) per cable side. The exact conversion formula is:</p>

<pre><code># 1 lb = 0.45359237 kg * 10 = 4.5359237 server units
sideWeight = round(target_lbs * 4.5359237)
</code></pre>

<table>
  <thead>
    <tr>
      <th>Logged Dumbbell / Cable Weight</th>
      <th>Equivalent Total Resistance</th>
      <th>Innodigym <code>sideWeight</code> (Tenths of kg)</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>45 lbs</td><td>45 lbs</td><td><strong>204</strong></td></tr>
    <tr><td>50 lbs</td><td>50 lbs</td><td><strong>227</strong></td></tr>
    <tr><td>63 lbs</td><td>63 lbs</td><td><strong>286</strong></td></tr>
    <tr><td>90 lbs</td><td>90 lbs</td><td><strong>408</strong></td></tr>
    <tr><td>98 lbs</td><td>98 lbs</td><td><strong>445</strong></td></tr>
    <tr><td>165 lbs</td><td>165 lbs</td><td><strong>748</strong></td></tr>
  </tbody>
</table>

<h3>6.2 Exercise Alias Mapping (<code>mapping.json</code>)</h3>
<p>Because exercise naming conventions vary between workout apps and Innodigym's action library, <code>mapping.json</code> normalizes titles before resistance updates are applied:</p>

<pre><code>{
  "hip thrust (belt)": "Belt Hip Thrust",
  "incline chest press (cable)": "Incline Bench Press (Bar)",
  "seated cable row - bar grip": "Seated Row",
  "reverse lunge (dumbbell)": "Weighted Reverse Lunge",
  "standing calf raise (cable)": "Weighted Calf Raise",
  "belt squat (machine)": "Belt Squat",
  "belt squat (cable)": "Belt Squat",
  "belt squat": "Belt Squat",
  "bench press (cable)": "Seated Chest Press",
  "seated chest press": "Seated Chest Press",
  "lat pulldown (cable)": "Close-Grip Reverse Pulldown",
  "close-grip reverse pulldown": "Close-Grip Reverse Pulldown",
  "seated chest flys (cable)": "Seated Chest Fly",
  "seated chest fly": "Seated Chest Fly",
  "standing cable fly": "Standing Cable Fly",
  "seated shoulder cable press": "Seated Alternating Shoulder Press",
  "seated shoulder press (cable)": "Seated Shoulder Press",
  "seated shoulder press": "Seated Shoulder Press",
  "seated alternating shoulder press": "Seated Alternating Shoulder Press",
  "face pull": "Face Pull",
  "rope cable curl": "Biceps Curl",
  "triceps rope pushdown": "Triceps Pushdown",
  "lying leg curl": "Lying Leg Curl",
  "cable crunch": "Rope Crunch",
  "rope crunch": "Rope Crunch",
  "seated lat pulldown": "Straight-Arm Pulldown",
  "straight-arm pulldown": "Straight-Arm Pulldown"
}
</code></pre>

<!-- SECTION 7: PERSISTENT BACKGROUND SERVICES -->
<h2>7. Daemon Scheduling & Automation</h2>

<h3>7.1 macOS LaunchAgent (InnoStudio Web Server)</h3>
<p>Create <code>~/Library/LaunchAgents/com.user.innostudio-web.plist</code>:</p>

<pre><code>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;Label&lt;/key&gt;
    &lt;string&gt;com.user.innostudio-web&lt;/string&gt;
    &lt;key&gt;ProgramArguments&lt;/key&gt;
    &lt;array&gt;
        &lt;string&gt;/usr/bin/python3&lt;/string&gt;
        &lt;string&gt;/Users/USER/.innox1/serve_innox1.py&lt;/string&gt;
    &lt;/array&gt;
    &lt;key&gt;WorkingDirectory&lt;/key&gt;
    &lt;string&gt;/Users/USER/.innox1&lt;/string&gt;
    &lt;key&gt;RunAtLoad&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;KeepAlive&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;StandardOutPath&lt;/key&gt;
    &lt;string&gt;/Users/USER/.innox1/web.log&lt;/string&gt;
    &lt;key&gt;StandardErrorPath&lt;/key&gt;
    &lt;string&gt;/Users/USER/.innox1/web.err&lt;/string&gt;
&lt;/dict&gt;
&lt;/plist&gt;
</code></pre>

<h3>7.2 macOS LaunchAgent (Dual Sync Daemon)</h3>
<p>Create <code>~/Library/LaunchAgents/com.user.workout-sync.plist</code> to run every 5 minutes:</p>

<pre><code>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;Label&lt;/key&gt;
    &lt;string&gt;com.user.workout-sync&lt;/string&gt;
    &lt;key&gt;ProgramArguments&lt;/key&gt;
    &lt;array&gt;
        &lt;string&gt;/usr/bin/python3&lt;/string&gt;
        &lt;string&gt;/Users/USER/.innox1/sync.py&lt;/string&gt;
        &lt;string&gt;--apply&lt;/string&gt;
    &lt;/array&gt;
    &lt;key&gt;StartInterval&lt;/key&gt;
    &lt;integer&gt;300&lt;/integer&gt;
    &lt;key&gt;RunAtLoad&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;StandardOutPath&lt;/key&gt;
    &lt;string&gt;/Users/USER/.innox1/sync.log&lt;/string&gt;
    &lt;key&gt;StandardErrorPath&lt;/key&gt;
    &lt;string&gt;/Users/USER/.innox1/sync.err&lt;/string&gt;
&lt;/dict&gt;
&lt;/plist&gt;
</code></pre>

<p>Load both agents into launchd:</p>
<pre><code>launchctl load ~/Library/LaunchAgents/com.user.innostudio-web.plist
launchctl load ~/Library/LaunchAgents/com.user.workout-sync.plist
</code></pre>

<div class="page-break"></div>

<!-- SECTION 8: HARDWARE REFRESH & VERIFICATION -->
<h2>8. Physical X1 Pro Console Verification</h2>

<p>When the background sync engine modifies your custom templates via the Renhe API, the physical console updates via pull-down refresh:</p>

<ol>
  <li>Power on your <strong>Innodigym X1 Pro</strong>.</li>
  <li>From the main screen, tap <strong>Custom Programs</strong>.</li>
  <li>Perform a <strong>pull-down gesture</strong> on the screen to trigger a fresh cloud synchronisation.</li>
  <li>Tap into your updated routine (e.g., <em>X1 Pro Full Body C</em>).</li>
  <li>Verify that the digital motor resistance sliders for each movement match your latest logged working weights.</li>
</ol>

<!-- SECTION 9: TROUBLESHOOTING -->
<h2>9. Operational Troubleshooting Reference</h2>

<table>
  <thead>
    <tr>
      <th>Symptom</th>
      <th>Underlying Root Cause</th>
      <th>Corrective Action</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Web client fails to connect on cellular data</td>
      <td>Cellular carrier port filtering or raw IP SSL handshake error</td>
      <td>Access exclusively via <code>https://&lt;NODE&gt;.ts.net/gym/</code> on standard port 443 with Tailscale active.</td>
    </tr>
    <tr>
      <td><code>401 Unauthorized</code> (Innodigym API)</td>
      <td>Expired JWT token in <code>innodigym_token.txt</code></td>
      <td>Extract a fresh token from the official mobile app or desktop companion and update <code>innodigym_token.txt</code>.</td>
    </tr>
    <tr>
      <td><code>401 Unauthorized</code> (OpenGym)</td>
      <td>Expired or invalid Bearer token</td>
      <td>Generate a new 6-letter pairing code in OpenGym Settings &rarr; Pair mobile app, and re-pair.</td>
    </tr>
    <tr>
      <td><code>[Errno 1] Operation not permitted</code></td>
      <td>macOS TCC sandbox blocking LaunchAgents from <code>~/Documents</code></td>
      <td>Store all operational scripts and configuration files in <code>~/.innox1/</code> outside the Documents sandbox.</td>
    </tr>
    <tr>
      <td>Exercise weight does not update</td>
      <td>Exercise name discrepancy between app and Innodigym catalog</td>
      <td>Add the exact app name and Innodigym action name to <code>mapping.json</code>.</td>
    </tr>
  </tbody>
</table>

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
    size_kb = os.path.getsize(OUTPUT_PDF) // 1024
    print(f"SUCCESS: PDF generated at: {OUTPUT_PDF} ({size_kb} KB)")
else:
    print("FAILED:", res.stderr)
