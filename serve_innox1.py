#!/usr/bin/env python3
"""
Local, Private Server for InnoStudio Web Client.
Runs 100% locally on your Mac mini or NAS.
Proxies API requests directly to Innodigym with your cached token.
Provides local OpenGym Bridge API for real-time synchronization.
Zero passwords or credentials ever leave your machine.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import http.server
import socketserver
import webbrowser

PORT = 8085
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "myinnox1-local")
TOKEN_FILE = os.path.join(BASE_DIR, "innodigym_token.txt")

# Import local OpenGym bridge, Tapo manager and Power Automation
sys.path.append(BASE_DIR)
import opengym_bridge
import tapo_manager
import power_automation

# Ensure token.json and token.js exist for instant, synchronous authentication
DEFAULT_EMAIL = os.environ.get("INNO_EMAIL", "User")
email = DEFAULT_EMAIL
token = ""
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE) as f:
        token = f.read().strip()

token_json_path = os.path.join(WEB_DIR, "token.json")
if os.path.exists(token_json_path):
    try:
        with open(token_json_path) as tj:
            email = json.load(tj).get("email", DEFAULT_EMAIL)
    except Exception:
        pass

def update_token_assets(tok, new_email=None):
    global token, email
    token = tok.strip()
    if new_email:
        email = new_email
    with open(TOKEN_FILE, "w") as tf:
        tf.write(token)
    with open(os.path.join(WEB_DIR, "token.json"), "w") as tj:
        json.dump({"token": token, "email": email}, tj)
    with open(os.path.join(WEB_DIR, "token.js"), "w") as jsf:
        jsf.write(f'window.INNO_TOKEN = {json.dumps(token)};\nwindow.INNO_EMAIL = {json.dumps(email)};\n')

update_token_assets(token)

class LocalInnoProxy(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def do_HEAD(self):
        if self.path == "/gym":
            self.send_response(301)
            self.send_header("Location", "/gym/")
            self.end_headers()
            return
        elif self.path.startswith("/gym/"):
            self.path = self.path[4:]
        super().do_HEAD()

    def do_GET(self):
        # Redirect /gym to /gym/ so browser resolves relative links properly
        if self.path == "/gym":
            self.send_response(301)
            self.send_header("Location", "/gym/")
            self.end_headers()
            return
        elif self.path.startswith("/gym/"):
            self.path = self.path[4:]

        clean_p = self.path.split("?")[0]

        # Dynamically inject live token into index.html
        if clean_p in ("/", "/index.html"):
            index_path = os.path.join(WEB_DIR, "index.html")
            if os.path.exists(index_path):
                with open(index_path, "r", encoding="utf-8") as f:
                    html = f.read()
                current_tok = ""
                if os.path.exists(TOKEN_FILE):
                    with open(TOKEN_FILE, "r") as tf:
                        current_tok = tf.read().strip()
                token_tag = f'<script>\nwindow.INNO_TOKEN = {json.dumps(current_tok)};\nwindow.INNO_EMAIL = {json.dumps(email)};\ntry {{ localStorage.setItem("innodigym_token", window.INNO_TOKEN); localStorage.setItem("innodigym_email", window.INNO_EMAIL); localStorage.removeItem("innodigym_manual_logout"); }} catch(e) {{}}\n</script>'
                if "</head>" in html:
                    html = html.replace("</head>", f"{token_tag}\n</head>", 1)
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                self.wfile.write(body)
                return

        # Dynamically serve token.js with live token
        if clean_p == "/token.js":
            current_tok = ""
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r") as tf:
                    current_tok = tf.read().strip()
            content = f'window.INNO_TOKEN = {json.dumps(current_tok)};\nwindow.INNO_EMAIL = {json.dumps(email)};\n'
            body = content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(body)
            return

        # Token endpoint for client auto-login and updates
        if self.path.startswith("/api/token"):
            current_tok = ""
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r") as tf:
                    current_tok = tf.read().strip()
            self.send_json_response({"token": current_tok, "email": email})
            return

        # OpenGym Bridge Endpoints
        if self.path.startswith("/api/opengym/status"):
            self.send_json_response(opengym_bridge.get_status())
            return
        elif self.path.startswith("/api/opengym/sync-history"):
            self.send_json_response(opengym_bridge.get_sync_history())
            return
        elif self.path.startswith("/api/opengym/routines"):
            self.send_json_response(opengym_bridge.get_routines())
            return
        # Tapo Power & Energy Endpoints
        elif self.path.startswith("/api/power/status"):
            self.send_json_response(power_automation.check_power_status())
            return
        elif self.path.startswith("/api/power/settings"):
            self.send_json_response(power_automation.get_settings())
            return
        elif self.path.startswith("/api/"):
            self.proxy_request("GET")
        else:
            super().do_GET()

    def do_POST(self):
        # Normalize /gym prefix if proxy did not strip it
        if self.path.startswith("/gym/"):
            self.path = self.path[4:]
        elif self.path == "/gym":
            self.path = "/"

        # Token endpoint for client auto-login and updates
        if self.path.startswith("/api/token"):
            length = int(self.headers.get("Content-Length", 0))
            if length > 0:
                body = self.rfile.read(length)
                try:
                    payload = json.loads(body.decode("utf-8"))
                    new_tok = payload.get("token")
                    new_email = payload.get("email", email)
                    if new_tok:
                        update_token_assets(new_tok, new_email)
                except Exception:
                    pass
            self.send_json_response({"token": token, "email": email})
            return

        # OpenGym Bridge Endpoints
        if self.path.startswith("/api/opengym/sync-weights"):
            res = opengym_bridge.trigger_weight_sync()
            self.send_json_response(res)
            return
        elif self.path.startswith("/api/opengym/push-course"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else b"{}"
            try:
                payload = json.loads(body.decode("utf-8"))
                course_id = payload.get("courseId")
                if not course_id:
                    self.send_json_response({"success": False, "error": "courseId required"}, status=400)
                    return
                # Auto power on machine if configured
                power_automation.auto_power_on_if_needed(reason="push-course")
                res = opengym_bridge.push_course_to_opengym(course_id)
                self.send_json_response(res)
            except Exception as e:
                self.send_json_response({"success": False, "error": str(e)}, status=500)
            return
        elif self.path.startswith("/api/opengym/import-routine"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else b"{}"
            try:
                payload = json.loads(body.decode("utf-8"))
                routine_id = payload.get("routineId")
                if not routine_id:
                    self.send_json_response({"success": False, "error": "routineId required"}, status=400)
                    return
                res = opengym_bridge.import_routine_to_innodigym(routine_id)
                self.send_json_response(res)
            except Exception as e:
                self.send_json_response({"success": False, "error": str(e)}, status=500)
            return
        # Tapo Power Controls & Settings
        elif self.path.startswith("/api/power/toggle"):
            self.send_json_response(tapo_manager.toggle_power())
            return
        elif self.path.startswith("/api/power/on"):
            self.send_json_response(tapo_manager.set_power(True))
            return
        elif self.path.startswith("/api/power/off"):
            self.send_json_response(tapo_manager.set_power(False))
            return
        elif self.path.startswith("/api/power/settings"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else b"{}"
            try:
                payload = json.loads(body.decode("utf-8"))
                updated = power_automation.update_settings(payload)
                self.send_json_response({"success": True, "settings": updated})
            except Exception as e:
                self.send_json_response({"success": False, "error": str(e)}, status=400)
            return
        elif self.path.startswith("/api/"):
            if self.path.startswith("/api/course/custom/save"):
                try:
                    power_automation.auto_power_on_if_needed(reason="course-save")
                except Exception:
                    pass
            self.proxy_request("POST")
        else:
            self.send_error(404)

    def send_json_response(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.end_headers()
        self.wfile.write(body)

    def proxy_request(self, method):
        global token
        target_url = "https://power.renhesports.com" + self.path
        headers = {
            "Origin": "https://power.renhesports.com",
            "Referer": "https://power.renhesports.com/"
        }
        for k, v in self.headers.items():
            if k.lower() in ("authorization", "content-type", "accept", "user-agent"):
                headers[k] = v

        current_tok = ""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as tf:
                current_tok = tf.read().strip()

        if "Authorization" in headers:
            headers["Authorization"] = headers["Authorization"].replace("Bearer ", "").strip()
        elif current_tok:
            headers["Authorization"] = current_tok

        # Read POST body if present
        body = None
        if method == "POST":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                body = self.rfile.read(content_length)

        req = urllib.request.Request(target_url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read()
                # If this was a successful login, automatically capture the new token and update token files
                if self.path.startswith("/api/app/login") and resp.status == 200:
                    try:
                        login_data = json.loads(resp_body.decode("utf-8"))
                        new_tok = login_data.get("data", {}).get("token")
                        login_email = email
                        if body:
                            try:
                                login_email = json.loads(body.decode("utf-8")).get("email", email)
                            except Exception:
                                pass
                        if new_tok:
                            update_token_assets(new_tok.strip(), login_email)
                    except Exception:
                        pass

                self.send_response(resp.status)
                for hk, hv in resp.headers.items():
                    if hk.lower() in ("content-type", "cache-control"):
                        self.send_header(hk, hv)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(500, str(e))

class ReusableTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128

def main():
    power_automation.start_watchdog()
    with ReusableTCPServer(("127.0.0.1", PORT), LocalInnoProxy) as httpd:
        print("=" * 65)
        print("  PRIVATE LOCAL INNOSTUDIO WEB CLIENT (with OpenGym Bridge)")
        print("=" * 65)
        print(f"✔ 100% Local & Private — Zero third-party proxies")
        print(f"✔ Auto-authenticated with your existing token")
        print(f"✔ OpenGym Bridge active at /api/opengym/*")
        print(f"\n👉 Running at: http://localhost:{PORT}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    main()
