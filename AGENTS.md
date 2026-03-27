# AGENTS.md

> Instructions for AI coding agents working on OS-APOW.

---

## Project Overview

**OS-APOW** (OpenSource AI-Powered Orchestration Workflow) is a headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders.

**Core Principle:** Zero-Touch Construction — a user opens a single "Specification Issue" and receives a functional, test-passed branch and PR without manual intervention.

### The Four Pillars

| Pillar | Component | Technology | Purpose |
|--------|-----------|------------|---------|
| **The Ear** | Notifier | FastAPI, Uvicorn | Webhook receiver for GitHub events |
| **The State** | Queue | GitHub Issues, Labels | Distributed state management |
| **The Brain** | Sentinel | Python Async, HTTPX | Persistent orchestrator |
| **The Hands** | Worker | Opencode CLI, Docker | Isolated agent execution |

---

## Setup Commands

### Prerequisites

- Python 3.12+
- UV package manager (0.10.9+)
- Docker (for containerized execution)

### Installation

```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --all-extras
```

### Running Services

```bash
# Run the Notifier (FastAPI webhook receiver)
uv run os-apow-notifier
# Or directly:
uv run uvicorn os_apow.services.notifier:app --reload

# Run the Sentinel (orchestrator)
uv run os-apow-sentinel
# Or directly:
uv run python -m os_apow.services.sentinel
```

### Building

```bash
# Build the package
uv build

# Build Docker image
docker build -t os-apow .
```

### Environment Variables

Create a `.env` file or export these variables:

```bash
# Required
export GITHUB_TOKEN="your-github-token"
export GITHUB_ORG="your-org"
export GITHUB_REPO="your-repo"
export WEBHOOK_SECRET="your-webhook-secret"  # For Notifier only

# Optional
export SENTINEL_BOT_LOGIN="bot-account-login"  # For distributed locking
```

---

## Project Structure

```
workflow-orchestration-queue-quebec16/
├── src/os_apow/                    # Main Python package
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # Application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── work_item.py            # WorkItem, TaskType, WorkItemStatus, scrub_secrets()
│   ├── queue/
│   │   ├── __init__.py
│   │   └── github_queue.py         # ITaskQueue interface, GitHubQueue implementation
│   └── services/
│       ├── __init__.py
│       ├── notifier.py             # FastAPI webhook receiver (The Ear)
│       └── sentinel.py             # Async orchestrator (The Brain)
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_notifier.py            # Notifier tests
│   └── test_sentinel.py            # Sentinel tests
│
├── scripts/                        # Shell bridge scripts
│   ├── devcontainer-opencode.sh    # Core orchestrator shell bridge
│   ├── gh-auth.ps1                 # GitHub authentication
│   └── validate.ps1                # Validation suite
│
├── plan_docs/                      # Architecture and planning documents
├── local_ai_instruction_modules/   # AI instruction modules
├── pyproject.toml                  # Project configuration (UV, pytest, ruff, mypy)
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Multi-service orchestration
└── README.md                       # Project overview
```

### Key Files

| File | Purpose |
|------|---------|
| `src/os_apow/models/work_item.py` | Unified data model (WorkItem, TaskType, WorkItemStatus, scrub_secrets) |
| `src/os_apow/queue/github_queue.py` | GitHub-backed work queue implementation |
| `src/os_apow/services/sentinel.py` | Sentinel orchestrator service |
| `src/os_apow/services/notifier.py` | FastAPI webhook receiver |
| `pyproject.toml` | UV package configuration, dependencies, tool settings |

---

## Code Style

### Python Standards

- **Python Version:** 3.12+
- **Type Hints:** Required for all function signatures
- **Style Guide:** Follow PEP 8, enforced by Ruff
- **Line Length:** 100 characters max
- **Imports:** Use `from __future__ import annotations` for forward references

### Data Validation

- Use **Pydantic v2** models for all data structures
- All models inherit from `BaseModel`
- Use `Enum` classes for fixed vocabularies (e.g., `TaskType`, `WorkItemStatus`)

### Async Patterns

- Use `async`/`await` for all I/O operations
- Use `httpx` for async HTTP requests
- Use `asyncio.create_subprocess_exec` for subprocess calls

### Import Paths

- Import from `os_apow.*` (not `src.*`)
- Example: `from os_apow.models.work_item import WorkItem`

### Example Code Style

```python
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class TaskType(str, Enum):
    """The kind of work the agent should perform."""
    PLAN = "PLAN"
    IMPLEMENT = "IMPLEMENT"


class WorkItem(BaseModel):
    """Unified work item used across all OS-APOW components."""
    id: str
    issue_number: int
    task_type: TaskType
```

---

## Testing Instructions

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=os_apow

# Run specific test file
uv run pytest tests/test_notifier.py

# Run specific test
uv run pytest tests/test_sentinel.py::test_function_name
```

### Test Location

- All tests are in the `tests/` directory
- Test files follow pattern `test_*.py`
- Use `pytest-asyncio` for async tests (mode: auto)

### Code Quality

```bash
# Linting (Ruff)
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Type checking (MyPy)
uv run mypy src/

# Format code
uv run ruff format src/ tests/
```

### Validation Suite

```bash
# Run full validation (lint, scan, test)
pwsh -NoProfile -File ./scripts/validate.ps1 -All

# Individual checks
pwsh -NoProfile -File ./scripts/validate.ps1 -Lint
pwsh -NoProfile -File ./scripts/validate.ps1 -Scan
pwsh -NoProfile -File ./scripts/validate.ps1 -Test
```

---

## Architecture Notes

### State Machine

Tasks transition through these states via GitHub labels:

```
┌───────────┐     Claim      ┌──────────────┐
│  QUEUED   │ ──────────────►│ IN_PROGRESS  │
│agent:queued│               │agent:in-     │
└───────────┘                │  progress    │
      ▲                      └──────┬───────┘
      │                             │
      │ Re-queue                    │ Complete
      │ (Stale)                     │
      │                      ┌──────▼───────┐
┌─────┴──────┐              │   SUCCESS    │
│RECONCILING │              │agent:success │
│agent:      │              └──────────────┘
│reconciling │
└────────────┘
```

### Label Taxonomy

| Label | Status | Description |
|-------|--------|-------------|
| `agent:queued` | QUEUED | Task awaiting pickup |
| `agent:in-progress` | IN_PROGRESS | Task actively being processed |
| `agent:reconciling` | RECONCILING | Stale task being recovered |
| `agent:success` | SUCCESS | Terminal success state |
| `agent:error` | ERROR | Logic/implementation failure |
| `agent:infra-failure` | INFRA_FAILURE | Infrastructure failure |
| `agent:stalled-budget` | STALLED_BUDGET | Budget exceeded (future) |

### Configuration Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `POLL_INTERVAL` | 60s | Sentinel polling interval |
| `MAX_BACKOFF` | 960s | Maximum exponential backoff |
| `HEARTBEAT_INTERVAL` | 300s | Heartbeat comment frequency |
| `SUBPROCESS_TIMEOUT` | 5700s | Outer sentinel timeout |

### Credential Scrubbing

All worker output is passed through `scrub_secrets()` before posting to GitHub:

```python
from os_apow.models.work_item import scrub_secrets

# Removes: ghp_*, ghs_*, gho_*, github_pat_*, Bearer tokens, sk-*, ZhipuAI keys
safe_text = scrub_secrets(log_output)
```

---

## PR and Commit Guidelines

### Branch Naming

- `feature/*` - New features
- `fix/*` - Bug fixes
- `refactor/*` - Code refactoring
- `docs/*` - Documentation updates

### Commit Message Format

```
type(scope): brief description

- Detailed change 1
- Detailed change 2

Refs: #issue-number
```

### Required Checks Before Committing

1. **Run validation:**
   ```bash
   pwsh -NoProfile -File ./scripts/validate.ps1 -All
   ```

2. **Fix all failures** — do not skip or suppress errors

3. **Re-run until clean**

4. **Then commit and push**

### Post-Push Monitoring

After pushing, monitor CI:

```bash
gh run list --limit 5
gh run watch <run-id>
gh run view <run-id> --log-failed
```

If CI fails, **stop feature work**, triage, fix, re-verify, push. Do not mark work complete while CI is red.

---

## Common Pitfalls

### GitHub API Rate Limiting

- Sentinel implements jittered exponential backoff (max 960s)
- Use GitHub App Installation Tokens for 5,000 req/hr
- Monitor for 403/429 responses

### Credential Scrubbing

- **Always** use `scrub_secrets()` before posting to GitHub
- Never log raw tokens, even in development
- Test fixtures must use synthetic values (e.g., `FAKE-KEY-FOR-TESTING-00000000`)
- Never use prefixes matching real formats (`sk-`, `ghp_`, `ghs_`, `AKIA`)

### Environment Variable Validation

- Notifier fails fast if `WEBHOOK_SECRET` or `GITHUB_TOKEN` are missing/placeholder
- Sentinel requires `GITHUB_TOKEN`, `GITHUB_ORG`, `GITHUB_REPO`
- Set `SENTINEL_BOT_LOGIN` for distributed locking safety

### Import Paths

- Use `os_apow.*` imports, not `src.*`
- The `pythonpath = ["src"]` is set in `pyproject.toml` for pytest

### Async Context

- All I/O operations must be async
- Use `asyncio.create_subprocess_exec`, not `subprocess.run`
- HTTPX client must be properly closed

---

## Entry Points

| Command | Service | Description |
|---------|---------|-------------|
| `os-apow-sentinel` | Sentinel | Run the orchestrator service |
| `os-apow-notifier` | Notifier | Run the webhook receiver |

Defined in `pyproject.toml`:

```toml
[project.scripts]
os-apow-sentinel = "os_apow.services.sentinel:main"
os-apow-notifier = "os_apow.services.notifier:main"
```

---

## Related Documentation

- [README.md](README.md) - Project overview
- [.ai-repository-summary.md](.ai-repository-summary.md) - AI-friendly repository summary
- [plan_docs/architecture.md](plan_docs/architecture.md) - Architecture details
- [plan_docs/tech-stack.md](plan_docs/tech-stack.md) - Technology stack

---

## Notes for AI Agents

- **UV is the package manager** — use `uv` commands, not `pip` or `poetry`
- **Import paths use `os_apow.*`** — not `src.*`
- **All GitHub Actions must be pinned to full SHA** — no tag or branch references
- **Healthcheck uses Python stdlib** — not curl
- **Shell bridge scripts are in `./scripts/`**
- **Validation is mandatory** before commit/push
