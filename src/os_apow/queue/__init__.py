"""
Queue module for OS-APOW.

Provides the ITaskQueue interface and GitHub-backed implementation
for distributed work queue management.
"""

from os_apow.queue.github_queue import GitHubQueue, ITaskQueue

__all__ = ["ITaskQueue", "GitHubQueue"]
