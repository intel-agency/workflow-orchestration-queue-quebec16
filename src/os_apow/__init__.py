"""
OS-APOW: OpenSource AI-Powered Orchestration Workflow

A headless agentic orchestration platform that transforms GitHub Issues
into autonomous execution orders.

Core Components:
- The Ear (Notifier): FastAPI webhook receiver for GitHub events
- The State (Queue): GitHub-backed distributed state management
- The Brain (Sentinel): Persistent orchestrator managing worker lifecycle
- The Hands (Worker): Opencode CLI execution in isolated containers
"""

__version__ = "0.1.0"
__author__ = "OS-APOW Team"
