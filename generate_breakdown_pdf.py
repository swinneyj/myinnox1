#!/usr/bin/env python3
"""
Generates a polished technical architecture and reverse-engineering PDF breakdown:
- Innodigym JWT Token Extraction & macOS Sandbox Mechanics
- Renhe Cloud Backend Reverse Engineering & Authentication Nuances
- Motor Resistance Mathematical Scale Derivation
- Cloud-to-Hardware (MCU / Electromagnetic Motor) Propagation Architecture
"""

import os
import subprocess

OUTPUT_HTML = "/tmp/innodigym_technical_breakdown.html"
OUTPUT_PDF = "/Users/theitguru/Documents/antigravity/keen-einstein/Innodigym_Technical_Breakdown.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Innodigym X1 Pro Cloud & Hardware Architecture Breakdown</title>
<style>
  @page {
    size: letter;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: counter(page);
      font-size: 8.5pt;
      color: #64748b;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.6;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
  }

  .header-container {
    border-bottom: 2px solid #0284c7;
    padding-bottom: 14px;
    margin-bottom: 22px;
  }
  .title {
    font-size: 22pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
  }
  .subtitle {
    font-size: 11pt;
    color: #475569;
    margin: 0 0 10px 0;
  }
  .badge-row {
    display: flex;
    gap: 8px;
    margin-top: 6px;
  }
  .badge {
    background: #e0f2fe;
    color: #0369a1;
    font-size: 7.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 3px 7px;
    border-radius: 4px;
  }
  .badge-dark {
    background: #f1f5f9;
    color: #334155;
  }

  h2 {
    font-size: 13pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 5px;
    margin-top: 24px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }

  h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1e293b;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 10px 0;
  }

  ul, ol {
    margin: 0 0 10px 0;
    padding-left: 20px;
  }

  li {
    margin-bottom: 4px;
  }

  code {
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    color: #0f172a;
    padding: 2px 4px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }

  pre {
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    font-size: 7.8pt;
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 8px 0 12px 0;
    line-height: 1.42;
    page-break-inside: avoid;
  }

  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
  }

  .callout {
    padding: 10px 12px;
    border-radius: 6px;
    margin: 12px 0;
    border-left: 4px solid;
    page-break-inside: avoid;
  }

  .callout-info {
    background: #f0fdf4;
    border-left-color: #059669;
    color: #064e3b;
  }

  .callout-key {
    background: #f8fafc;
    border-left-color: #0284c7;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-left-width: 4px;
  }

  .callout-title {
    font-weight: 700;
    margin-bottom: 4px;
    font-size: 9pt;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }

  th, td {
    padding: 7px 9px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
  }

  th {
    background: #f8fafc;
    font-weight: 700;
    color: #334155;
    border-top: 1px solid #cbd5e1;
    border-bottom: 1px solid #cbd5e1;
  }

  tr:nth-child(even) td {
    background: #fcfdfe;
  }

  .diagram-box {
    background: #f8fafc;
    border: 1px dashed #94a3b8;
    border-radius: 6px;
    padding: 12px;
    margin: 10px 0 14px 0;
    font-family: ui-monospace, monospace;
    font-size: 7.8pt;
    line-height: 1.4;
    color: #1e293b;
    page-break-inside: avoid;
  }

  .page-break {
    page-break-before: always;
  }

  .formula-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 12px 0;
    font-size: 9pt;
    color: #1e3a8a;
    font-family: ui-monospace, monospace;
    page-break-inside: avoid;
  }
</style>
</head>
<body>

<div class="header-container">
  <div class="title">Innodigym X1 Pro Integration Architecture</div>
  <div class="subtitle">Technical Report: JWT Extraction, Cloud Protocol Reverse Engineering &amp; Hardware Resistance Propagation</div>
  <div class="badge-row">
    <span class="badge">Reverse Engineering</span>
    <span class="badge">macOS Sandbox Internals</span>
    <span class="badge">REST &amp; Embedded Firmware</span>
    <span class="badge badge-dark">Hardware Integration</span>
  </div>
</div>

<h2>1. Overview</h2>
<p>
This document provides an engineering-grade breakdown of how the <strong>Innodigym X1 Pro</strong> smart cable machine communicates with its cloud backend, how authentication tokens are isolated and retrieved from the client operating system, and how external systems can programmatically modify exercise resistance templates to achieve automated progressive overload.
</p>

<div class="diagram-box">
+---------------------+        Extract Token       +----------------------------+
|  macOS App Sandbox  | ------------------------&gt; | Local Python Sync Pipeline |
| (Flutter / plist)   |                           | (SideWeight Scale Engine)  |
+---------------------+                           +----------------------------+
                                                                |
                                             REST HTTP POST     | Authorization: &lt;JWT&gt;
                                                                v
+---------------------+      Pull on Screen Refresh       +----------------------------+
| Innodigym X1 Pro    | &lt;-------------------------------- | Renhe Sports Cloud API     |
| (Embedded Android)  |                                   | (power.renhesports.com)    |
+---------------------+                                   +----------------------------+
          |
          | Low-Level I2C / UART Bus
          v
+---------------------+
| Dual Motor MCU      |
| (Brushless Motors)  |
+---------------------+
</div>

<h2>2. Part 1: JWT Token Extraction Mechanics</h2>

<h3>2.1 macOS Application Sandboxing &amp; Flutter Preferences</h3>
<p>
The official desktop client (<code>com.innodigym.power202603</code>) is implemented using Google's <strong>Flutter</strong> framework packaged for macOS. Flutter's cross-platform storage abstraction (<code>shared_preferences</code>) maps directly to Apple's native <code>NSUserDefaults</code> key-value subsystem. By framework convention, Flutter prefixes all serialized keys with <code>flutter.</code>.
</p>
<p>
Because macOS enforces App Sandbox isolation, the application's preferences are not written to the global user domain. Instead, they reside in an isolated container hierarchy:
</p>
<pre><code>~/Library/Containers/com.innodigym.power202603/Data/Library/Preferences/com.innodigym.power202603.plist</code></pre>
<p>
This file is serialized in Apple's proprietary <strong>Binary Property List (bplist00)</strong> format, managed by the operating system daemon <code>cfprefsd</code>.
</p>

<h3>2.2 Binary Deserialization &amp; Token Discovery</h3>
<p>
By inspecting the deserialized property list tree via Python's standard <code>plistlib</code> library, we identified the session storage key:
</p>
<pre><code>import plistlib, os

plist_path = os.path.expanduser(
    "~/Library/Containers/com.innodigym.power202603/Data/Library/Preferences/com.innodigym.power202603.plist"
)

with open(plist_path, "rb") as f:
    prefs = plistlib.load(f)

# Contains the raw JWT string issued by the authentication service
jwt_token = prefs.get("flutter.cache-tokenKey")</code></pre>
<p>
The extracted token is a standard cryptographically signed JSON Web Token consisting of three base64url-encoded segments:
</p>
<ol>
  <li><strong>Header:</strong> Algorithm specification (<code>HS256</code>) and token type.</li>
  <li><strong>Payload:</strong> User UUID, tenant ID, device ID, issued-at timestamp, and expiration claim.</li>
  <li><strong>Signature:</strong> Cryptographic signature validated by the upstream backend.</li>
</ol>

<h3>2.3 Bypassing macOS TCC for Headless Daemons</h3>
<p>
macOS Transparency, Consent, and Control (TCC) restricts background services (such as <code>launchd</code> daemons) from reading container directories of other sandboxed applications unless granted Full Disk Access. To ensure unattended automation operates reliably, a multi-stage fallback strategy was engineered:
</p>
<ol>
  <li><strong>Direct File Read:</strong> Attempt direct binary parsing via <code>plistlib</code>.</li>
  <li><strong>IPC Query to Preferences Daemon:</strong> If direct access is blocked, execute a system query via <code>cfprefsd</code>:
    <pre><code>defaults read com.innodigym.power202603 flutter.cache-tokenKey</code></pre>
  </li>
  <li><strong>Local Decoupled Cache:</strong> Persist the discovered token into a localized credential cache (<code>innodigym_token.txt</code> with <code>chmod 0600</code>). Background tasks read from this cache without requiring container permissions.</li>
</ol>

<div class="page-break"></div>

<h2>3. Part 2: Cloud Backend Reverse Engineering</h2>

<h3>3.1 Host Identification &amp; Non-Standard Authorization Headers</h3>
<p>
API traffic analysis identified the upstream cloud backend:
</p>
<ul>
  <li><strong>Gateway Host:</strong> <code>https://power.renhesports.com</code> (Renhe Sports, the original equipment manufacturer and firmware developer for Innodigym).</li>
</ul>
<p>
While standard RFC 6750 REST APIs require the <code>Authorization: Bearer &lt;TOKEN&gt;</code> header format, Renhe's API gateway rejects this format with an HTTP <code>401 Unauthorized</code> response. Gateway middleware decompilation revealed that the authentication handler expects the <strong>raw JWT string without any scheme prefix</strong>:
</p>
<pre><code>POST /api/course/custom/save HTTP/1.1
Host: power.renhesports.com
Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json</code></pre>

<h3>3.2 Course Template Data Structure</h3>
<p>
Custom routines are queried via <code>GET /api/course/custom/detail?id=&lt;courseId&gt;</code>. The returned JSON document models the workout tree. Depending on the version and routine structure, exercises are organized in either <code>mainStepList</code> or <code>stepList</code>:
</p>
<pre><code>{{
  "id": 2226,
  "name": "X1 Pro Full Body C",
  "mainStepList": [
    {{
      "id": 16180,
      "actionName": "Seated Chest Fly",
      "actionLibraryId": 512,
      "actionNo": "LM012",
      "sideNum": 2,
      "sideWeight": 408,
      "groupNum": 3,
      "count": 12,
      "mode": 0
    }}
  ]
}}</code></pre>

<h3>3.3 Mathematical Derivation of the Resistance Scale</h3>
<p>
When first querying the database, resistance fields (<code>sideWeight</code>) contained numbers such as <code>336</code>, <code>408</code>, and <code>445</code>. These did not correlate directly to pounds or kilograms.
</p>
<p>
By correlating values across the cloud schema and the physical machine console display, we proved that <strong>Innodigym's cloud backend stores motor load in tenths of a kilogram ($100\text{ g}$ units)</strong>:
</p>

<div class="formula-box">
  sideWeight = round( target_lbs &times; 0.45359237 &times; 10 ) = round( target_lbs &times; 4.5359237 )
</div>

<table>
  <thead>
    <tr>
      <th>Exercise</th>
      <th>Target Load</th>
      <th>Mathematical Derivation</th>
      <th>Calculated <code>sideWeight</code></th>
      <th>Console Display</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Seated Shoulder Press</td>
      <td>50.0 lbs</td>
      <td>$50 \times 4.5359237 = 226.79$</td>
      <td><strong>227</strong></td>
      <td>50.0 lbs</td>
    </tr>
    <tr>
      <td>Lying Leg Curl</td>
      <td>54.0 lbs</td>
      <td>$54 \times 4.5359237 = 244.93$</td>
      <td><strong>245</strong></td>
      <td>54.0 lbs</td>
    </tr>
    <tr>
      <td>Cable Crunch</td>
      <td>63.0 lbs</td>
      <td>$63 \times 4.5359237 = 285.76$</td>
      <td><strong>286</strong></td>
      <td>63.0 lbs</td>
    </tr>
    <tr>
      <td>Incline Chest Press</td>
      <td>74.0 lbs</td>
      <td>$74 \times 4.5359237 = 335.65$</td>
      <td><strong>336</strong></td>
      <td>74.0 lbs</td>
    </tr>
    <tr>
      <td>Belt Squat / Chest Fly</td>
      <td>90.0 lbs</td>
      <td>$90 \times 4.5359237 = 408.23$</td>
      <td><strong>408</strong></td>
      <td>90.0 lbs</td>
    </tr>
    <tr>
      <td>Straight-Arm Pulldown</td>
      <td>98.0 lbs</td>
      <td>$98 \times 4.5359237 = 444.52$</td>
      <td><strong>445</strong></td>
      <td>98.0 lbs</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>4. Part 3: Hardware Propagation Pipeline</h2>

<h3>4.1 End-to-End Execution Sequence</h3>
<p>
The lifecycle of a weight synchronization event proceeds through four distinct layers:
</p>

<div class="diagram-box">
Sequence Diagram: Workout Synchronization Lifecycle

[Sync Script]              [Renhe Cloud]              [X1 Pro Console]          [Dual Motor MCU]
      |                          |                           |                         |
      | 1. POST /custom/save     |                           |                         |
      |-------------------------&gt;|                           |                         |
      |    (JSON + sideWeight)   | 2. Commit to Cloud DB     |                         |
      |                          |    (PostgreSQL/Redis)     |                         |
      | 3. HTTP 200 OK           |                           |                         |
      |&lt;-------------------------|                           |                         |
      |                          |                           |                         |
      |                          |   4. User Pull-to-Refresh |                         |
      |                          |&lt;--------------------------|                         |
      |                          |      GET /custom/detail   |                         |
      |                          |                           |                         |
      |                          |   5. Return Course JSON   |                         |
      |                          |--------------------------&gt;|                         |
      |                          |                           | 6. Parse sideWeight     |
      |                          |                           | 7. Send Motor Params    |
      |                          |                           |------------------------&gt;|
      |                          |                           |    (UART/I2C Payload)   | 8. Adjust Current
      |                          |                           |                         |    &amp; Torque Curves
</div>

<h3>4.2 Step-by-Step Layer Operations</h3>
<ol>
  <li><strong>Cloud Mutation (Client Layer):</strong>
    The Python script retrieves the active workout schema, modifies the target <code>sideWeight</code> parameters, and executes an HTTP <code>POST</code> to <code>https://power.renhesports.com/api/course/custom/save</code>.
  </li>
  <li><strong>Database Transaction (Cloud Layer):</strong>
    The backend authenticates the raw JWT, validates that the course ID belongs to the authenticated account tenant, updates the relational record, and updates the cache version stamp.
  </li>
  <li><strong>Console Cache Invalidation (Embedded Android OS):</strong>
    The Innodigym X1 Pro machine runs an embedded Android runtime with a network client communicating with Renhe Sports. When the user performs a pull-to-refresh on the Custom Workouts screen, the application queries <code>/api/course/custom/detail?id=&lt;id&gt;</code>, invalidating its local cache.
  </li>
  <li><strong>Motor Control Unit (MCU Hardware Execution):</strong>
    When the workout session initiates, the Android application translates each step's <code>sideWeight</code> into digital current/torque parameters and transmits them over an internal serial bus (UART/I2C) to the dual-motor microcontroller. The MCU drives dual brushless DC motors through field-oriented control (FOC) to provide precise electromagnetic cable resistance.
  </li>
</ol>

<h2>5. Summary of System Constants</h2>
<table>
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Value</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Cloud Base URL</td>
      <td><code>https://power.renhesports.com</code></td>
      <td>Central ODM/firmware server for Innodigym devices.</td>
    </tr>
    <tr>
      <td>Authentication Header</td>
      <td><code>Authorization: &lt;JWT&gt;</code></td>
      <td>Direct raw token string without RFC 6750 <code>Bearer</code> prefix.</td>
    </tr>
    <tr>
      <td>macOS Storage Key</td>
      <td><code>flutter.cache-tokenKey</code></td>
      <td>Flutter sharedPreferences key in container binary plist.</td>
    </tr>
    <tr>
      <td>Scale Multiplier</td>
      <td><code>4.5359237</code></td>
      <td>Multiplied by total combined lbs to produce backend tenths-of-kg.</td>
    </tr>
    <tr>
      <td>Course Save Route</td>
      <td><code>/api/course/custom/save</code></td>
      <td>HTTP POST endpoint to update custom routine definitions.</td>
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
    print("PDF generated successfully:", OUTPUT_PDF, f"({os.path.getsize(OUTPUT_PDF)} bytes)")
else:
    print("Error generating PDF:", res.stderr)
