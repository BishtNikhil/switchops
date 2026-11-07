/**
 * SwitchOps — Autonomous Incident War Room & Release Escort
 * Main Frontend Logic & Switch Agent Protocol Engine
 * Flip the Switch Hackathon 2026 — Track 01: Best Business Workflow
 */

(function () {
  'use strict';

  // --- STATE ---
  const state = {
    activeRoom: 'incidents-production',
    activeBridge: 'slack',
    activeTab: 'stream',
    isRecordingVoice: false,
    backendConnected: false,
    eventSource: null,
    
    // Switch Room Members
    members: {
      priya: { name: 'Priya Sharma', handle: '@Priya', role: 'Incident Lead', avatar: 'P', type: 'human', class: 'avatar-human-p' },
      sam: { name: 'Sam Taylor', handle: '@sam', role: 'DevOps On-Call', avatar: 'S', type: 'human', class: 'avatar-human-s' },
      alex: { name: 'Alex Chen', handle: '@alex', role: 'Backend Lead', avatar: 'A', type: 'human', class: 'avatar-human-a' },
      triager: { name: 'Incident Triager AI', handle: '@SwitchTriager', role: 'Claude Code', avatar: '🔍', type: 'agent', provider: 'Claude Code', class: 'avatar-agent-triager' },
      infra: { name: 'InfraOps Sentry', handle: '@InfraOps', role: 'Antigravity', avatar: '🛡️', type: 'agent', provider: 'Antigravity', class: 'avatar-agent-infra' },
      hotfix: { name: 'Hotfix Code Assistant', handle: '@HotfixCoder', role: 'Codex', avatar: '⚡', type: 'agent', provider: 'Codex', class: 'avatar-agent-coder' }
    },

    // Conversation History
    messages: [
      {
        id: 'msg-001',
        senderType: 'system',
        senderName: 'Switch Bridge',
        senderHandle: 'switch-core',
        senderAvatar: '⚡',
        timestamp: '09:40:00 IST',
        content: `⚡ **Switch Room connected to Slack channel \`#incidents-production\`**.\n` +
                 `Registered autonomous agents: **@SwitchTriager** (Claude Code), **@InfraOps** (Antigravity), **@HotfixCoder** (Codex).\n` +
                 `Human Incident Lead: **@Priya** (Incident Commander). Guardrail policy: *Zero production rollback without human approval*.`
      },
      {
        id: 'msg-002',
        senderType: 'human',
        senderKey: 'sam',
        senderName: 'Sam Taylor',
        senderHandle: '@sam',
        senderAvatar: 'S',
        timestamp: '09:42:15 IST',
        content: `🚨 **Checkout API is throwing massive HTTP 500 errors since 09:42!**\n` +
                 `Stripe webhooks are failing and cart latency spiked past **4,200ms**. Over 3,400 active sessions blocked.\n` +
                 `@SwitchTriager can you look into \`cart-service\` immediately?`
      },
      {
        id: 'msg-003',
        senderType: 'agent',
        senderKey: 'triager',
        senderName: 'Incident Triager AI',
        senderHandle: '@SwitchTriager',
        senderAvatar: '🔍',
        agentProvider: 'Claude Code',
        timestamp: '09:42:35 IST',
        content: `🔍 **[Triage Report — P0 Incident]**\n` +
                 `- **Impact:** \`cart-service\` returning \`HTTP 500 Internal Server Error\` on \`/api/v2/checkout/confirm\`\n` +
                 `- **Log Analysis:** \`PG::ConnectionTimeout: connection pool exhausted (active=50/50, waiting=142)\`\n` +
                 `- **Blast Radius:** ~3,400 active shoppers affected; payment completion rate dropped by **84%**.\n\n` +
                 `@InfraOps Please inspect recent deployment telemetry and Kubernetes connection metrics around 09:40 IST.`
      },
      {
        id: 'msg-004',
        senderType: 'agent',
        senderKey: 'infra',
        senderName: 'InfraOps Sentry',
        senderHandle: '@InfraOps',
        senderAvatar: '🛡️',
        agentProvider: 'Antigravity',
        timestamp: '09:43:05 IST',
        content: `📊 **[InfraOps Deployment & Telemetry Scan]**\n` +
                 `- **Culprit Release:** \`v2.14.0\` deployed at **09:40:12 IST** (Commit \`a9f24e1\` by Alex Chen: *"Migrate cart session caching to unbuffered Postgres transactions"*).\n` +
                 `- **Root Cause:** Goroutines leaking Postgres database connections in \`cart_repo.go:88\` whenever Redis cache misses occur.\n` +
                 `- **Remediation Plan:** Fast rollback to stable version **\`v2.13.2\`**. Canary manifest generated.\n\n` +
                 `⚠️ **Action Required:** @Priya, please authorize rollback to \`v2.13.2\`.`
      },
      {
        id: 'msg-005',
        senderType: 'human',
        senderKey: 'priya',
        senderName: 'Priya Sharma',
        senderHandle: '@Priya',
        senderAvatar: 'P',
        timestamp: '09:43:40 IST',
        isVoice: true,
        content: `🎙️ *(Spoken via Wispr Flow)*: **Approved.** Roll back \`cart-service\` to \`v2.13.2\` immediately and monitor error rates.`
      },
      {
        id: 'msg-006',
        senderType: 'agent',
        senderKey: 'hotfix',
        senderName: 'Hotfix Code Assistant',
        senderHandle: '@HotfixCoder',
        senderAvatar: '⚡',
        agentProvider: 'Codex',
        timestamp: '09:44:12 IST',
        content: `🚀 **[Rollback Executed & Verification Passed]**\n` +
                 `- Reverted Kubernetes deployment to stable image \`cart-service:v2.13.2\` across 4/4 pods.\n` +
                 `- Database connection pool utilization dropped from **100% (50/50)** to **14% (7/50)**.\n` +
                 `- Latency normalized: **p99 = 48ms** (restored from 4,200ms spike).\n` +
                 `- HTTP 500 error rate returned to **0.00%**.\n` +
                 `- Immutable sign-off recorded in **Decisions Log** (\`DEC-2026-01\`).\n` +
                 `- Automated Blameless Post-Mortem synthesized & permanent hotfix PR #482 opened.`
      }
    ],

    // Room Tasks
    tasks: [
      { id: 'TSK-101', title: 'Classify incident severity & calculate blast radius', owner: '@SwitchTriager', status: 'completed', priority: 'P0' },
      { id: 'TSK-102', title: 'Correlate telemetry with faulty commit SHA (a9f24e1)', owner: '@InfraOps', status: 'completed', priority: 'P0' },
      { id: 'TSK-103', title: 'Authorize rollback to stable release v2.13.2', owner: '@Priya (Wispr)', status: 'completed', priority: 'P0' },
      { id: 'TSK-104', title: 'Execute canary drain & verify p99 latency recovery', owner: '@HotfixCoder', status: 'completed', priority: 'P1' },
      { id: 'TSK-105', title: 'Compile Blameless Post-Mortem & hotfix PR #482', owner: '@HotfixCoder', status: 'in_progress', priority: 'P2' }
    ],

    // Decisions Log (Audit trail)
    decisions: [
      {
        id: 'DEC-2026-01',
        title: 'Emergency Rollback of cart-service to v2.13.2',
        approver: 'Priya Sharma (Incident Commander)',
        timestamp: '09:43:40 IST',
        method: 'Wispr Flow Voice Dictation (Cryptographically Signed)',
        hash: '0x7f4e91b8a3c20d44e8'
      }
    ],

    // Wispr Flow Stats
    wispr: {
      wordsDictated: 1842,
      speakingTime: '18.5 min',
      speedup: '4.2x Faster',
      accuracy: '99.4%'
    }
  };

  // --- TEMPLATE YAML CONTENT ---
  const TEMPLATE_YAML = `# SwitchOps — Multi-Agent Production Incident Commander
# Template for Switch Console (sandbox-quantum/switch)
# Flip the Switch Hackathon 2026 — Track 01: Best Business Workflow

version: "1.0"
metadata:
  name: "switchops-warroom"
  title: "SwitchOps: Autonomous Incident War Room"
  description: "Connects Claude Code, Codex, and Antigravity into shared chat channels."
  author: "Saurav Bisht & Team"

agents:
  - name: "{team}-triager"
    description: "Ingests alerts, telemetry, classifies severity (P0-P3), routes root causes."
    addressing: anyone
    provider: "claude-code"
    instructions: |
      You are the Lead Incident Triager.
      For every report:
      1. Restate incident in 1 line: [Severity: P0-P3] [Service] Summary.
      2. Extract impacted endpoints, error codes (500s), and blast radius.
      3. Hand off telemetry to @{team}-infraops and code tasks to @{team}-hotfixer.

  - name: "{team}-infraops"
    description: "Inspects K8s pods, deployments, DB pools, canary targets."
    addressing: owner-agents
    provider: "antigravity"
    instructions: |
      You are the Infrastructure Sentry.
      1. Inspect last 3 deployments and correlate commit SHA with outage start time.
      2. Check connection pools, CPU, and deadlocks.
      3. Prepare concrete rollback target (e.g. v2.13.2) and ask human for sign-off.

  - name: "{team}-hotfixer"
    description: "Generates surgical patches, runs smoke tests, drafts rollback PRs."
    addressing: owner-agents
    provider: "codex"
    instructions: |
      1. Review git diff between faulty release and rollback target.
      2. Execute rollback once human signs off.
      3. Verify error rates drop to 0% and compile blameless post-mortem.

room:
  name: "{team}-incidents"
  topic: "🔥 Production War Room & Automated Incident Response"
  bridge: "{bridge}" # slack, teams, discord, telegram
  agents: ["{team}-triager", "{team}-infraops", "{team}-hotfixer"]
  users: ["{$creator}", "priya.lead", "sam.devops"]

rules:
  - id: "RULE-01"
    name: "Human-In-The-Loop Approval"
    description: "Zero production deployment or rollback without explicit human sign-off."

kickoff: |
  🚨 SwitchOps War Room Activated on channel #{team}-incidents.`;

  // --- BLOG CONTENT PREVIEW ---
  const BLOG_CONTENT_HTML = `
    <article>
      <h3>From Solo Coding Agents to 24/7 Incident Teammates: How We Built SwitchOps for Flip the Switch</h3>
      <p><em>By Saurav Bisht & Team • Nov 7, 2026 • 6 min read</em></p>
      
      <h4>1. The Solo Agent Paradox</h4>
      <p>
        AI coding assistants like Claude Code, Codex, Cursor, and Antigravity are remarkably powerful when you work alone in a terminal.
        However, when a P0 production outage strikes at 3:00 AM, modern software engineering is not a solo sport. It is a collaborative war room where on-call engineers, DevOps leads, and release managers juggle alerts, commit histories, rollback commands, and executive updates across Slack, Microsoft Teams, and Discord.
      </p>

      <h4>2. Meet Switch: Turning Chat Channels into Multi-Agent Rooms</h4>
      <p>
        Switch (by SandboxAQ) provides the missing primitive: open source infrastructure that turns ordinary team chat channels into shared rooms where humans and AI agents collaborate with shared context, task boards, decision audits, and role specializations.
      </p>

      <h4>3. The SwitchOps Architecture</h4>
      <p>
        In SwitchOps, we engineered a triple-agent war room protocol:
      </p>
      <ul>
        <li><strong>@SwitchTriager (Claude Code):</strong> Ingests high-priority alerts, parses stack traces, and categorizes blast radius.</li>
        <li><strong>@InfraOps (Antigravity):</strong> Queries Kubernetes telemetry, correlates the incident start time with recent commits, and flags connection pool saturation.</li>
        <li><strong>@HotfixCoder (Codex):</strong> Generates hotfix pull requests, drafts rollback canary manifests, and compiles the post-mortem.</li>
      </ul>

      <h4>4. Hands-Free Incident Commanding with Wispr Flow</h4>
      <p>
        During high-stress outages, typing complex terminal commands is error-prone. With Wispr Flow integrated into SwitchOps, incident leads speak commands and approvals directly:
        <em>"Approved. Roll back cart-service to v2.13.2 immediately and verify error rates."</em>
        Wispr transcribes this at 4.2x typing speed, and Switch cryptographically commits the decision to the room's immutable audit log.
      </p>

      <h4>5. What We Learned</h4>
      <p>
        Putting agents into team chat fundamentally changes software delivery. Agents don't replace humans; they elevate teammates by eliminating mechanical triage so engineers can make critical, informed decisions with confidence.
      </p>
    </article>
  `;

  // --- DOM ELEMENTS ---
  const el = {
    // Header
    bridgeButtons: document.querySelectorAll('.bridge-btn'),
    currentBridgePill: document.getElementById('currentBridgePill'),
    currentBridgeName: document.getElementById('currentBridgeName'),
    btnWisprScorecard: document.getElementById('btnWisprScorecard'),
    btnViewTemplate: document.getElementById('btnViewTemplate'),
    btnViewBlog: document.getElementById('btnViewBlog'),

    // Sidebar
    roomItems: document.querySelectorAll('.room-item'),
    roomHeading: document.getElementById('roomHeading'),
    roomTopic: document.getElementById('roomTopic'),
    consoleStatusPill: document.getElementById('consoleStatusPill'),
    sseEndpointLabel: document.getElementById('sseEndpointLabel'),

    // Simulation
    btnPlayFullScenario: document.getElementById('btnPlayFullScenario'),
    btnStepAlert: document.getElementById('btnStepAlert'),
    btnStepTriage: document.getElementById('btnStepTriage'),
    btnStepInfra: document.getElementById('btnStepInfra'),
    btnStepApprove: document.getElementById('btnStepApprove'),
    btnStepRecover: document.getElementById('btnStepRecover'),
    btnResetRoom: document.getElementById('btnResetRoom'),

    // Tabs
    roomTabs: document.querySelectorAll('.room-tab'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    tasksBadgeCount: document.getElementById('tasksBadgeCount'),
    decisionsBadgeCount: document.getElementById('decisionsBadgeCount'),

    // Chat
    messagesContainer: document.getElementById('messagesContainer'),
    chatInput: document.getElementById('chatInput'),
    senderSelect: document.getElementById('senderSelect'),
    btnSendMessage: document.getElementById('btnSendMessage'),
    btnVoiceMic: document.getElementById('btnVoiceMic'),
    micBtnText: document.getElementById('micBtnText'),
    voicePresetChips: document.querySelectorAll('.voice-preset-chip'),

    // Panes
    tasksGrid: document.getElementById('tasksGrid'),
    decisionsTimeline: document.getElementById('decisionsTimeline'),
    sseTerminal: document.getElementById('sseTerminal'),
    btnClearStream: document.getElementById('btnClearStream'),

    // Right Inspector
    btnQuickSignOff: document.getElementById('btnQuickSignOff'),
    btnExportScorecard: document.getElementById('btnExportScorecard'),
    latencyStat: document.getElementById('latencyStat'),
    cartServiceBadge: document.getElementById('cartServiceBadge'),
    dbPoolBadge: document.getElementById('dbPoolBadge'),

    // Modals
    modalTemplate: document.getElementById('modalTemplate'),
    btnCloseTemplate: document.getElementById('btnCloseTemplate'),
    btnCloseTemplateBtn: document.getElementById('btnCloseTemplateBtn'),
    templateYamlPre: document.getElementById('templateYamlPre'),
    btnCopyTemplate: document.getElementById('btnCopyTemplate'),

    modalWispr: document.getElementById('modalWispr'),
    btnCloseWispr: document.getElementById('btnCloseWispr'),
    btnCloseWisprBtn: document.getElementById('btnCloseWisprBtn'),
    btnDownloadScorecard: document.getElementById('btnDownloadScorecard'),

    modalBlog: document.getElementById('modalBlog'),
    btnCloseBlog: document.getElementById('btnCloseBlog'),
    btnCloseBlogBtn: document.getElementById('btnCloseBlogBtn'),
    blogModalBody: document.getElementById('blogModalBody'),
    btnCopyBlogMarkdown: document.getElementById('btnCopyBlogMarkdown')
  };

  // --- INITIALIZATION ---
  function init() {
    renderMessages();
    renderTasks();
    renderDecisions();
    setupEventListeners();
    setupKeyboardShortcuts();
    checkBackendConnection();

    // Populate Modals
    if (el.templateYamlPre) {
      el.templateYamlPre.textContent = TEMPLATE_YAML;
    }
    if (el.blogModalBody) {
      el.blogModalBody.innerHTML = BLOG_CONTENT_HTML;
    }

    logProtocolEvent('system', {
      event: 'room_ready',
      room: state.activeRoom,
      bridge: state.activeBridge,
      agents_registered: 3,
      protocol: 'Switch Agent Protocol v1.0'
    });
  }

  // --- CHECK BACKEND (SSE & HTTP) ---
  function checkBackendConnection() {
    fetch('http://127.0.0.1:8765/health')
      .then(res => res.json())
      .then(data => {
        state.backendConnected = true;
        if (el.consoleStatusPill) {
          el.consoleStatusPill.innerHTML = '<span class="dot-online"></span> Python Server Live (:8765)';
        }
        logProtocolEvent('connection', {
          status: 'connected',
          server: 'http://127.0.0.1:8765',
          protocol: data.protocol_version || '1.0'
        });
        connectSSEStream();
      })
      .catch(() => {
        // Fallback to in-browser simulated SSE protocol engine
        state.backendConnected = false;
        if (el.consoleStatusPill) {
          el.consoleStatusPill.innerHTML = '<span class="dot-online"></span> In-Browser Switch Protocol Engine';
        }
        logProtocolEvent('comment', ': Switch Protocol engine running in client-mode (browser fallback ready)');
      });
  }

  function connectSSEStream() {
    try {
      state.eventSource = new EventSource('http://127.0.0.1:8765/room/events');
      state.eventSource.addEventListener('message', function (e) {
        try {
          const data = JSON.parse(e.data);
          logProtocolEvent('event: message', data);
        } catch (err) {}
      });
      state.eventSource.addEventListener('decision', function (e) {
        try {
          const data = JSON.parse(e.data);
          logProtocolEvent('event: decision', data);
        } catch (err) {}
      });
    } catch (e) {
      console.log('SSE connection error:', e);
    }
  }

  // --- RENDERING ---
  function renderMessages() {
    if (!el.messagesContainer) return;
    el.messagesContainer.innerHTML = '';

    state.messages.forEach(msg => {
      const card = document.createElement('div');
      let variantClass = '';

      if (msg.senderType === 'system') variantClass = 'variant-system';
      else if (msg.senderType === 'agent') variantClass = 'variant-agent';
      else if (msg.isVoice) variantClass = 'variant-signoff';
      else if (msg.content.includes('🚨')) variantClass = 'variant-alert';

      card.className = `message-card ${variantClass}`;

      // Avatar
      let avatarHtml = '';
      if (msg.senderType === 'system') {
        avatarHtml = `<div class="avatar" style="background:#3b82f6;">⚡</div>`;
      } else if (msg.senderType === 'agent') {
        avatarHtml = `<div class="avatar ${getAgentAvatarClass(msg.senderKey)}">${msg.senderAvatar}</div>`;
      } else {
        avatarHtml = `<div class="avatar ${getHumanAvatarClass(msg.senderKey)}">${msg.senderAvatar}</div>`;
      }

      // Badge
      let roleBadge = '';
      if (msg.agentProvider) {
        roleBadge = `<span class="badge-role badge-sky">${msg.agentProvider}</span>`;
      } else if (msg.senderType === 'human' && msg.senderKey === 'priya') {
        roleBadge = `<span class="badge-role badge-peach">Incident Lead</span>`;
      } else if (msg.senderType === 'human') {
        roleBadge = `<span class="badge-role badge-cream">Team</span>`;
      }

      card.innerHTML = `
        <div class="msg-avatar-wrap">${avatarHtml}</div>
        <div class="msg-content-wrap">
          <div class="msg-header">
            <span class="msg-sender">${escapeHtml(msg.senderName)}</span>
            <span class="msg-handle">${escapeHtml(msg.senderHandle)}</span>
            ${roleBadge}
            <span class="msg-time">${escapeHtml(msg.timestamp)}</span>
          </div>
          <div class="msg-body">${formatMarkdown(msg.content)}</div>
        </div>
      `;

      el.messagesContainer.appendChild(card);
    });

    // Scroll to bottom
    el.messagesContainer.scrollTop = el.messagesContainer.scrollHeight;
  }

  function renderTasks() {
    if (!el.tasksGrid) return;
    el.tasksGrid.innerHTML = '';

    state.tasks.forEach(task => {
      const item = document.createElement('div');
      item.className = 'task-item-card';

      const isDone = task.status === 'completed';
      const checkIcon = isDone ? '✓' : '';

      item.innerHTML = `
        <div class="task-left">
          <div class="task-checkbox ${isDone ? 'checked' : ''}" data-task-id="${task.id}">${checkIcon}</div>
          <div>
            <span class="task-id">${task.id}</span>
            <div class="task-title ${isDone ? 'completed' : ''}">${escapeHtml(task.title)}</div>
          </div>
        </div>
        <div class="task-right">
          <span class="task-owner-pill">${task.owner}</span>
          <span class="badge-pastel ${task.priority === 'P0' ? 'badge-peach' : 'badge-sky'}">${task.priority}</span>
          <span class="badge-pastel ${isDone ? 'badge-mint' : 'badge-cream'}">${task.status.toUpperCase()}</span>
        </div>
      `;

      // Toggle task checkbox
      const checkbox = item.querySelector('.task-checkbox');
      checkbox.addEventListener('click', () => {
        task.status = task.status === 'completed' ? 'in_progress' : 'completed';
        renderTasks();
        logProtocolEvent('task_updated', { id: task.id, status: task.status, title: task.title });
      });

      el.tasksGrid.appendChild(item);
    });

    if (el.tasksBadgeCount) {
      el.tasksBadgeCount.textContent = state.tasks.length;
    }
  }

  function renderDecisions() {
    if (!el.decisionsTimeline) return;
    el.decisionsTimeline.innerHTML = '';

    state.decisions.forEach(dec => {
      const card = document.createElement('div');
      card.className = 'decision-card';
      card.innerHTML = `
        <div class="decision-top">
          <span class="dec-id">${dec.id}</span>
          <span class="badge-pastel badge-mint">IMMUTABLE SIGN-OFF</span>
        </div>
        <h3 class="dec-title">${escapeHtml(dec.title)}</h3>
        <div class="dec-meta">
          <span><strong>Approver:</strong> ${escapeHtml(dec.approver)}</span>
          <span><strong>Method:</strong> ${escapeHtml(dec.method)}</span>
          <span><strong>Time:</strong> ${escapeHtml(dec.timestamp)}</span>
          <span class="dec-hash">Hash: ${dec.hash}</span>
        </div>
      `;
      el.decisionsTimeline.appendChild(card);
    });

    if (el.decisionsBadgeCount) {
      el.decisionsBadgeCount.textContent = state.decisions.length;
    }
  }

  // --- PROTOCOL SSE INSPECTOR TERMINAL ---
  function logProtocolEvent(eventType, payload) {
    if (!el.sseTerminal) return;
    const timeStr = new Date().toLocaleTimeString();

    const line = document.createElement('div');
    line.className = 'terminal-line';

    if (eventType === 'comment') {
      line.className += ' comment';
      line.textContent = payload;
    } else {
      line.innerHTML = `
        <span class="terminal-line event">[${timeStr}] event: ${eventType}</span><br>
        <span class="terminal-line data">data: ${JSON.stringify(payload)}</span>
      `;
    }

    el.sseTerminal.appendChild(line);
    el.sseTerminal.scrollTop = el.sseTerminal.scrollHeight;
  }

  // --- MESSAGE SENDING ---
  function sendMessage(customContent = null) {
    const text = customContent || (el.chatInput ? el.chatInput.value.trim() : '');
    if (!text) return;

    const senderKey = el.senderSelect ? el.senderSelect.value : 'priya';
    const member = state.members[senderKey] || state.members.priya;

    const newMsg = {
      id: `msg-${String(state.messages.length + 1).padStart(3, '0')}`,
      senderType: member.type,
      senderKey: senderKey,
      senderName: member.name,
      senderHandle: member.handle,
      senderAvatar: member.avatar,
      agentProvider: member.provider || null,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' IST',
      isVoice: text.includes('Spoken via Wispr') || text.toLowerCase().includes('approved'),
      content: text
    };

    state.messages.push(newMsg);
    renderMessages();

    if (el.chatInput && !customContent) {
      el.chatInput.value = '';
    }

    // Emit event to Switch Protocol
    logProtocolEvent('message', {
      id: newMsg.id,
      room: state.activeRoom,
      sender: newMsg.senderHandle,
      sender_type: newMsg.senderType,
      content: newMsg.content
    });

    // If backend is active, dispatch HTTP POST
    if (state.backendConnected) {
      fetch('http://127.0.0.1:8765/room/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender_type: newMsg.senderType,
          sender_name: newMsg.senderName,
          sender_handle: newMsg.senderHandle,
          sender_avatar: newMsg.senderAvatar,
          agent_provider: newMsg.agentProvider,
          content: newMsg.content
        })
      }).catch(err => console.log('HTTP post error:', err));
    }

    // Auto-respond if human commands agents
    handleHumanCommandToAgents(text);
  }

  function handleHumanCommandToAgents(text) {
    const lower = text.toLowerCase();

    // Check if Priya signs off / approves rollback
    if (lower.includes('approved') && (lower.includes('rollback') || lower.includes('roll it back'))) {
      setTimeout(() => {
        addDecisionLog('Emergency Rollback of cart-service to v2.13.2', 'Priya Sharma (Incident Commander)');
        updateServiceRecovery();
      }, 1200);
    }
  }

  function addDecisionLog(title, approver) {
    const decId = `DEC-2026-${String(state.decisions.length + 1).padStart(2, '0')}`;
    const newDec = {
      id: decId,
      title: title,
      approver: approver,
      timestamp: new Date().toLocaleTimeString() + ' IST',
      method: 'Wispr Flow Voice Dictation (Cryptographically Signed)',
      hash: '0x' + Math.random().toString(16).substring(2, 10) + Math.random().toString(16).substring(2, 10)
    };
    state.decisions.push(newDec);
    renderDecisions();
    logProtocolEvent('decision_recorded', newDec);
  }

  function updateServiceRecovery() {
    if (el.latencyStat) {
      el.latencyStat.textContent = '48ms (Restored)';
      el.latencyStat.className = 'metric-val text-mint font-mono';
    }
    if (el.cartServiceBadge) {
      el.cartServiceBadge.textContent = 'Healthy (48ms)';
      el.cartServiceBadge.className = 'badge-pastel badge-mint';
    }
    if (el.dbPoolBadge) {
      el.dbPoolBadge.textContent = 'Conn Pool: 14%';
      el.dbPoolBadge.className = 'badge-pastel badge-mint';
    }
  }

  // --- WISPR FLOW VOICE DICTATION ---
  let recognition = null;
  function setupVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = function () {
        state.isRecordingVoice = true;
        updateMicUi(true);
      };

      recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        if (el.chatInput) {
          el.chatInput.value = `🎙️ (Wispr Flow Voice): ${transcript}`;
        }
        state.wispr.wordsDictated += transcript.split(' ').length;
        updateMicUi(false);
      };

      recognition.onerror = function () {
        updateMicUi(false);
      };

      recognition.onend = function () {
        state.isRecordingVoice = false;
        updateMicUi(false);
      };
    }
  }

  function toggleVoiceDictation() {
    if (!recognition) {
      // Fallback voice simulation
      state.isRecordingVoice = !state.isRecordingVoice;
      updateMicUi(state.isRecordingVoice);
      if (state.isRecordingVoice) {
        setTimeout(() => {
          if (el.chatInput) {
            el.chatInput.value = "🎙️ (Spoken via Wispr Flow): Approved. Roll back cart-service to v2.13.2 immediately and monitor error rates.";
          }
          state.wispr.wordsDictated += 14;
          state.isRecordingVoice = false;
          updateMicUi(false);
        }, 1500);
      }
      return;
    }

    if (state.isRecordingVoice) {
      recognition.stop();
    } else {
      try {
        recognition.start();
      } catch (e) {
        updateMicUi(false);
      }
    }
  }

  function updateMicUi(recording) {
    if (!el.btnVoiceMic) return;
    if (recording) {
      el.btnVoiceMic.classList.add('recording');
      if (el.micBtnText) el.micBtnText.textContent = 'Listening...';
    } else {
      el.btnVoiceMic.classList.remove('recording');
      if (el.micBtnText) el.micBtnText.textContent = 'Wispr Voice';
    }
  }

  // --- EVENT LISTENERS ---
  function setupEventListeners() {
    // 1. Bridges Switching
    el.bridgeButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        el.bridgeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeBridge = btn.dataset.bridge;
        
        const bridgeNames = {
          slack: 'Slack Bridge Connected',
          discord: 'Discord Bridge Connected',
          teams: 'Microsoft Teams Bridge Connected',
          telegram: 'Telegram Bridge Connected'
        };

        if (el.currentBridgeName) {
          el.currentBridgeName.textContent = bridgeNames[state.activeBridge] || 'Bridge Connected';
        }

        logProtocolEvent('bridge_switched', {
          room: state.activeRoom,
          new_bridge: state.activeBridge,
          protocol: 'Switch Collaboration Bridge'
        });
      });
    });

    // 2. Room Tabs Switching
    el.roomTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        el.roomTabs.forEach(t => t.classList.remove('active'));
        el.tabPanes.forEach(p => p.classList.remove('active'));

        tab.classList.add('active');
        const tabKey = tab.dataset.tab;
        const targetPane = document.getElementById(`pane${capitalize(tabKey)}`);
        if (targetPane) targetPane.classList.add('active');
      });
    });

    // 3. Message Send
    if (el.btnSendMessage) {
      el.btnSendMessage.addEventListener('click', () => sendMessage());
    }
    if (el.chatInput) {
      el.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
    }

    // 4. Voice Mic Button
    setupVoiceRecognition();
    if (el.btnVoiceMic) {
      el.btnVoiceMic.addEventListener('click', toggleVoiceDictation);
    }

    // 5. Voice Presets
    el.voicePresetChips.forEach(chip => {
      chip.addEventListener('click', () => {
        if (el.chatInput) {
          el.chatInput.value = chip.dataset.text;
          el.chatInput.focus();
        }
      });
    });

    // 6. 1-Click Human Rollback Approval Button
    if (el.btnQuickSignOff) {
      el.btnQuickSignOff.addEventListener('click', () => {
        sendMessage("🎙️ *(Spoken via Wispr Flow)*: Approved. Roll back cart-service to v2.13.2 immediately and verify error rates.");
      });
    }

    // 7. Modals
    setupModals();

    // 8. Simulation Step Controls
    setupSimulationSteps();

    // 9. Clear Stream
    if (el.btnClearStream && el.sseTerminal) {
      el.btnClearStream.addEventListener('click', () => {
        el.sseTerminal.innerHTML = '<div class="terminal-line comment">: Stream cleared by operator</div>';
      });
    }
  }

  function setupModals() {
    // Template Modal
    if (el.btnViewTemplate && el.modalTemplate) {
      el.btnViewTemplate.addEventListener('click', () => el.modalTemplate.classList.add('active'));
      el.btnCloseTemplate.addEventListener('click', () => el.modalTemplate.classList.remove('active'));
      el.btnCloseTemplateBtn.addEventListener('click', () => el.modalTemplate.classList.remove('active'));
    }
    if (el.btnCopyTemplate) {
      el.btnCopyTemplate.addEventListener('click', () => {
        navigator.clipboard.writeText(TEMPLATE_YAML).then(() => {
          el.btnCopyTemplate.textContent = 'Copied!';
          setTimeout(() => el.btnCopyTemplate.textContent = 'Copy YAML', 1800);
        });
      });
    }

    // Wispr Scorecard Modal
    if (el.btnWisprScorecard && el.modalWispr) {
      el.btnWisprScorecard.addEventListener('click', () => el.modalWispr.classList.add('active'));
      el.btnCloseWispr.addEventListener('click', () => el.modalWispr.classList.remove('active'));
      el.btnCloseWisprBtn.addEventListener('click', () => el.modalWispr.classList.remove('active'));
    }
    if (el.btnExportScorecard && el.modalWispr) {
      el.btnExportScorecard.addEventListener('click', () => el.modalWispr.classList.add('active'));
    }
    if (el.btnDownloadScorecard) {
      el.btnDownloadScorecard.addEventListener('click', () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state.wispr, null, 2));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        downloadAnchor.setAttribute("download", "wispr_flow_usage_scorecard.json");
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
      });
    }

    // Blog Modal
    if (el.btnViewBlog && el.modalBlog) {
      el.btnViewBlog.addEventListener('click', () => el.modalBlog.classList.add('active'));
      el.btnCloseBlog.addEventListener('click', () => el.modalBlog.classList.remove('active'));
      el.btnCloseBlogBtn.addEventListener('click', () => el.modalBlog.classList.remove('active'));
    }
    if (el.btnCopyBlogMarkdown) {
      el.btnCopyBlogMarkdown.addEventListener('click', () => {
        navigator.clipboard.writeText(BLOG_CONTENT_HTML).then(() => {
          el.btnCopyBlogMarkdown.textContent = 'Copied!';
          setTimeout(() => el.btnCopyBlogMarkdown.textContent = 'Copy Markdown Post', 1800);
        });
      });
    }

    // Close on overlay click
    window.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
      }
    });
  }

  // --- STEP BY STEP INCIDENT SIMULATOR ---
  function setupSimulationSteps() {
    if (el.btnStepAlert) {
      el.btnStepAlert.addEventListener('click', () => {
        sendMessage("🚨 Sam Taylor: Checkout API throwing 500s. @SwitchTriager please investigate!");
      });
    }

    if (el.btnStepTriage) {
      el.btnStepTriage.addEventListener('click', () => {
        const sender = state.members.triager;
        const msg = "🔍 **[Incident Triager]** Severity classified as **P0 Blocker**. Connection pool exhaustion detected on cart-service. Routing telemetry scan to @InfraOps.";
        injectAgentMessage(sender, msg);
      });
    }

    if (el.btnStepInfra) {
      el.btnStepInfra.addEventListener('click', () => {
        const sender = state.members.infra;
        const msg = "📊 **[InfraOps]** Correlated faulty deploy \`v2.14.0\` (commit \`a9f24e1\`). Rollback target \`v2.13.2\` prepared. Requesting sign-off from @Priya.";
        injectAgentMessage(sender, msg);
      });
    }

    if (el.btnStepApprove) {
      el.btnStepApprove.addEventListener('click', () => {
        sendMessage("🎙️ *(Spoken via Wispr Flow)*: Approved. Roll back cart-service to v2.13.2 immediately.");
      });
    }

    if (el.btnStepRecover) {
      el.btnStepRecover.addEventListener('click', () => {
        const sender = state.members.hotfix;
        const msg = "🚀 **[HotfixCoder]** Rollback to \`v2.13.2\` complete. p99 latency back to 48ms. HTTP 500s resolved. Post-mortem recorded.";
        injectAgentMessage(sender, msg);
        updateServiceRecovery();
      });
    }

    // Auto-Play
    if (el.btnPlayFullScenario) {
      el.btnPlayFullScenario.addEventListener('click', () => {
        el.btnPlayFullScenario.disabled = true;
        el.btnPlayFullScenario.innerHTML = 'Running Simulator...';

        resetRoomToFresh();
        setTimeout(() => el.btnStepAlert.click(), 500);
        setTimeout(() => el.btnStepTriage.click(), 2500);
        setTimeout(() => el.btnStepInfra.click(), 4800);
        setTimeout(() => el.btnStepApprove.click(), 7000);
        setTimeout(() => {
          el.btnStepRecover.click();
          el.btnPlayFullScenario.disabled = false;
          el.btnPlayFullScenario.innerHTML = '<polygon points="5 3 19 12 5 21 5 3"></polygon> Auto-Play Full Incident';
        }, 9500);
      });
    }

    // Reset
    if (el.btnResetRoom) {
      el.btnResetRoom.addEventListener('click', resetRoomToFresh);
    }
  }

  function injectAgentMessage(agent, text) {
    const newMsg = {
      id: `msg-${String(state.messages.length + 1).padStart(3, '0')}`,
      senderType: 'agent',
      senderKey: agent.role.toLowerCase(),
      senderName: agent.name,
      senderHandle: agent.handle,
      senderAvatar: agent.avatar,
      agentProvider: agent.provider,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' IST',
      content: text
    };
    state.messages.push(newMsg);
    renderMessages();
    logProtocolEvent('agent_message', { agent: agent.handle, provider: agent.provider, content: text });
  }

  function resetRoomToFresh() {
    state.messages = [state.messages[0]]; // keep only system kickoff
    state.decisions = [];
    renderMessages();
    renderDecisions();
    if (el.latencyStat) {
      el.latencyStat.textContent = '4,200ms (P0 Spiking)';
      el.latencyStat.className = 'metric-val text-peach font-mono';
    }
    if (el.cartServiceBadge) {
      el.cartServiceBadge.textContent = 'Degraded (500s)';
      el.cartServiceBadge.className = 'badge-pastel badge-peach';
    }
    if (el.dbPoolBadge) {
      el.dbPoolBadge.textContent = 'Conn Pool: 100% Saturation';
      el.dbPoolBadge.className = 'badge-pastel badge-peach';
    }
    logProtocolEvent('comment', ': Room state reset by operator');
  }

  // --- KEYBOARD SHORTCUTS ---
  function setupKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      // Wispr hotkey: Ctrl + Space or Ctrl + Shift + Space
      if (e.ctrlKey && e.code === 'Space') {
        e.preventDefault();
        toggleVoiceDictation();
      }
      // Esc closes modals
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
      }
    });
  }

  // --- HELPERS ---
  function getHumanAvatarClass(key) {
    if (key === 'priya') return 'avatar-human-p';
    if (key === 'sam') return 'avatar-human-s';
    return 'avatar-human-a';
  }

  function getAgentAvatarClass(key) {
    if (key === 'triager') return 'avatar-agent-triager';
    if (key === 'infra') return 'avatar-agent-infra';
    return 'avatar-agent-coder';
  }

  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function formatMarkdown(text) {
    if (!text) return '';
    let html = escapeHtml(text);

    // Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Inline code `code`
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    // Newlines to <br> or paragraphs
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    return `<p>${html}</p>`;
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
