# OS-APOW Technology Stack

**Document Version:** 1.0  
**Last Updated:** 2026-03-27  
**Status:** Planning

---

## Overview

This document defines the complete technology stack for OS-APOW (OpenSource AI-Powered Orchestration Workflow), a headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders.

---

## Primary Languages

| Language | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.12+ | Primary language for Orchestrator, API Webhook receiver, and all system logic |
| **PowerShell Core** | 7.x+ | Shell Bridge Scripts, Auth synchronization, cross-platform CLI |
| **Bash** | 5.x | Shell Bridge Scripts, container orchestration utilities |

---

## Core Frameworks & Libraries

### Web Framework (The Ear - Notifier)

| Component | Package | Version | Purpose |
|-----------|---------|---------|---------|
| **FastAPI** | `fastapi` | Latest | High-performance async web framework for webhook receiver |
| **Uvicorn** | `uvicorn[standard]` | Latest | ASGI server for production deployment |
| **Pydantic** | `pydantic` | v2.x | Strict data validation and settings management |

### HTTP Client

| Component | Package | Version | Purpose |
|-----------|---------|---------|---------|
| **HTTPX** | `httpx` | Latest | Async HTTP client for GitHub API calls |

### Package Management

| Component | Package | Version | Purpose |
|-----------|---------|---------|---------|
| **uv** | `uv` | 0.10.9+ | Rust-based Python package installer and dependency resolver |

---

## Agent Runtime

| Component | Version | Purpose |
|-----------|---------|---------|
| **opencode CLI** | 1.2.24+ | AI agent runtime for executing specialist agents |
| **ZhipuAI GLM** | glm-5 | Primary LLM model for agent reasoning |

### MCP Servers

| Server | Purpose |
|--------|---------|
| `@modelcontextprotocol/server-sequential-thinking` | Structured reasoning and problem decomposition |
| `@modelcontextprotocol/server-memory` | Knowledge graph persistence for context |

---

## Containerization & Infrastructure

| Component | Version | Purpose |
|-----------|---------|---------|
| **Docker** | 24.x+ | Container runtime for worker isolation |
| **Docker Compose** | v2.x | Multi-container orchestration |
| **DevContainers** | Latest | Reproducible development environment |

### DevContainer Features

| Feature | Purpose |
|---------|---------|
| `node` | Node.js runtime for MCP servers |
| `python` | Python language support |
| `gh-cli` | GitHub CLI for API interactions |

---

## Development Tools

### Runtimes (Pre-installed in DevContainer)

| Tool | Version | Purpose |
|------|---------|---------|
| **.NET SDK** | 10.0.102 | Build/test .NET projects (if needed for templates) |
| **Node.js** | 24.14.0 LTS | JavaScript runtime for MCP servers |
| **Bun** | 1.3.10 | Fast JS/TS runtime and package manager |
| **uv** | 0.10.9 | Python package manager |

### CLI Tools

| Tool | Purpose |
|------|---------|
| **gh** | GitHub CLI for issues, PRs, repos, releases, actions |
| **git** | Version control |
| **opencode** | AI agent runtime |

---

## CI/CD Platform

| Component | Purpose |
|-----------|---------|
| **GitHub Actions** | Build, test, scan, publish workflows |
| **GHCR** | GitHub Container Registry for Docker images |

---

## Data & State Management

| Component | Purpose |
|-----------|---------|
| **GitHub Issues** | Distributed state management ("Markdown as a Database") |
| **GitHub Labels** | Task status indicators (`agent:queued`, `agent:in-progress`, etc.) |
| **GitHub Projects** | Kanban-style workflow visualization |
| **GitHub Milestones** | Phase-based progress tracking |

---

## Security Components

| Component | Purpose |
|-----------|---------|
| **HMAC SHA256** | Webhook signature verification |
| **GitHub App Installation Tokens** | API authentication (5,000 req/hr) |
| **Credential Scrubber** | Regex-based secret removal from logs |

---

## Shell Bridge Scripts

| Script | Purpose |
|--------|---------|
| `devcontainer-opencode.sh` | Core orchestrator invoking worker Docker context |
| `gh-auth.ps1` | GitHub App authentication synchronization |
| `common-auth.ps1` | Shared authentication utilities |
| `update-remote-indices.ps1` | Vector index maintenance |
| `import-labels.ps1` | Label synchronization from `.labels.json` |
| `create-milestones.ps1` | Milestone creation from plan docs |
| `query.ps1` | PR review thread management |

---

## Project Configuration

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python project metadata and dependencies |
| `uv.lock` | Deterministic lockfile for exact package versions |
| `.env` | Environment variables (GITHUB_TOKEN, GITHUB_ORG, SENTINEL_BOT_LOGIN) |

---

## Configuration Constants

### Sentinel Defaults (Hardcoded per Simplification Report S-3)

| Constant | Value | Description |
|----------|-------|-------------|
| `POLL_INTERVAL` | 60s | Base polling interval |
| `MAX_BACKOFF` | 960s (16 min) | Maximum exponential backoff |
| `HEARTBEAT_INTERVAL` | 300s (5 min) | Status comment frequency |
| `SUBPROCESS_TIMEOUT` | 5700s (95 min) | Outer sentinel timeout |
| `ENV_RESET_MODE` | `"stop"` | Environment teardown mode |

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub API authentication |
| `GITHUB_ORG` | Yes | Target organization |
| `SENTINEL_BOT_LOGIN` | Yes | Bot account login for distributed locking |

---

## Label Taxonomy

| Label | State | Description |
|-------|-------|-------------|
| `agent:queued` | QUEUED | Task awaiting pickup |
| `agent:in-progress` | IN_PROGRESS | Task actively being processed |
| `agent:reconciling` | RECONCILING | Stale task being recovered |
| `agent:success` | SUCCESS | Task completed successfully |
| `agent:error` | ERROR | Task failed (logic error) |
| `agent:infra-failure` | INFRA_FAILURE | Task failed (infrastructure) |
| `agent:stalled-budget` | STALLED_BUDGET | Budget exceeded (future) |

---

## Dependencies Summary

### Production Dependencies

```toml
[project]
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.0.0",
    "httpx>=0.27.0",
]
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]
```

---

## References

- [OS-APOW Implementation Specification v1.2](./OS-APOW%20Implementation%20Specification%20v1.2.md)
- [OS-APOW Architecture Guide v3.2](./OS-APOW%20Architecture%20Guide%20v3.2.md)
- [OS-APOW Simplification Report v1](./OS-APOW%20Simplification%20Report%20v1.md)
