# OS-APOW Architecture Documentation

This directory contains architecture documentation for the OS-APOW system.

## Documents

- [System Architecture](../../plan_docs/architecture.md) - Four-pillar architecture overview
- [Technology Stack](../../plan_docs/tech-stack.md) - Complete technology stack
- [Development Plan](../../plan_docs/OS-APOW%20Development%20Plan%20v4.2.md) - Phased development roadmap

## Key Architectural Decisions

### ADR 07: Standardized Shell-Bridge Execution
The Orchestrator interacts with the agentic environment exclusively via `devcontainer-opencode.sh`.

### ADR 08: Polling-First Resiliency Model
Sentinel uses polling as primary discovery; webhooks are an optimization.

### ADR 09: Provider-Agnostic Interface Layer
All queue interactions are abstracted behind `ITaskQueue` interface.

## Component Overview

| Component | Technology | Purpose |
|-----------|------------|---------|
| The Ear | FastAPI | Webhook receiver |
| The State | GitHub Issues | Distributed state |
| The Brain | Python Async | Orchestrator |
| The Hands | Opencode CLI | Agent execution |
