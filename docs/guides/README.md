# OS-APOW Development Guides

This directory contains development and deployment guides for the OS-APOW system.

## Quick Start Guide

### Prerequisites
- Python 3.12+
- UV package manager
- Docker (for containerized execution)

### Installation

```bash
# Install dependencies
uv sync

# Set environment variables
export GITHUB_TOKEN="your-token"
export WEBHOOK_SECRET="your-secret"
export GITHUB_ORG="your-org"
export GITHUB_REPO="your-repo"
```

### Running Services

```bash
# Notifier (webhook receiver)
uv run os-apow-notifier

# Sentinel (orchestrator)
uv run os-apow-sentinel
```

## Development Workflow

1. Create a feature branch
2. Make changes
3. Run tests: `uv run pytest`
4. Run linter: `uv run ruff check src/ tests/`
5. Submit PR

## Docker Deployment

```bash
# Build
docker build -t os-apow .

# Run notifier
docker run -p 8000:8000 \
  -e GITHUB_TOKEN="token" \
  -e WEBHOOK_SECRET="secret" \
  os-apow

# Using docker-compose
docker-compose up notifier
```

## Configuration

See [AI Repository Summary](../../.ai-repository-summary.md) for complete configuration reference.
