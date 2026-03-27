"""
Tests for OS-APOW Notifier Service
"""

from __future__ import annotations

import hashlib
import hmac
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient


class TestNotifierHealthEndpoint:
    """Tests for the Notifier health check endpoint."""

    def test_health_check_returns_online(self) -> None:
        """Test that health check returns online status."""
        # We need to mock the environment validation
        import os

        # Set required environment variables for import
        os.environ["WEBHOOK_SECRET"] = "test-secret-for-testing-00000000"
        os.environ["GITHUB_TOKEN"] = "test-token-for-testing-00000000"

        # Import after setting env vars
        from os_apow.services.notifier import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["system"] == "OS-APOW Notifier"


class TestNotifierSignatureVerification:
    """Tests for GitHub webhook signature verification."""

    def test_missing_signature_returns_401(self) -> None:
        """Test that missing signature header returns 401."""
        import os

        os.environ["WEBHOOK_SECRET"] = "test-secret-for-testing-00000000"
        os.environ["GITHUB_TOKEN"] = "test-token-for-testing-00000000"

        from os_apow.services.notifier import app

        client = TestClient(app)
        response = client.post(
            "/webhooks/github",
            json={"test": "data"},
        )

        assert response.status_code == 401

    def test_invalid_signature_returns_401(self) -> None:
        """Test that invalid signature returns 401."""
        import os

        os.environ["WEBHOOK_SECRET"] = "test-secret-for-testing-00000000"
        os.environ["GITHUB_TOKEN"] = "test-token-for-testing-00000000"

        from os_apow.services.notifier import app

        client = TestClient(app)
        response = client.post(
            "/webhooks/github",
            json={"test": "data"},
            headers={"X-Hub-Signature-256": "sha256=invalid"},
        )

        assert response.status_code == 401

    def test_valid_signature_accepted(self) -> None:
        """Test that valid signature is accepted."""
        import os

        secret = "test-secret-for-testing-00000000"
        os.environ["WEBHOOK_SECRET"] = secret
        os.environ["GITHUB_TOKEN"] = "test-token-for-testing-00000000"

        from os_apow.services.notifier import app

        client = TestClient(app)

        body = b'{"test": "data"}'
        signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        response = client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-Hub-Signature-256": signature,
                "X-GitHub-Event": "push",
            },
        )

        # Should be accepted (though may return ignored status)
        assert response.status_code == 200


class TestNotifierWebhookHandling:
    """Tests for webhook event handling."""

    def test_ignored_event_returns_ignored_status(self) -> None:
        """Test that non-actionable events return ignored status."""
        import os

        secret = "test-secret-for-testing-00000000"
        os.environ["WEBHOOK_SECRET"] = secret
        os.environ["GITHUB_TOKEN"] = "test-token-for-testing-00000000"

        from os_apow.services.notifier import app

        client = TestClient(app)

        body = b'{"action": "closed"}'
        signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        response = client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-Hub-Signature-256": signature,
                "X-GitHub-Event": "issues",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
