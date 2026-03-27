# OS-APOW Architecture

**Document Version:** 1.0  
**Last Updated:** 2026-03-27  
**Status:** Planning

---

## Executive Summary

OS-APOW (OpenSource AI-Powered Orchestration Workflow) represents a paradigm shift from **Interactive AI Coding** to **Headless Agentic Orchestration**. The system transforms standard project management artifacts—specifically GitHub Issues—into "Execution Orders" that are autonomously fulfilled by specialized AI agents.

**Core Principle:** Zero-Touch Construction — a user opens a single "Specification Issue" and receives a functional, test-passed branch and PR without manual intervention.

---

## System Architecture (4 Pillars)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           OS-APOW System                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   THE EAR    │    │  THE STATE   │    │  THE BRAIN   │              │
│  │   (Notifier) │    │   (Queue)    │    │  (Sentinel)  │              │
│  │              │    │              │    │              │              │
│  │  FastAPI     │    │  GitHub      │    │  Async       │              │
│  │  Webhook     │◄───┤  Issues &    │◄───┤  Python      │              │
│  │  Receiver    │    │  Labels      │    │  Service     │              │
│  └──────┬───────┘    └──────────────┘    └──────┬───────┘              │
│         │                                        │                      │
│         │                                        │                      │
│         │           ┌──────────────┐            │                      │
│         │           │  THE HANDS   │            │                      │
│         └──────────►│  (Worker)    │◄───────────┘                      │
│                     │              │                                   │
│                     │  Opencode    │                                   │
│                     │  DevContainer│                                   │
│                     └──────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Pillar 1: The Ear (Work Event Notifier)

### Technology Stack
- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic

### Role
Primary gateway for external stimuli and asynchronous triggers.

### Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Secure Webhook Ingestion** | Hardened endpoint for GitHub events (issues, issue_comment, pull_request) |
| **Cryptographic Verification** | HMAC SHA256 validation against WEBHOOK_SECRET |
| **Intelligent Triage** | Parse markdown body, detect intent, apply appropriate labels |
| **Queue Initialization** | Apply `agent:queued` label via GitHub REST API |

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhooks/github` | POST | GitHub webhook receiver |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger/OpenAPI documentation |

### Security
- Rejects requests with invalid/missing `X-Hub-Signature-256` header
- Returns 401 Unauthorized for malformed signatures
- Returns 202 Accepted within 10-second GitHub timeout

---

## Pillar 2: The State (Work Queue)

### Implementation
Distributed state management via GitHub Issues, Labels, and Milestones.

### Philosophy
**"Markdown as a Database"** — GitHub Issues serve as the persistence layer, providing:
- World-class audit logs
- Transparent versioning
- Out-of-the-box UI for human supervision
- Real-time intervention via commenting

### State Machine

```
┌─────────────────────────────────────────────────────────────────┐
│                     Task State Transitions                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────┐     Claim      ┌──────────────┐               │
│   │  QUEUED   │ ──────────────►│ IN_PROGRESS  │               │
│   │agent:queued│               │agent:in-     │               │
│   └───────────┘                │  progress    │               │
│        ▲                       └──────┬───────┘               │
│        │                              │                        │
│        │ Re-queue                     │ Complete               │
│        │ (Stale)                      │                        │
│        │                       ┌──────▼───────┐               │
│   ┌────┴──────┐               │              │               │
│   │RECONCILING│               │   SUCCESS    │               │
│   │agent:     │               │agent:success │               │
│   │reconciling│               │              │               │
│   └───────────┘               └──────────────┘               │
│                                      ▲                        │
│                                      │                        │
│                               ┌──────┴───────┐               │
│                               │    ERROR     │               │
│                               │agent:error   │               │
│                               │OR            │               │
│                               │INFRA_FAILURE │               │
│                               └──────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Label Taxonomy

| Label | Status | Description |
|-------|--------|-------------|
| `agent:queued` | QUEUED | Task passed validation, awaiting Sentinel |
| `agent:in-progress` | IN_PROGRESS | Sentinel claimed the issue |
| `agent:reconciling` | RECONCILING | Stale task being recovered |
| `agent:success` | SUCCESS | Terminal success state |
| `agent:error` | ERROR | Logic/implementation failure |
| `agent:infra-failure` | INFRA_FAILURE | Infrastructure failure |
| `agent:stalled-budget` | STALLED_BUDGET | Budget exceeded (future) |

### Concurrency Control
Uses GitHub "Assignees" as distributed lock semaphore:
1. Assign Sentinel bot account to issue
2. Re-fetch the issue
3. Verify current assignee matches
4. Only then proceed with work

---

## Pillar 3: The Brain (Sentinel Orchestrator)

### Technology Stack
- Python 3.12+ (Async)
- HTTPX (async HTTP client)
- PowerShell Core (shell bridge)
- Docker CLI

### Role
Persistent supervisor managing worker lifecycle and mapping high-level intent to shell commands.

### Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sentinel Lifecycle                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. POLLING DISCOVERY                                           │
│     └─► Query GitHub API every 60s for agent:queued issues     │
│     └─► Apply jittered exponential backoff on rate-limit       │
│                                                                 │
│  2. AUTH SYNCHRONIZATION                                        │
│     └─► Run gh-auth.ps1 to ensure valid installation tokens    │
│                                                                 │
│  3. TASK CLAIMING                                               │
│     └─► Assign-then-verify distributed locking                 │
│     └─► Update labels: queued → in-progress                    │
│     └─► Post claim comment                                     │
│                                                                 │
│  4. ENVIRONMENT PROVISIONING                                    │
│     └─► devcontainer-opencode.sh up                            │
│     └─► devcontainer-opencode.sh start                         │
│                                                                 │
│  5. TASK EXECUTION                                              │
│     └─► devcontainer-opencode.sh prompt "{workflow}"           │
│     └─► Stream stdout to worker_run_ID.jsonl                   │
│     └─► Post heartbeat every 5 minutes                         │
│                                                                 │
│  6. FINALIZATION                                                │
│     └─► Detect subprocess exit code                            │
│     └─► Update labels: in-progress → success/error             │
│     └─► Post final comment with results                        │
│                                                                 │
│  7. ENVIRONMENT RESET                                           │
│     └─► devcontainer-opencode.sh stop                          │
│     └─► Prevent state bleed between tasks                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Shell-Bridge Protocol

| Command | Purpose | Timeout |
|---------|---------|---------|
| `up` | Provision Docker network and volumes | 60s |
| `start` | Launch opencode-server in container | 60s |
| `prompt` | Execute workflow instruction | 5700s |
| `stop` | Stop container (preserve state) | 60s |
| `down` | Full teardown (rare) | 300s |

### Telemetry
- **Worker Output:** Captured to `worker_run_ID_TIMESTAMP.jsonl`
- **Public Telemetry:** Sanitized via `scrub_secrets()` before GitHub comments
- **Heartbeat:** Posted every 5 minutes for long-running tasks

### Graceful Shutdown
- Handles `SIGTERM` and `SIGINT`
- Sets shutdown flag, finishes current task
- Closes HTTPX connection pool
- Prevents orphaned `agent:in-progress` issues

---

## Pillar 4: The Hands (Opencode Worker)

### Technology Stack
- opencode CLI
- LLM Core (GLM-5)
- DevContainer (Docker)

### Role
Execution layer where actual coding happens in an isolated, reproducible environment.

### Worker Capabilities

| Capability | Description |
|------------|-------------|
| **Contextual Awareness** | Access to local project structure, vector-indexed codebase |
| **Instructional Logic** | Reads markdown workflows from `/local_ai_instruction_modules/` |
| **Verification** | Runs local test suites before submitting PR |

### Environment Isolation

| Constraint | Value | Purpose |
|------------|-------|---------|
| **CPU Limit** | 2 CPUs | Prevent DoS on host |
| **RAM Limit** | 4GB | Prevent memory exhaustion |
| **Network** | Isolated bridge | No access to host subnet |
| **Credentials** | Ephemeral env vars | Never written to disk |

---

## Key Architectural Decisions (ADRs)

### ADR 07: Standardized Shell-Bridge Execution

**Decision:** Orchestrator interacts with agentic environment exclusively via `devcontainer-opencode.sh`.

**Rationale:** Reusing shell scripts guarantees environment parity between AI agent and human developers. Avoids "Configuration Drift."

**Consequence:** Python code focuses on logic/state; Shell scripts handle container orchestration.

---

### ADR 08: Polling-First Resiliency Model

**Decision:** Sentinel uses polling as primary discovery; webhooks are optimization.

**Rationale:** Webhooks are "fire and forget." Polling ensures state reconciliation on restart, making the system self-healing.

**Consequence:** System resilient against server downtime and network partitions.

---

### ADR 09: Provider-Agnostic Interface Layer

**Decision:** All queue interactions abstracted behind `ITaskQueue` interface.

**Rationale:** Enables future swapping to Linear, Notion, or SQL queues without rewriting orchestrator logic.

**Consequence:** `GitHubQueue` implements interface; other providers can be added without core changes.

---

## Data Flow (Happy Path)

```
1. User opens GitHub Issue with [Plan] title
                │
                ▼
2. GitHub Webhook hits Notifier (FastAPI)
                │
                ▼
3. Notifier validates HMAC signature
                │
                ▼
4. Notifier applies agent:queued label
                │
                ▼
5. Sentinel poller detects new label
                │
                ▼
6. Sentinel claims issue (assign-then-verify)
                │
                ▼
7. Sentinel runs devcontainer-opencode.sh up
                │
                ▼
8. Sentinel sends prompt to Worker
                │
                ▼
9. Worker executes workflow, creates PR
                │
                ▼
10. Sentinel detects completion, applies agent:success
```

---

## Security Architecture

### Network Isolation
- Worker containers run in dedicated Docker network
- Cannot access host network or local subnet
- Internet access for packages only

### Credential Management
- GitHub App Installation Tokens injected as temporary env vars
- Credentials destroyed when container exits
- Never written to disk within container

### Credential Scrubbing
All worker output passed through `scrub_secrets()` before GitHub comments:
- GitHub PATs: `ghp_*`, `ghs_*`, `gho_*`, `github_pat_*`
- Bearer tokens
- API keys: `sk-*`, ZhipuAI keys

### Resource Constraints
- 2 CPUs / 4GB RAM per worker container
- Prevents rogue agent from causing DoS

---

## Self-Bootstrapping Lifecycle

```
Stage 0: Seeding
└─► Developer manually clones template repository

Stage 1: Manual Launch
└─► Developer runs devcontainer-opencode.sh up

Stage 2: Project Setup
└─► Agent indexes repo, configures environment

Stage 3: Handover
└─► Developer starts sentinel.py service
└─► AI manages all further development autonomously
```

---

## Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # Core definition for uv dependencies
├── uv.lock                      # Deterministic lockfile
├── src/
│   ├── os_apow/
│   │   ├── __init__.py
│   │   ├── main.py              # Application entry point
│   │   ├── api/                 # FastAPI routes
│   │   ├── models/              # Pydantic data schemas
│   │   │   └── work_item.py     # Unified WorkItem, TaskType, Status
│   │   └── services/            # Business logic
│   └── queue/
│       └── github_queue.py      # ITaskQueue + GitHubQueue
├── tests/
│   └── test_main.py
├── scripts/                     # Shell Bridge layer
│   ├── devcontainer-opencode.sh # Core orchestrator
│   ├── gh-auth.ps1              # GitHub auth sync
│   └── update-remote-indices.ps1
├── local_ai_instruction_modules/
│   ├── create-app-plan.md
│   ├── perform-task.md
│   └── analyze-bug.md
├── docs/                        # Architecture and user documentation
├── plan_docs/                   # Seeded plan documents
├── Dockerfile
├── docker-compose.yml
├── AGENTS.md                    # AI agent instructions
└── README.md
```

---

## References

- [OS-APOW Architecture Guide v3.2](./OS-APOW%20Architecture%20Guide%20v3.2.md)
- [OS-APOW Development Plan v4.2](./OS-APOW%20Development%20Plan%20v4.2.md)
- [OS-APOW Implementation Specification v1.2](./OS-APOW%20Implementation%20Specification%20v1.2.md)
- [OS-APOW Plan Review](./OS-APOW%20Plan%20Review.md)
- [OS-APOW Simplification Report v1](./OS-APOW%20Simplification%20Report%20v1.md)
