#!/usr/bin/env python3
"""
SwitchOps — Switch Room Protocol Server
Flip the Switch Hackathon 2026 — Track 01: Best Business Workflow

Implements the official Switch Agent Protocol:
- GET  /room/events   -> Server-Sent Events (SSE) stream for agents & clients
- POST /room/messages -> Ingest messages from human chat apps (Slack/Discord) or agents
- GET  /room/state    -> Full room state (history, tasks, decisions, rules, knowledge)
- POST /room/decisions-> Immutable human-in-the-loop decision logging
- POST /room/tasks    -> Shared task updates
- GET  /health        -> Health check
"""

import sys
import os
import json
import time
import queue
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 8765

# In-memory thread-safe state
ROOM_STATE = {
    "room_name": "incidents-production",
    "topic": "🔥 Production Incident War Room & Release Escort",
    "bridge": "slack",
    "active_agents": [
        {
            "id": "triager",
            "name": "Incident Triager AI",
            "handle": "@SwitchTriager",
            "provider": "claude-code",
            "status": "online",
            "role": "Root-cause triage, log analysis, severity classification (P0-P3)"
        },
        {
            "id": "infraops",
            "name": "InfraOps Sentry",
            "handle": "@InfraOps",
            "provider": "antigravity",
            "status": "online",
            "role": "K8s cluster telemetry, commit correlation, rollback canary inspection"
        },
        {
            "id": "hotfixer",
            "name": "Hotfix Code Assistant",
            "handle": "@HotfixCoder",
            "provider": "codex",
            "status": "online",
            "role": "Code patch generation, automated regression tests, post-mortem synthesis"
        }
    ],
    "users": [
        {"id": "priya", "name": "Priya Sharma", "role": "Incident Commander", "avatar": "P"},
        {"id": "sam", "name": "Sam Taylor", "role": "On-Call DevOps Engineer", "avatar": "S"},
        {"id": "alex", "name": "Alex Chen", "role": "Lead Architect", "avatar": "A"}
    ],
    "messages": [
        {
            "id": "msg-001",
            "sender_type": "system",
            "sender_name": "Switch Bridge",
            "sender_avatar": "⚡",
            "timestamp": "2026-11-07T21:40:00Z",
            "content": "⚡ **Switch Room connected to Slack `#incidents-production`**. Registered agents: @SwitchTriager (Claude Code), @InfraOps (Antigravity), @HotfixCoder (Codex). Human Lead: @Priya."
        },
        {
            "id": "msg-002",
            "sender_type": "human",
            "sender_name": "Sam Taylor",
            "sender_handle": "@sam",
            "sender_avatar": "S",
            "timestamp": "2026-11-07T21:42:15Z",
            "content": "🚨 Checkout API is throwing massive HTTP 500 errors since 09:42 IST! Stripe webhooks failing and cart latency spiked past 4200ms. @SwitchTriager can you look into cart-service immediately?"
        },
        {
            "id": "msg-003",
            "sender_type": "agent",
            "sender_name": "Incident Triager AI",
            "sender_handle": "@SwitchTriager",
            "sender_avatar": "🤖",
            "agent_provider": "claude-code",
            "timestamp": "2026-11-07T21:42:30Z",
            "content": "🔍 **[Triage Report - P0 Incident]**\n- **Impact:** `cart-service` returning `HTTP 500 Internal Server Error` on `/api/v2/checkout/confirm`\n- **Error Log:** `PG::ConnectionTimeout: connection pool exhausted (active=50/50)`\n- **Blast Radius:** ~3,400 active shoppers affected; payment drop ~84%.\n\n@InfraOps Please check K8s telemetry and recent deployments around 09:40 IST."
        },
        {
            "id": "msg-004",
            "sender_type": "agent",
            "sender_name": "InfraOps Sentry",
            "sender_handle": "@InfraOps",
            "sender_avatar": "🛡️",
            "agent_provider": "antigravity",
            "timestamp": "2026-11-07T21:43:05Z",
            "content": "📊 **[Telemetry & Deploy Correlation]**\n- Identified culprit release: **`v2.14.0`** deployed at **09:40:12 IST** (Commit `a9f24e1` by Alex Chen: *'Migrate cart session caching to unbuffered Postgres transactions'*).\n- Root Cause: Unclosed connection in `cart_repo.go:88` during Redis fallback.\n- **Remediation Plan:** Fast rollback to stable version **`v2.13.2`**. Canary manifest prepared.\n\n⚠️ **Awaiting Human Sign-Off:** @Priya, please authorize rollback to `v2.13.2`."
        },
        {
            "id": "msg-005",
            "sender_type": "human",
            "sender_name": "Priya Sharma",
            "sender_handle": "@Priya",
            "sender_avatar": "P",
            "timestamp": "2026-11-07T21:43:40Z",
            "content": "🎙️ *(Spoken via Wispr Flow)*: Approved. Roll back `cart-service` to v2.13.2 immediately and monitor error rates."
        },
        {
            "id": "msg-006",
            "sender_type": "agent",
            "sender_name": "Hotfix Code Assistant",
            "sender_handle": "@HotfixCoder",
            "sender_avatar": "⚡",
            "agent_provider": "codex",
            "timestamp": "2026-11-07T21:44:10Z",
            "content": "🚀 **[Remediation Executed & Smoke Tests Passed]**\n- Rollback deployment `v2.13.2` applied to 4/4 K8s replica sets.\n- Connection pool utilization dropped from 100% to 14%.\n- Latency restored to baseline: **48ms p99**.\n- HTTP 500 error rate returned to **0.00%**.\n- Drafted Post-Mortem in Decision Log and opened PR #482 for permanent connection pool leak fix."
        }
    ],
    "tasks": [
        {"id": "TSK-101", "title": "Classify incident severity & blast radius", "owner": "@SwitchTriager", "status": "completed", "priority": "P0"},
        {"id": "TSK-102", "title": "Correlate telemetry with last commit SHA", "owner": "@InfraOps", "status": "completed", "priority": "P0"},
        {"id": "TSK-103", "title": "Rollback cart-service to v2.13.2", "owner": "@HotfixCoder", "status": "completed", "priority": "P0"},
        {"id": "TSK-104", "title": "Verify p99 latency & error rates", "owner": "@InfraOps", "status": "completed", "priority": "P1"},
        {"id": "TSK-105", "title": "Compile Blameless Post-Mortem", "owner": "@HotfixCoder", "status": "in_progress", "priority": "P2"}
    ],
    "decisions": [
        {
            "id": "DEC-2026-01",
            "timestamp": "2026-11-07T21:43:40Z",
            "decision": "Rollback cart-service to v2.13.2",
            "approver": "Priya Sharma (Incident Lead)",
            "sign_off_method": "Wispr Flow Voice Dictation",
            "status": "APPROVED_AND_EXECUTED",
            "hash": "0x7f4e91b8a3c20d"
        }
    ],
    "rules": [
        {"id": "R1", "rule": "Zero Production Mutation Without Human Sign-Off", "status": "Enforced"},
        {"id": "R2", "rule": "Mandatory Post-Mortem within 15 Minutes for P0/P1", "status": "Active"},
        {"id": "R3", "rule": "Wispr Flow Voice Command Cryptographic Signing", "status": "Verified"}
    ],
    "knowledge": [
        {"title": "Cart-Service Runbook", "type": "runbook", "content": "Database pool size: 50. Max lifetime: 5m. Rollback target: v2.13.2."},
        {"title": "Escalation Matrix", "type": "doc", "content": "P0: Notify #incidents, page Priya (Lead) + Sam (DevOps)."},
        {"title": "Switch Agent Protocol Specs", "type": "spec", "content": "SSE inbound on /room/events, outbound JSON HTTP POST on /room/messages."}
    ]
}

# Subscribers for SSE
SUBSCRIBERS = []
SUBSCRIBERS_LOCK = threading.Lock()

def broadcast_event(event_type, data):
    """Broadcast an SSE event to all connected agent listeners"""
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with SUBSCRIBERS_LOCK:
        dead = []
        for q in SUBSCRIBERS:
            try:
                q.put_nowait(payload)
            except Exception:
                dead.append(q)
        for q in dead:
            SUBSCRIBERS.remove(q)

class SwitchProtocolHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self, content_type="application/json"):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", content_type)

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        
        # 1. Server-Sent Events (SSE) Stream
        if url.path == "/room/events":
            self.send_response(200)
            self._set_cors_headers(content_type="text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            q = queue.Queue()
            with SUBSCRIBERS_LOCK:
                SUBSCRIBERS.append(q)

            # Send initial room state
            init_event = f"event: room_connected\ndata: {json.dumps({'status': 'connected', 'room': ROOM_STATE['room_name']})}\n\n"
            self.wfile.write(init_event.encode("utf-8"))
            self.wfile.flush()

            try:
                while True:
                    try:
                        msg = q.get(timeout=20.0)
                        self.wfile.write(msg.encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        # Keep-alive heartbeat comment
                        self.wfile.write(b": heartbeat\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                with SUBSCRIBERS_LOCK:
                    if q in SUBSCRIBERS:
                        SUBSCRIBERS.remove(q)
            return

        # 2. Get Room State
        elif url.path == "/room/state":
            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(ROOM_STATE, indent=2).encode("utf-8"))
            return

        # 3. Health Check
        elif url.path in ["/health", "/"]:
            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
            resp = {
                "status": "healthy",
                "service": "SwitchOps Room Protocol Server",
                "protocol_version": "1.0",
                "active_listeners": len(SUBSCRIBERS),
                "room": ROOM_STATE["room_name"]
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def do_POST(self):
        url = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception:
            self.send_response(400)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Invalid JSON body"}')
            return

        # 1. Post a new message to the room
        if url.path == "/room/messages":
            msg_id = f"msg-{len(ROOM_STATE['messages']) + 1:03d}"
            new_msg = {
                "id": msg_id,
                "sender_type": body.get("sender_type", "human"),
                "sender_name": body.get("sender_name", "Anonymous"),
                "sender_handle": body.get("sender_handle", "@user"),
                "sender_avatar": body.get("sender_avatar", "👤"),
                "agent_provider": body.get("agent_provider", None),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "content": body.get("content", "")
            }
            ROOM_STATE["messages"].append(new_msg)
            broadcast_event("message", new_msg)

            self.send_response(201)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": new_msg}).encode("utf-8"))
            return

        # 2. Record an immutable Human Decision
        elif url.path == "/room/decisions":
            dec_id = f"DEC-2026-{len(ROOM_STATE['decisions']) + 1:02d}"
            new_decision = {
                "id": dec_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "decision": body.get("decision", "No decision text"),
                "approver": body.get("approver", "Human Lead"),
                "sign_off_method": body.get("sign_off_method", "UI Click"),
                "status": body.get("status", "APPROVED"),
                "hash": hex(int(time.time() * 1000))
            }
            ROOM_STATE["decisions"].append(new_decision)
            broadcast_event("decision", new_decision)

            self.send_response(201)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "decision": new_decision}).encode("utf-8"))
            return

        # 3. Add or update task
        elif url.path == "/room/tasks":
            tsk_id = body.get("id") or f"TSK-{len(ROOM_STATE['tasks']) + 101}"
            task = {
                "id": tsk_id,
                "title": body.get("title", "Untitled task"),
                "owner": body.get("owner", "@unassigned"),
                "status": body.get("status", "in_progress"),
                "priority": body.get("priority", "P1")
            }
            # update existing or append
            for i, t in enumerate(ROOM_STATE["tasks"]):
                if t["id"] == tsk_id:
                    ROOM_STATE["tasks"][i] = task
                    break
            else:
                ROOM_STATE["tasks"].append(task)

            broadcast_event("task_update", task)
            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "task": task}).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

def run():
    # Ensure stdout handles unicode safely on Windows shells
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    server = HTTPServer(("0.0.0.0", PORT), SwitchProtocolHandler)
    print("=" * 70)
    print(f"[*] SwitchOps Room Protocol Server running on http://127.0.0.1:{PORT}")
    print(f"[*] SSE Endpoint:   http://127.0.0.1:{PORT}/room/events")
    print(f"[*] Messages API:   http://127.0.0.1:{PORT}/room/messages")
    print(f"[*] State API:      http://127.0.0.1:{PORT}/room/state")
    print("=" * 70)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down SwitchOps server gracefully.")
        server.server_close()

if __name__ == "__main__":
    run()
