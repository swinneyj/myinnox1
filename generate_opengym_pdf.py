#!/usr/bin/env python3
"""
Generates a polished, professional PDF guide for the OpenGym <-> Innodigym X1 Pro Sync System.
Includes full production script source code, mapping configuration, Docker compose, and cross-platform instructions.
"""

import os
import html
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_HTML = "/tmp/opengym_innodigym_guide.html"
OUTPUT_PDF = os.path.join(BASE_DIR, "OpenGym_Innodigym_Sync_Guide.pdf")

# Read local script files dynamically
with open(os.path.join(BASE_DIR, "opengym_sync.py")) as f:
    opengym_sync_code = html.escape(f.read())

with open(os.path.join(BASE_DIR, "mapping.json")) as f:
    mapping_json_code = html.escape(f.read())

with open(os.path.join(BASE_DIR, "docker-compose.opengym.yml")) as f:
    docker_compose_code = html.escape(f.read())

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>OpenGym to Innodigym X1 Pro Integration Guide</title>
<style>
  @page {{
    size: letter;
    margin: 16mm 14mm 16mm 14mm;
    @bottom-right {{
      content: counter(page);
      font-size: 8.5pt;
      color: #64748b;
    }}
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.5;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
  }}

  /* Header Cover Area */
  .header-container {{
    border-bottom: 2px solid #059669;
    padding-bottom: 14px;
    margin-bottom: 20px;
  }}
  .title {{
    font-size: 22pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
  }}
  .subtitle {{
    font-size: 11pt;
    color: #475569;
    margin: 0 0 10px 0;
  }}
  .badge-row {{
    display: flex;
    gap: 8px;
    margin-top: 6px;
  }}
  .badge {{
    background: #d1fae5;
    color: #065f46;
    font-size: 7.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 3px 7px;
    border-radius: 4px;
  }}
  .badge-dark {{
    background: #f1f5f9;
    color: #334155;
  }}

  h2 {{
    font-size: 13pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 5px;
    margin-top: 22px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }}

  h3 {{
    font-size: 10.5pt;
    font-weight: 700;
    color: #1e293b;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }}

  p {{
    margin: 0 0 8px 0;
  }}

  ul, ol {{
    margin: 0 0 10px 0;
    padding-left: 20px;
  }}

  li {{
    margin-bottom: 4px;
  }}

  code {{
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    font-size: 8pt;
    background: #f1f5f9;
    color: #0f172a;
    padding: 2px 4px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}

  pre {{
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    font-size: 7.2pt;
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 8px 0 12px 0;
    line-height: 1.38;
    page-break-inside: avoid;
  }}

  pre.long-code {{
    page-break-inside: auto;
    font-size: 6.8pt;
    line-height: 1.32;
    padding: 10px;
  }}

  pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
  }}

  .callout {{
    padding: 10px 12px;
    border-radius: 6px;
    margin: 12px 0;
    border-left: 4px solid;
    page-break-inside: avoid;
  }}

  .callout-info {{
    background: #f0fdf4;
    border-left-color: #059669;
    color: #064e3b;
  }}

  .callout-warn {{
    background: #fffbeb;
    border-left-color: #f59e0b;
    color: #78350f;
  }}

  .callout-key {{
    background: #f8fafc;
    border-left-color: #0284c7;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-left-width: 4px;
  }}

  .callout-title {{
    font-weight: 700;
    margin-bottom: 4px;
    font-size: 9pt;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 8pt;
    page-break-inside: avoid;
  }}

  th, td {{
    padding: 6px 8px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
  }}

  th {{
    background: #f8fafc;
    font-weight: 700;
    color: #334155;
    border-top: 1px solid #cbd5e1;
    border-bottom: 1px solid #cbd5e1;
  }}

  tr:nth-child(even) td {{
    background: #fcfdfe;
  }}

  .page-break {{
    page-break-before: always;
  }}

  .diagram-box {{
    background: #f8fafc;
    border: 1px dashed #94a3b8;
    border-radius: 6px;
    padding: 10px;
    margin: 10px 0 14px 0;
    font-family: ui-monospace, monospace;
    font-size: 7.5pt;
    line-height: 1.35;
    color: #1e293b;
    page-break-inside: avoid;
  }}
</style>
</head>
<body>

<div class="header-container">
  <div class="title">OpenGym &harr; Innodigym X1 Pro Sync Guide</div>
  <div class="subtitle">Complete Setup: Self-Hosted Docker Deployment, Progressive Overload Tracking &amp; Machine Cloud Automation</div>
  <div class="badge-row">
    <span class="badge">100% Free &amp; Open Source</span>
    <span class="badge">Docker / Dockhand</span>
    <span class="badge">Mac &amp; Windows Compatible</span>
    <span class="badge badge-dark">Full Source Code Included</span>
  </div>
</div>

<h2>1. Overview &amp; Architecture</h2>
<p>
This guide details how to replace proprietary, paid fitness trackers with <strong>OpenGym</strong>—a free, open-source fitness platform running inside Docker (on a local machine, NAS, or home server via <strong>Dockhand</strong> or Portainer)—and automatically synchronize working weights with the <strong>Innodigym X1 Pro</strong> smart home gym.
</p>
<p>
Whenever a workout is completed in OpenGym (via web, iPhone, Apple Watch, or Android app), the sync engine extracts the heaviest working weight logged for each exercise and updates the corresponding custom workout templates in the Innodigym cloud.
</p>

<div class="diagram-box">
[ User Logs Workout ] &rarr; ( OpenGym App / Web )<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&darr;<br>
[ Docker Stack: Dockhand / NAS ] &rarr; OpenGym API (GET /api/data)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&darr;<br>
[ Local Python Engine: opengym_sync.py ] &rarr; Calculates Combined Lbs &rarr; Server Units<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&darr;<br>
[ Innodigym Cloud API ] &rarr; POST /api/course/custom/save (Auth: JWT)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&darr;<br>
[ Innodigym X1 Pro Physical Machine ] &rarr; Dials update on Pull-Down Refresh
</div>

<div class="callout callout-key">
  <div class="callout-title">The Resistance Conversion Formula</div>
  The Innodigym X1 Pro backend internally stores motor resistance in <strong>tenths of a kilogram</strong>:
  <br>
  <code>sideWeight = round(target_lbs &times; 4.5359237)</code>
  <br>
  <em>Example:</em> A <strong>74 lb</strong> bench press requires <code>336</code> server units. The sync engine automatically performs this conversion, ensuring that all templates display exact combined pounds.
</div>

<h2>2. Phase 1: Deploying OpenGym on Docker (Dockhand / NAS)</h2>
<p>
OpenGym is deployed as a lightweight two-container stack (API backend + Web frontend with exercise animations).
</p>

<h3>Docker Compose Stack Specification</h3>
<pre><code>{docker_compose_code}</code></pre>

<h3>Deployment Steps (Dockhand / Portainer):</h3>
<ol>
  <li>Open your Docker management UI (e.g. <strong>Dockhand</strong> at <code>http://&lt;HOST_IP&gt;:3866</code>).</li>
  <li>Navigate to <strong>Stacks</strong> &rarr; <strong>Add Compose Stack</strong> and name it <code>opengym</code>.</li>
  <li>Paste the Compose YAML above (adjust the IP address in <code>ORIGIN</code> and <code>RP_ID</code> to match your host IP).</li>
  <li>Click <strong>Deploy / Start Stack</strong>. Docker will pull the images and start both containers.</li>
  <li>Open <code>http://&lt;HOST_IP&gt;:8080</code> in any web browser and complete your initial account registration.</li>
  <li>In <strong>Settings</strong>, set your preferred weight unit to <strong>lbs</strong>.</li>
</ol>

<div class="page-break"></div>

<h2>3. Phase 2: Populating Routines &amp; History</h2>
<p>
You can populate all your workout routines into OpenGym immediately using either of two methods:
</p>

<h3>Method A: Web UI Built-In Importer (One-Click)</h3>
<ol>
  <li>In the OpenGym web app, click <strong>Settings (gear icon)</strong> &rarr; <strong>Import</strong>.</li>
  <li>Select <strong>Import from Hevy</strong> (or CSV).</li>
  <li>Paste your Hevy API key and click <strong>Import</strong>. OpenGym automatically creates all your workout routines, maps exercises, and imports your full workout history.</li>
</ol>

<h3>Method B: Automated Migration Script</h3>
<p>
Run the included migration script to automatically fetch all routines via the Hevy API, map the exercise templates to OpenGym catalogue IDs, and save them directly into your OpenGym profile:
</p>
<pre><code>python3 import_hevy_to_opengym.py</code></pre>

<h2>4. Phase 3: Linking the Sync Engine</h2>
<p>
The sync script interacts with OpenGym through its REST API (<code>GET /api/data</code>). To authorize the script on your local machine, choose either of the following authentication methods:
</p>

<h3>Option 1: Mobile App Pairing Token (Recommended)</h3>
<ol>
  <li>In OpenGym, go to <strong>Settings</strong> &rarr; <strong>Pair the mobile app</strong>.</li>
  <li>The app displays a 6-letter pairing code (e.g., <code>K8X2W9</code>).</li>
  <li>Run the sync script with the pairing parameter:
    <pre><code>python3 opengym_sync.py --pair K8X2W9</code></pre>
  </li>
  <li>The script redeems the one-time code for a long-lived Bearer session token and saves it to <code>opengym_token.txt</code>.</li>
</ol>

<h3>Option 2: Direct Username &amp; Password Sign-In</h3>
<p>
Since <code>PASSWORD_LOGIN=1</code> is enabled in your stack, you can authenticate directly:
</p>
<pre><code>python3 opengym_sync.py --login &lt;USERNAME&gt; &lt;PASSWORD&gt;</code></pre>

<h2>5. Phase 4: Innodigym Authentication</h2>
<p>
The Innodigym cloud API (<code>https://power.renhesports.com</code>) authenticates requests using a JWT string in the raw <code>Authorization: &lt;JWT&gt;</code> header (without the <code>Bearer</code> prefix).
</p>

<h3>macOS Extraction (Automatic):</h3>
<p>
If the official Innodigym macOS application is installed, the sync script automatically retrieves the active token from the application preferences:
</p>
<pre><code>defaults read com.innodigym.power202603 flutter.cache-tokenKey</code></pre>

<h3>Windows Extraction (Manual):</h3>
<p>
On Windows systems, you can capture your JWT token using either of the following approaches:
</p>
<ol>
  <li><strong>Web Portal / Browser DevTools:</strong> Log in at <code>https://power.renhesports.com</code>. Open Developer Tools (<code>F12</code>) &rarr; <strong>Network tab</strong> &rarr; inspect any request to <code>/api/course/...</code> &rarr; copy the <code>Authorization</code> header value.</li>
  <li><strong>Local Proxy:</strong> Use Fiddler or HTTP Toolkit to capture outgoing traffic from the Innodigym desktop app.</li>
  <li>Save the captured JWT string into a text file named <code>innodigym_token.txt</code> in the sync folder.</li>
</ol>

<div class="page-break"></div>

<h2>6. Phase 5: Exercise Mapping (`mapping.json`)</h2>
<p>
The sync engine uses <code>mapping.json</code> to resolve differences between OpenGym exercise names and Innodigym action names:
</p>

<pre><code>{mapping_json_code}</code></pre>

<table>
  <thead>
    <tr>
      <th>Innodigym Action Name</th>
      <th>OpenGym Name</th>
      <th>Match Method</th>
      <th>Sync Handling</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Incline Bench Press (Bar)</td>
      <td>Incline Chest Press (Cable)</td>
      <td>Mapping table alias</td>
      <td>Combined barbell weight mapped</td>
    </tr>
    <tr>
      <td>Belt Hip Thrust</td>
      <td>Belt Hip Thrust</td>
      <td>Exact match</td>
      <td>Combined belt load updated</td>
    </tr>
    <tr>
      <td>Seated Row</td>
      <td>Seated Row</td>
      <td>Exact match</td>
      <td>Cable row resistance updated</td>
    </tr>
    <tr>
      <td>Weighted Calf Raise</td>
      <td>Standing Calf Raise</td>
      <td>Mapping table alias</td>
      <td>Platform calf raise updated</td>
    </tr>
    <tr>
      <td>Weighted Reverse Lunge</td>
      <td>Reverse Lunge</td>
      <td>Fuzzy substring match</td>
      <td>Combined load updated</td>
    </tr>
  </tbody>
</table>

<h2>7. Phase 6: Automated Background Scheduling</h2>

<h3>macOS Automation (`launchd`)</h3>
<p>
Create a persistent LaunchAgent to run the sync script every 5 minutes in the background:
</p>
<ol>
  <li>Create <code>~/Library/LaunchAgents/com.user.opengym-innodigym-sync.plist</code>:</li>
</ol>
<pre><code>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;Label&lt;/key&gt;
    &lt;string&gt;com.user.opengym-innodigym-sync&lt;/string&gt;
    &lt;key&gt;ProgramArguments&lt;/key&gt;
    &lt;array&gt;
        &lt;string&gt;/usr/bin/python3&lt;/string&gt;
        &lt;string&gt;/Users/USER/.opengym-innodigym/opengym_sync.py&lt;/string&gt;
        &lt;string&gt;--auto&lt;/string&gt;
    &lt;/array&gt;
    &lt;key&gt;StartInterval&lt;/key&gt;
    &lt;integer&gt;300&lt;/integer&gt;
    &lt;key&gt;RunAtLoad&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;StandardOutPath&lt;/key&gt;
    &lt;string&gt;/Users/USER/.opengym-innodigym/sync.log&lt;/string&gt;
    &lt;key&gt;StandardErrorPath&lt;/key&gt;
    &lt;string&gt;/Users/USER/.opengym-innodigym/sync.err&lt;/string&gt;
&lt;/dict&gt;
&lt;/plist&gt;</code></pre>
<ol start="2">
  <li>Activate the service:
    <pre><code>launchctl load ~/Library/LaunchAgents/com.user.opengym-innodigym-sync.plist</code></pre>
  </li>
</ol>

<h3>Windows Automation (Task Scheduler)</h3>
<p>
On Windows, schedule the script using Windows Task Scheduler or the command prompt:
</p>
<pre><code>schtasks /create /tn "OpenGym-Innodigym-Sync" /tr "python.exe C:\\Scripts\\opengym_sync.py --auto" /sc minute /mo 5</code></pre>

<div class="page-break"></div>

<h2>8. Phase 7: Operation &amp; Physical Machine Verification</h2>

<h3>Dry-Run Preview (Manual Test)</h3>
<p>
To inspect weight changes before committing them to the Innodigym cloud backend:
</p>
<pre><code>python3 opengym_sync.py</code></pre>
<p>
The script outputs an alignment table showing old weights, heaviest logged OpenGym weights, and whether an update will occur.
</p>

<h3>Applying Updates to Innodigym</h3>
<pre><code>python3 opengym_sync.py --apply</code></pre>

<h3>Verifying on the Physical X1 Pro Console:</h3>
<ol>
  <li>Turn on your <strong>Innodigym X1 Pro</strong>.</li>
  <li>Navigate to your <strong>Custom Workouts</strong> tab.</li>
  <li><strong>Pull down on the screen</strong> to refresh the workout list from the cloud.</li>
  <li>Open your workout template (e.g. <em>X1 Pro Full Body B</em>).</li>
  <li>The updated resistance numbers will immediately appear on the dials ready for your next training session.</li>
</ol>

<div class="callout callout-warn">
  <div class="callout-title">UI Cache Behavior Note</div>
  If the desktop or mobile Innodigym app was already open on a specific workout detail screen when the background sync occurred, tap the back arrow (&larr;) and reopen the routine (or restart the app) to see the fresh cloud values. The physical X1 Pro console reloads immediately on pull-to-refresh.
</div>

<h2>9. Troubleshooting Reference</h2>
<table>
  <thead>
    <tr>
      <th>Issue</th>
      <th>Root Cause</th>
      <th>Resolution</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>401 Unauthorized</code> (OpenGym)</td>
      <td>Pairing token expired or invalid</td>
      <td>Run <code>python3 opengym_sync.py --pair &lt;CODE&gt;</code> using a fresh pairing code from OpenGym Settings.</td>
    </tr>
    <tr>
      <td><code>401 Unauthorized</code> (Innodigym)</td>
      <td>Innodigym JWT token expired</td>
      <td>Open the Innodigym desktop or mobile app to refresh the session token.</td>
    </tr>
    <tr>
      <td>No workout found</td>
      <td>Workout not yet saved in OpenGym</td>
      <td>Tap <strong>Finish Workout</strong> in OpenGym so the session moves to completed history.</td>
    </tr>
    <tr>
      <td>Wrong resistance display</td>
      <td>Unit scale calculation error</td>
      <td>Ensure <code>sideWeight = target_lbs &times; 4.5359237</code> is used; never send raw lbs or raw kg.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>10. Complete Production Script Source Code (`opengym_sync.py`)</h2>
<p>
Below is the complete, self-contained Python synchronization script. It handles OpenGym API authentication, exercise catalog resolution, Innodigym cloud communication, resistance unit scaling, and automatic background change detection.
</p>

<pre class="long-code"><code>{opengym_sync_code}</code></pre>

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
