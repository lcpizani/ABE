# OpenClaw Configuration — ABE Agent

This document describes the OpenClaw runtime configuration for the ABE agent, sourced from `~/.openclaw/openclaw.json` and the registered cron jobs.

---

## Agent Definition

ABE is registered in the `agents.list` array with the following settings:

```json
{
  "id": "abe",
  "name": "abe",
  "workspace": "<path/to/workspace>`",
  "agentDir": "~/.openclaw/agents/abe/agent",
  "model": "anthropic/claude-sonnet-4-0"
}
```

| Field | Value | Notes |
|---|---|---|
| `id` | `abe` | Used to reference the agent in cron jobs and bindings |
| `workspace` | `<path/to/workspace>` | Root directory OpenClaw mounts for file access |
| `agentDir` | `~/.openclaw/agents/abe/agent` | Where OpenClaw stores agent-level state (models, auth profiles) |
| `model` | `anthropic/claude-sonnet-4-0` | Primary model; overrides the global default |

### Global Model Default

The `agents.defaults` block sets the fallback for all agents:

```json
{
  "model": { "primary": "anthropic/claude-sonnet-4-6" },
  "workspace": "<path/to/workspace>",
  "compaction": { "memoryFlush": { "enabled": false } },
  "memorySearch": { "enabled": false }
}
```

ABE explicitly overrides the model to `claude-sonnet-4-0` and also disables session-level memory search:

```json
"memorySearch": {
  "experimental": { "sessionMemory": false }
}
```

---

## Tool Permissions

ABE uses the `full` tool profile with the following tools explicitly allowed:

| Category | Tools |
|---|---|
| File I/O | `read`, `write`, `edit`, `apply_patch` |
| Execution | `exec`, `code_execution`, `process` |
| Memory | `memory_search`, `memory_get` |
| Web | `web_search`, `web_fetch`, `x_search` |
| Messaging | `tts`, `gateway` |
| Media | `image`, `image_generate` |
| Sessions | `sessions_spawn`, `sessions_yield`, `subagents` |
| Scheduling | `cron` |
| System | `nodes`, `browser`, `canvas`, `agents_list` |

---

## Channel Binding

ABE is bound exclusively to the Telegram channel:

```json
"bindings": [
  {
    "agentId": "abe",
    "match": { "channel": "telegram" }
  }
]
```

All messages arriving on Telegram are routed to the `abe` agent.

### Telegram Channel Settings

```json
"channels": {
  "telegram": {
    "enabled": true,
    "dmPolicy": "open",
    "groupPolicy": "allowlist",
    "streaming": "partial"
  }
}
```

| Setting | Value | Meaning |
|---|---|---|
| `dmPolicy` | `open` | Any Telegram user can DM ABE |
| `groupPolicy` | `allowlist` | Groups must be explicitly allowed |
| `streaming` | `partial` | Sends partial responses as they stream |

## TTS (Text-to-Speech)

```json
"messages": {
  "tts": {
    "auto": "always",
    "provider": "microsoft",
    "providers": {
      "microsoft": { "voice": "en-US-AndrewNeural" }
    },
    "maxTextLength": 4000
  }
}
```

| Setting | Value |
|---|---|
| Provider | Microsoft Azure TTS |
| Voice | `en-US-AndrewNeural` |
| Auto-send | Always (when TTS is enabled for the session) |
| Max text length | 4,000 characters |

---

## Gateway

The local gateway exposes a REST API used by heartbeat scripts and internal tooling:

```json
"gateway": {
  "port": 18789,
  "mode": "local",
  "bind": "loopback",
  "auth": { "mode": "token" },
  "tailscale": { "mode": "off" }
}
```

| Setting | Value |
|---|---|
| Port | `18789` |
| Bind | Loopback only (`127.0.0.1`) |
| Auth | Bearer token |
| Tailscale | Disabled |

The following canvas commands are denied over the gateway (nodes cannot invoke them):

- `canvas.eval`
- `canvas.a2ui.push` / `pushJSONL` / `reset`
- `canvas.navigate`
- `canvas.snapshot`

---

## Cron Jobs

Five jobs are registered under `agentId: abe`. All use `sessionTarget: isolated` (each run gets a fresh session) and `wakeMode: now` (fires immediately when the interval elapses).

| Name | Interval | Timeout | Trigger Message |
|---|---|---|---|
| `daily-price-check` | 30 min | 120 s | `Run your daily price check heartbeat task.` |
| `daily-calendar-reminders` | 30 min | 120 s | `Run your daily calendar reminders heartbeat task.` |
| `weekly-margin-refresh` | 30 min | 180 s | `Run your weekly margin refresh heartbeat task.` |

> **Current state:** All three active jobs are in a timeout error loop as of 2026-04-14. The heartbeat scripts exceed the timeout budget. See [heartbeat.md](../for-developers/heartbeat.md) for the script implementation.

Delivery is configured as:

```json
"delivery": {
  "mode": "announce",
  "channel": "last",
  "bestEffort": false
}
```

`bestEffort: false` means failed deliveries are retried; `channel: last` sends to the most recently active Telegram conversation.

### Registering / Updating a Cron Job

```bash
# Add a new job
openclaw cron add --agent abe --name "job-name" \
  --every 30m \
  --message "Run your <task> heartbeat task." \
  --timeout-seconds 120

# List all jobs
openclaw cron list --agent abe

# Remove a job
openclaw cron remove --agent abe --name "job-name"
```

See [deployment.md](../for-staff/deployment.md) for the original registration commands with timezone and cron-expression variants.

---

## Session Scope

```json
"session": {
  "dmScope": "per-channel-peer"
}
```

Each Telegram user gets their own isolated session context. Conversations between different farmers never share context.

---

## Commands

```json
"commands": {
  "native": "auto",
  "nativeSkills": "auto",
  "restart": true,
  "ownerDisplay": "raw"
}
```

| Setting | Meaning |
|---|---|
| `native: auto` | Native OpenClaw commands are auto-detected |
| `nativeSkills: auto` | Skills registered in the workspace are auto-loaded |
| `restart: true` | `!restart` command is enabled for the agent owner |
| `ownerDisplay: raw` | Owner sees raw tool output, not formatted summaries |

---

## Version

Configuration last touched by OpenClaw version `2026.4.5` on `2026-04-14`.
