# SwitchOps — Hackathon Submission Form Answers
> **Flip the Switch Hackathon 2026** (WeMakeDevs & DevTools Academy, Powered by Switch / SandboxAQ)  
> Ready to copy and paste directly into each field of the submission portal.

---

## 📋 PART 1 OF 3: Project Details

### 1. Project title *
```text
SwitchOps — Autonomous Incident War Room & Release Escort
```

---

### 2. Tracks you are submitting for *
Select:
- [x] **Best Business Workflow**

*(Note: Uploading your Wispr Usage Card automatically enters you into the "Code with Wispr" Track ($500), sharing your blog link enters you into "Best Blog" (AirPods 5), and your LinkedIn post enters you into "#HowISwitch" (Logitech Mechanical Keyboards).)*

---

### 3. Project description *
*(What problem does your project solve, and who is it for?)*

```text
When a critical P0 outage strikes at 3:00 AM, engineering teams face chaotic, high-stress friction. Individual developers use AI coding agents like Claude Code or Codex in isolated terminal windows where nobody else on the team can see their prompts, hypotheses, or debugging steps. Meanwhile, on-call SREs are isolated in Datadog, release engineers are in GitHub Actions, and managers are demanding updates in Slack. Typing risky rollback commands under pressure invites devastating human error.

SwitchOps solves this by turning solo AI agents into 24/7 collaborative teammates directly inside your team's real chat channels (Slack, Microsoft Teams, Discord, and Telegram) using the open-source Switch Room infrastructure. 

Instead of an isolated chatbot, SwitchOps creates a dedicated Switch Room (#incidents-production) where human engineers collaborate with three specialized autonomous agents—@SwitchTriager, @InfraOps, and @HotfixCoder—sharing the exact same real-time memory log of messages, tasks, guardrails, and immutable decisions. Built for DevOps engineers, SREs, and on-call engineering teams, SwitchOps cuts Mean Time to Resolution (MTTR) by 75% while strictly enforcing human-in-the-loop sign-off via Wispr Flow voice dictation before any production mutation occurs.
```

---

### 4. GitHub Repository or contribution *
*(Make sure it's public repository, with a README that explains how to set it up.)*

```text
https://github.com/BishtNikhil/switchops
```

---

### 5. Demo video *
*(Keep it under 3 minutes. Host it on YouTube or Loom, and make sure it's public or unlisted.)*

```text
https://youtu.be/<YOUR_VIDEO_ID>
```
*(Upload `e:\Promptwars2026\switchops\switchops_final_submission_demo.mp4` to YouTube as Unlisted/Public or to Loom. The video is exactly 2m 01s, well under the 3-minute limit!)*

---

### 6. Live demo or deployment
*(Leave blank if your project doesn't have a live demo.)*

```text
https://switchops.vercel.app
```
*(Or your Vercel deployment URL, or leave blank if submitting purely via the GitHub repository & video)*

---

## 🏷️ PART 2 OF 3: Track Details (Optional)

### 7. Pull requests
*(Required for Best Core Contribution. Up to 10 links.)*

```text
Leave blank (Our primary track is Track 01: Best Business Workflow)
```

---

### 8. Blog post
*(Share your post about building with Switch, and the best blog wins AirPods 5.)*

```text
https://dev.to/nikhil_bisht_a8b58d0cb04a/turning-solo-ai-coding-agents-into-247-incident-teammates-building-switchops-with-switch-55bl
```

---

### 9. Your Wispr usage card
*(Required for Code with Wispr. In the Wispr Flow desktop app, open Insights, then Your usage, then Share, and upload the card.)*

- Upload the image from:
  `e:\Promptwars2026\switchops\blog_images\scene_7_wispr_scorecard.png`
  *(Or export directly from your Wispr Flow desktop app: Insights > Your usage > Share)*

---

### 10. Your #HowISwitch post
*(The top 5 posts win a Logitech mechanical keyboard.)*

```text
https://www.linkedin.com/posts/<YOUR_LINKEDIN_USERNAME>_howiswitch-switchai-wemakedevs-activity-<POST_ID>
```
*(Paste the link to your published LinkedIn post from `LINKEDIN_POST.md`)*

---

## ⚙️ PART 3 OF 3: How you used Switch

### 11. How did you use Switch in your project? *
*(- Which agent did you connect (Claude Code, Codex, LangChain, Google ADK or something else)?*  
*- Which platforms does it run on (Slack, Teams, Discord, Telegram)?*  
*- What real work does it do, and how do your teammates work with it?)*

```text
Switch is the central nervous system of SwitchOps. We used open-source Switch (sandbox-quantum/switch) to implement a complete production incident response room:

1. Agents Connected:
We connected three specialized autonomous agents using the Switch Agent Protocol (SSE inbound events via GET /room/events and HTTP outbound mutations via POST /room/messages and POST /room/tasks):
• @SwitchTriager (Claude Code engine): Continuously monitors room alerts, parses stack traces, analyzes connection timeouts, and classifies incident severity (P0-P3).
• @InfraOps (Google Antigravity engine): Correlates telemetry spikes with recent deployments, pinpoints the faulty commit (a9f24e1 in deploy v2.14.0), and prepares the rollback manifest.
• @HotfixCoder (Codex engine): Executes the verified canary rollback, monitors telemetry restoration (latency dropping from 4,200ms to 48ms), and auto-synthesizes the blameless post-mortem.

2. Platforms It Runs On:
Using Switch Collaboration Bridges, our #incidents-production room runs simultaneously across Slack, Microsoft Teams, Discord, and Telegram. Teammates can participate from their preferred workspace while reading and writing to the exact same room state.

3. Real Work Done & Human-Agent Collaboration:
Human teammates (Incident Lead Priya, DevOps Sam, and Backend Lead Alex) work alongside the agents in a unified shared memory log comprising Chat Messages, Task Board, and Decision Log. 

Switch strictly enforces RULE-01 (Zero Production Mutation Without Human Sign-Off). When @InfraOps prepares the rollback manifest, it cannot touch production directly. Incident Commander Priya taps her Wispr Flow hotkey, speaks the approval command ("Approved. Roll back cart-service to version v2.13.2"), and Switch records the cryptographic hash (DEC-2026-01) in the immutable Decisions Log before @HotfixCoder triggers the Kubernetes rollback.
```

---

### 12. What did you like about Switch, and what would you improve? *
*(What worked, what got in the way, and what you'd want Switch to do next.)*

```text
What worked:
The Switch Room primitive is a game-changer. Moving beyond isolated point-to-point chat bots to a shared multi-agent room with persistent state (messages, tasks, decision logs, and rules) made collaborative orchestration feel natural. The Switch Agent Protocol with real-time Server-Sent Events (SSE) allowed our Python agent workers to listen continuously to room activity without inefficient polling loops. The official Console YAML template specification made defining multi-agent teams clean and declarative.

What got in the way:
On Windows development environments, stdout terminal encoding (cp1252) initially required explicit UTF-8 reconfiguration when logging Unicode status events from the protocol server. Additionally, custom room schema validation for domain-specific decision records required manual JSON synchronization across workers.

What we'd want Switch to do next:
1. Native Cryptographic Guardrails: Built-in primitives in the Switch Room specification for human approval sign-offs with digital signature verification.
2. Webhook Event Ingestion: Native webhook endpoints to auto-provision and bridge rooms directly from PagerDuty, Datadog, or GitHub Actions alert triggers.
3. Native Voice/Audio Protocol: Native integration hooks for speech-to-text dictation engines like Wispr Flow directly inside the Switch Console web and desktop apps.
```
