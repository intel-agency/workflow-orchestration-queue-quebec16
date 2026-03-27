"""
Tests for OS-APOW Sentinel Service
"""

from __future__ import annotations

import pytest

from os_apow.models.work_item import TaskType, WorkItem, WorkItemStatus


class TestWorkItem:
    """Tests for the WorkItem model."""

    def test_work_item_creation(self) -> None:
        """Test creating a WorkItem instance."""
        item = WorkItem(
            id="12345",
            issue_number=42,
            source_url="https://github.com/org/repo/issues/42",
            context_body="Test issue body",
            target_repo_slug="org/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="node_123",
        )

        assert item.id == "12345"
        assert item.issue_number == 42
        assert item.task_type == TaskType.IMPLEMENT
        assert item.status == WorkItemStatus.QUEUED

    def test_task_type_enum_values(self) -> None:
        """Test TaskType enum has expected values."""
        assert TaskType.PLAN.value == "PLAN"
        assert TaskType.IMPLEMENT.value == "IMPLEMENT"
        assert TaskType.BUGFIX.value == "BUGFIX"

    def test_work_item_status_enum_values(self) -> None:
        """Test WorkItemStatus enum maps to GitHub labels."""
        assert WorkItemStatus.QUEUED.value == "agent:queued"
        assert WorkItemStatus.IN_PROGRESS.value == "agent:in-progress"
        assert WorkItemStatus.SUCCESS.value == "agent:success"
        assert WorkItemStatus.ERROR.value == "agent:error"
        assert WorkItemStatus.INFRA_FAILURE.value == "agent:infra-failure"


class TestScrubSecrets:
    """Tests for the scrub_secrets utility."""

    def test_scrub_github_pat(self) -> None:
        """Test scrubbing GitHub PAT patterns."""
        from os_apow.models.work_item import scrub_secrets

        text = "Token: ghp_1234567890abcdefghijklmnopqrstuvwx"
        result = scrub_secrets(text)
        assert "ghp_" not in result
        assert "***REDACTED***" in result

    def test_scrub_bearer_token(self) -> None:
        """Test scrubbing Bearer token patterns."""
        from os_apow.models.work_item import scrub_secrets

        text = "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456"
        result = scrub_secrets(text)
        assert "Bearer" not in result or "***REDACTED***" in result

    def test_scrub_preserves_normal_text(self) -> None:
        """Test that normal text is preserved."""
        from os_apow.models.work_item import scrub_secrets

        text = "This is a normal log message without secrets"
        result = scrub_secrets(text)
        assert result == text


class TestSentinelConfiguration:
    """Tests for Sentinel configuration constants."""

    def test_poll_interval(self) -> None:
        """Test that poll interval is configured correctly."""
        from os_apow.services.sentinel import POLL_INTERVAL

        assert POLL_INTERVAL == 60

    def test_max_backoff(self) -> None:
        """Test that max backoff is configured correctly."""
        from os_apow.services.sentinel import MAX_BACKOFF

        assert MAX_BACKOFF == 960  # 16 minutes

    def test_heartbeat_interval(self) -> None:
        """Test that heartbeat interval is configured correctly."""
        from os_apow.services.sentinel import HEARTBEAT_INTERVAL

        assert HEARTBEAT_INTERVAL == 300  # 5 minutes

    def test_subprocess_timeout(self) -> None:
        """Test that subprocess timeout is higher than inner watchdog."""
        from os_apow.services.sentinel import SUBPROCESS_TIMEOUT

        # Must be higher than HARD_CEILING_SECS (5400) in run_opencode_prompt.sh
        assert SUBPROCESS_TIMEOUT == 5700  # 95 min
        assert SUBPROCESS_TIMEOUT > 5400
