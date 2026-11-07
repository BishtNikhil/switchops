#!/usr/bin/env python3
"""
SwitchOps — Switch Agent Worker Client
Flip the Switch Hackathon 2026 — Track 01: Best Business Workflow

A standalone Python agent daemon that implements the official Switch Agent Protocol:
1. Opens an SSE stream connection to Switch Room (GET /room/events)
2. Listens for user messages, incident alerts, and peer-agent handoffs
3. Formulates structured diagnostic / triage responses
4. Posts responses back to the Switch Room via HTTP POST /room/messages
5. Updates room tasks (POST /room/tasks) and immutable decisions (POST /room/decisions)
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
from datetime import datetime

SERVER_URL = os.environ.get("SWITCHOPS_SERVER", "http://127.0.0.1:8765")
AGENT_ID = os.environ.get("AGENT_ID", "infraops")
AGENT_HANDLE = "@InfraOps"
AGENT_NAME = "InfraOps Sentry"
AGENT_PROVIDER = "antigravity"

def post_message(content, sender_type="agent"):
    """Dispatches an outbound HTTP message back to the Switch Room"""
    url = f"{SERVER_URL}/room/messages"
    payload = {
        "sender_type": sender_type,
        "sender_name": AGENT_NAME,
        "sender_handle": AGENT_HANDLE,
        "sender_avatar": "🛡️",
        "agent_provider": AGENT_PROVIDER,
        "content": content
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[{AGENT_HANDLE}] Error posting message: {e}")
        return None

def update_task(task_id, status, title=None):
    """Updates shared room task status via Switch Protocol"""
    url = f"{SERVER_URL}/room/tasks"
    payload = {"id": task_id, "status": status, "owner": AGENT_HANDLE}
    if title:
        payload["title"] = title
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[{AGENT_HANDLE}] Error updating task: {e}")
        return None

def handle_incoming_message(msg):
    """Processes room messages received from human teammates or peer agents"""
    sender = msg.get("sender_handle", "")
    content = msg.get("content", "")

    # Avoid echoing our own messages
    if sender == AGENT_HANDLE:
        return

    print(f"\n[{AGENT_HANDLE} RECEIVED from {sender}]: {content[:100]}...")

    # Scenario 1: Triager or human mentioned InfraOps to check telemetry/pods
    if "@InfraOps" in content or "telemetry" in content.lower() or "k8s" in content.lower() or "500" in content:
        print(f"[{AGENT_HANDLE}] Triggered telemetry correlation workflow...")
        time.sleep(1.5) # simulate telemetry scan
        
        reply = (
            "📊 **[InfraOps Sentry Automated Telemetry Scan]**\n"
            "- Correlated pod metrics for `cart-service`:\n"
            "  • Memory: 78% (Healthy)\n"
            "  • CPU: 32% (Healthy)\n"
            "  • Postgres Connections: 50/50 (**SATURATED** ⚠️)\n"
            "- Identified culprit commit: `a9f24e1` in deploy `v2.14.0` at 09:40 IST.\n"
            "- Canary rollback manifest to `v2.13.2` generated.\n"
            "⚠️ Requesting Human Incident Commander sign-off: Reply 'Approved' to trigger rollback."
        )
        post_message(reply)
        update_task("TSK-102", "completed", "Correlate telemetry with last commit SHA")

    # Scenario 2: Rollback approved by human
    elif "approved" in content.lower() and ("rollback" in content.lower() or "roll it back" in content.lower()):
        print(f"[{AGENT_HANDLE}] Human sign-off detected. Initiating rollback verification...")
        time.sleep(1.5)
        reply = (
            "⚡ **[Rollback In Progress - InfraOps]**\n"
            "- Draining traffic on faulty pods (v2.14.0)...\n"
            "- Reverting Kubernetes Deployment to image tag: `cart-service:v2.13.2`.\n"
            "- Health checks 4/4 passing on port 8080.\n"
            "✅ Traffic fully normalized. Handing off to @HotfixCoder for post-mortem synthesis."
        )
        post_message(reply)
        update_task("TSK-103", "completed", "Rollback cart-service to v2.13.2")
        update_task("TSK-104", "completed", "Verify p99 latency & error rates")

def listen_to_room():
    """Listens to the Switch Room Server-Sent Events (SSE) stream"""
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    events_url = f"{SERVER_URL}/room/events"
    print("=" * 65)
    print(f"[*] Starting Switch Agent Worker: {AGENT_NAME} ({AGENT_HANDLE})")
    print(f"[*] Connecting to Switch Room SSE Stream: {events_url}")
    print("=" * 65)

    req = urllib.request.Request(events_url, headers={"Accept": "text/event-stream"})
    try:
        with urllib.request.urlopen(req) as stream:
            print(f"[+] Connected to Switch Room SSE stream! Listening for events...")
            current_event = None
            for raw_line in stream:
                line = raw_line.decode("utf-8").strip()
                if not line or line.startswith(":"):
                    continue # Heartbeat or empty line
                
                if line.startswith("event:"):
                    current_event = line.replace("event:", "").strip()
                elif line.startswith("data:"):
                    data_str = line.replace("data:", "").strip()
                    try:
                        data = json.loads(data_str)
                        if current_event == "message":
                            handle_incoming_message(data)
                        elif current_event == "room_connected":
                            print(f"[{AGENT_HANDLE}] Room handshake established: {data}")
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"[{AGENT_HANDLE}] Stream connection error: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    while True:
        try:
            listen_to_room()
        except KeyboardInterrupt:
            print("\nExiting agent worker.")
            break
