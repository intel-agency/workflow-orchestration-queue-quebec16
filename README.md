# OS-APOW

**OpenSource AI-Powered Orchestration Workflow**

A headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders.

## Overview

OS-APOW represents a paradigm shift from **Interactive AI Coding** to **Headless Agentic Orchestration**. The system transforms standard project management artifacts—specifically GitHub Issues—into "Execution Orders" that are autonomously fulfilled by specialized AI agents.

**Core Principle:** Zero-Touch Construction — a user opens a single "Specification Issue" and receives a functional, test-passed branch and PR without manual intervention.

## Architecture

The system is built on four pillars:

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
│         │           ┌──────────────┐            │                      │
│         └──────────►│  THE HANDS   │◄───────────┘                      │
│                     │  (Worker)    │                                   │
│                     │              │                                   │
│                     │  Opencode    │                                   │
│                     │  DevContainer│                                   │
│                     └──────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **The Ear (Notifier)** | FastAPI, Uvicorn | Webhook receiver for GitHub events |
| **The State (Queue)** | GitHub Issues, Labels | Distributed state management |
| **The Brain (Sentinel)** | Python Async, HTTPX | Persistent orchestrator |
| **The Hands (Worker)** | Opencode CLI, Docker | Isolated agent execution |

## Quick Start

### Prerequisites

- Python 3.12+
- Docker (for containerized execution)
- UV package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/intel-agency/workflow-orchestration-queue-quebec16.git
cd workflow-orchestration-queue-quebec16

# Install dependencies with UV
uv sync

# Set environment variables
export GITHUB_TOKEN="your-token-here"
export WEBHOOK_SECRET="your-webhook-secret"
export GITHUB_ORG="your-org"
export GITHUB_REPO="your-repo"
```

### Running the Notifier

```bash
# Development mode
uv run uvicorn os_apow.services.notifier:app --reload

# Or using the CLI entry point
uv run os-apow-notifier
```

### Running the Sentinel

```bash
# Using the CLI entry point
uv run os-apow-sentinel

# Or directly
uv run python -m os_apow.services.sentinel
```

### Docker Deployment

```bash
# Build the image
docker build -t os-apow .

# Run the notifier
docker run -p 8000:8000 \
  -e GITHUB_TOKEN="your-token" \
  -e WEBHOOK_SECRET="your-secret" \
  os-apow

# Using docker-compose
docker-compose up notifier
docker-compose --profile sentinel up
```

## Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub API authentication token |
| `GITHUB_ORG` | Target GitHub organization |
| `GITHUB_REPO` | Target repository name |
| `WEBHOOK_SECRET` | GitHub webhook secret for signature verification |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTINEL_BOT_LOGIN` | (empty) | Bot account login for distributed locking |

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=os_apow
```

### Code Quality

```bash
# Linting
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## Project Structure

```
src/os_apow/
├── __init__.py          # Package initialization
├── main.py              # Application entry point
├── models/
│   ├── __init__.py
│   └── work_item.py     # Unified data models
├── queue/
│   ├── __init__.py
│   └── github_queue.py  # GitHub-backed work queue
└── services/
    ├── __init__.py
    ├── sentinel.py      # Sentinel orchestrator
    └── notifier.py      # FastAPI webhook receiver

tests/
├── __init__.py
├── test_sentinel.py     # Sentinel tests
└── test_notifier.py     # Notifier tests
```

## Documentation

- [Architecture Guide](docs/architecture/) - System architecture details
- [Development Guides](docs/guides/) - Development and deployment guides
- [AI Repository Summary](.ai-repository-summary.md) - AI agent reference

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## Repository Summary

See [.ai-repository-summary.md](.ai-repository-summary.md) for a comprehensive AI-friendly repository overview.
