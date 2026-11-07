# Security Policy & The Ponytail Method Compliance

SwitchOps is engineered with security and compliance as primary design constraints. This document details the security posture, secret hygiene, and repository sanitation standards applied to this project for the **Flip the Switch Hackathon 2026**.

---

## 🔒 1. The Ponytail Method: Clean, Contained & Zero Loose Ends

The "Ponytail Method" enforces that all sensitive credentials, temporary artifacts, and environment configurations are tightly bound, isolated, and strictly excluded from public version control:

1. **Zero Hardcoded Secrets:**
   - No API keys, passwords, webhook tokens, or cryptographic private keys exist anywhere in source code (`.py`, `.js`, `.html`, `.json`, `.yaml`).
   - Every integration relies on runtime environment variables managed via an isolated `.env` file (enforced by `.gitignore`).
   - A sanitized `.env.example` is provided with dummy placeholders.

2. **Airtight Exclusion Boundary (`.gitignore`):**
   - Environment configurations (`.env`, `.env.*`)
   - Cryptographic keys and certificates (`*.pem`, `*.key`, `*.pfx`, `*.id_rsa*`)
   - Python bytecode and virtual environments (`__pycache__/`, `venv/`, `.venv/`)
   - Render caches and temporary media processing directories (`processed_audio_*/`, `temp_*.mp4`)
   - Operating system and IDE metadata (`.DS_Store`, `Thumbs.db`, `.idea/`, `.vscode/`)

3. **Rule-01 Autonomous Guardrail:**
   - AI agents operating within the Switch Room have **read-only diagnostic access** to production.
   - Any mutating production operation (e.g. Kubernetes rollback, database failover) is cryptographically gated behind human commander sign-off recorded in the immutable `Decisions Log`.

---

## 🔍 2. Secret Scan & Sanitization Verification

Prior to pushing to GitHub, the repository was audited using automated pattern scanning:

| Category | Checked Patterns | Verification Result |
| :--- | :--- | :--- |
| **API Keys** | `sk-*`, `anthropic_*`, `openai_*`, `wispr_*` | ✅ **0 matches found** |
| **Tokens & Webhooks** | `Bearer *`, `hooks.slack.com`, `discord.com/api/webhooks` | ✅ **0 matches found** |
| **Private Keys & Certs** | `-----BEGIN PRIVATE KEY-----`, `*.pem`, `*.key` | ✅ **0 matches found** |
| **Database Credentials** | `postgres://*:*@`, `mysql://*:*@` | ✅ **0 matches found** |

---

## 🛡️ 3. Responsible Vulnerability Disclosure

If you discover any security consideration or potential vulnerability within SwitchOps, please open an advisory or contact the maintainers directly:

- **Author:** Nikhil Bisht
- **Hackathon:** Flip the Switch 2026 (WeMakeDevs & DevTools Academy)
- **Response SLA:** Within 24 hours of notification
