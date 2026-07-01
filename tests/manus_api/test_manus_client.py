"""Tests for the manus-api skill's ManusClient helper.

No real network calls are made: requests.Session.request is patched in every
test so we can assert on exactly what the client sends (method, URL, headers,
JSON body / query params) and how it parses responses.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

SKILL_SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills", "manus-api", "scripts"
)
sys.path.insert(0, os.path.abspath(SKILL_SCRIPTS_DIR))

from manus_client import (  # noqa: E402
    API_KEY_HEADER,
    DEFAULT_BASE_URL,
    ManusAPIError,
    ManusClient,
)


def make_response(status_code=200, json_body=None, text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.text = text if text else (str(json_body) if json_body is not None else "")
    resp.content = b"x" if (json_body is not None or text) else b""
    resp.json.return_value = json_body if json_body is not None else {}
    return resp


@pytest.fixture
def client():
    return ManusClient(api_key="test-key-123")


# ---------------------------------------------------------------------------
# Construction / auth
# ---------------------------------------------------------------------------


def test_reads_api_key_from_env(monkeypatch):
    monkeypatch.setenv("MANUS_API_KEY", "env-key-456")
    c = ManusClient()
    assert c.api_key == "env-key-456"


def test_constructor_param_overrides_env(monkeypatch):
    monkeypatch.setenv("MANUS_API_KEY", "env-key-456")
    c = ManusClient(api_key="explicit-key")
    assert c.api_key == "explicit-key"


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("MANUS_API_KEY", raising=False)
    with pytest.raises(ValueError):
        ManusClient()


def test_default_base_url(client):
    assert client.base_url == DEFAULT_BASE_URL == "https://api.manus.ai"


# ---------------------------------------------------------------------------
# create_task
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_create_task_sends_correct_request(mock_request, client):
    mock_request.return_value = make_response(
        200,
        {
            "ok": True,
            "request_id": "req_1",
            "task_id": "task_abc123",
            "task_title": "My task",
            "task_url": "https://manus.im/app/task_abc123",
        },
    )

    result = client.create_task("hello world")

    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "POST"
    assert url == "https://api.manus.ai/v2/task.create"
    assert kwargs["headers"][API_KEY_HEADER] == "test-key-123"
    assert kwargs["headers"]["Content-Type"] == "application/json"
    assert kwargs["json"] == {"message": {"content": "hello world"}}
    assert result["task_id"] == "task_abc123"
    assert result["task_url"] == "https://manus.im/app/task_abc123"


@patch("requests.Session.request")
def test_create_task_passes_optional_fields(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True, "task_id": "t1"})

    client.create_task(
        "do research",
        project_id="proj_1",
        locale="en",
        interactive_mode=True,
        hide_in_task_list=True,
        share_visibility="team",
        agent_profile="manus-1.6-max",
        connectors=["conn_1"],
        enable_skills=["skill_1"],
        force_skills=["skill_2"],
        structured_output_schema={"type": "object"},
    )

    _, kwargs = mock_request.call_args
    body = kwargs["json"]
    assert body["project_id"] == "proj_1"
    assert body["locale"] == "en"
    assert body["interactive_mode"] is True
    assert body["hide_in_task_list"] is True
    assert body["share_visibility"] == "team"
    assert body["agent_profile"] == "manus-1.6-max"
    assert body["structured_output_schema"] == {"type": "object"}
    assert body["message"] == {
        "content": "do research",
        "connectors": ["conn_1"],
        "enable_skills": ["skill_1"],
        "force_skills": ["skill_2"],
    }


@patch("requests.Session.request")
def test_create_task_omits_none_fields(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True, "task_id": "t1"})

    client.create_task("hello")

    _, kwargs = mock_request.call_args
    body = kwargs["json"]
    # None-valued optional kwargs should not be sent at all.
    assert "project_id" not in body
    assert "agent_profile" not in body
    assert body["message"] == {"content": "hello"}


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_get_task_sends_correct_request(mock_request, client):
    mock_request.return_value = make_response(
        200, {"ok": True, "id": "task_abc123", "status": "running"}
    )

    result = client.get_task("task_abc123")

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "GET"
    assert url == "https://api.manus.ai/v2/task.detail"
    assert kwargs["params"] == {"task_id": "task_abc123"}
    assert kwargs["headers"][API_KEY_HEADER] == "test-key-123"
    assert result["status"] == "running"


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_list_tasks_default_params(mock_request, client):
    mock_request.return_value = make_response(
        200, {"ok": True, "data": [], "has_more": False}
    )

    result = client.list_tasks()

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "GET"
    assert url == "https://api.manus.ai/v2/task.list"
    # No filters given -> no keys should be sent.
    assert kwargs["params"] == {}
    assert result["has_more"] is False


@patch("requests.Session.request")
def test_list_tasks_with_filters(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True, "data": []})

    client.list_tasks(limit=50, cursor="cur_1", order="asc", scope="project", project_id="proj_1")

    _, kwargs = mock_request.call_args
    assert kwargs["params"] == {
        "limit": 50,
        "cursor": "cur_1",
        "order": "asc",
        "scope": "project",
        "project_id": "proj_1",
    }


# ---------------------------------------------------------------------------
# send_message
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_send_message_sends_correct_request(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True, "request_id": "req_2"})

    result = client.send_message("task_abc123", "continue please")

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "POST"
    assert url == "https://api.manus.ai/v2/task.sendMessage"
    assert kwargs["json"] == {
        "task_id": "task_abc123",
        "message": {"content": "continue please"},
    }
    assert result["ok"] is True


@patch("requests.Session.request")
def test_send_message_with_agent_profile_and_schema(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True})

    client.send_message(
        "task_abc123",
        "go",
        agent_profile="manus-1.6-lite",
        structured_output_schema={"type": "object"},
    )

    _, kwargs = mock_request.call_args
    body = kwargs["json"]
    assert body["agent_profile"] == "manus-1.6-lite"
    assert body["structured_output_schema"] == {"type": "object"}


# ---------------------------------------------------------------------------
# stop_task / delete_task / update_task / confirm_action
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_stop_task(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True})

    client.stop_task("task_abc123")

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "POST"
    assert url == "https://api.manus.ai/v2/task.stop"
    assert kwargs["json"] == {"task_id": "task_abc123"}


@patch("requests.Session.request")
def test_delete_task(mock_request, client):
    mock_request.return_value = make_response(
        200, {"ok": True, "id": "task_abc123", "deleted": True}
    )

    result = client.delete_task("task_abc123")

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "POST"
    assert url == "https://api.manus.ai/v2/task.delete"
    assert kwargs["json"] == {"task_id": "task_abc123"}
    assert result["deleted"] is True


@patch("requests.Session.request")
def test_update_task(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True})

    client.update_task("task_abc123", title="New title", share_visibility="public")

    _, kwargs = mock_request.call_args
    assert kwargs["json"] == {
        "task_id": "task_abc123",
        "title": "New title",
        "share_visibility": "public",
    }


@patch("requests.Session.request")
def test_confirm_action(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True})

    client.confirm_action("task_abc123", "evt_1", input={"approved": True})

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "POST"
    assert url == "https://api.manus.ai/v2/task.confirmAction"
    assert kwargs["json"] == {
        "task_id": "task_abc123",
        "event_id": "evt_1",
        "input": {"approved": True},
    }


# ---------------------------------------------------------------------------
# webhooks
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_create_webhook(mock_request, client):
    mock_request.return_value = make_response(
        200,
        {
            "ok": True,
            "webhook": {"id": "wh_1", "url": "https://example.com/hook", "status": "active"},
        },
    )

    result = client.create_webhook("https://example.com/hook")

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "POST"
    assert url == "https://api.manus.ai/v2/webhook.create"
    assert kwargs["json"] == {"url": "https://example.com/hook"}
    assert result["webhook"]["id"] == "wh_1"


@patch("requests.Session.request")
def test_create_webhook_with_events(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True, "webhook": {"id": "wh_2"}})

    client.create_webhook("https://example.com/hook", events=["task_stopped"])

    _, kwargs = mock_request.call_args
    assert kwargs["json"] == {
        "url": "https://example.com/hook",
        "events": ["task_stopped"],
    }


@patch("requests.Session.request")
def test_list_webhooks(mock_request, client):
    mock_request.return_value = make_response(
        200, {"ok": True, "data": [{"id": "wh_1"}, {"id": "wh_2"}]}
    )

    result = client.list_webhooks()

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "GET"
    assert url == "https://api.manus.ai/v2/webhook.list"
    assert len(result["data"]) == 2


@patch("requests.Session.request")
def test_delete_webhook(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True})

    client.delete_webhook("wh_1")

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "POST"
    assert url == "https://api.manus.ai/v2/webhook.delete"
    assert kwargs["json"] == {"webhook_id": "wh_1"}


@patch("requests.Session.request")
def test_get_webhook_public_key(mock_request, client):
    mock_request.return_value = make_response(
        200, {"ok": True, "public_key": "-----BEGIN PUBLIC KEY-----...", "algorithm": "RSA-SHA256"}
    )

    result = client.get_webhook_public_key()

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "GET"
    assert url == "https://api.manus.ai/v2/webhook.publicKey"
    assert result["algorithm"] == "RSA-SHA256"


# ---------------------------------------------------------------------------
# list_messages
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_list_messages(mock_request, client):
    mock_request.return_value = make_response(200, {"ok": True, "data": []})

    client.list_messages("task_abc123", order="desc", limit=10)

    args, kwargs = mock_request.call_args
    method, url = args
    assert method == "GET"
    assert url == "https://api.manus.ai/v2/task.listMessages"
    assert kwargs["params"] == {"task_id": "task_abc123", "order": "desc", "limit": 10}


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_raises_on_4xx_with_body_in_message(mock_request, client):
    error_body = '{"ok": false, "error": {"code": "not_found", "message": "Task not found"}}'
    mock_request.return_value = make_response(404, text=error_body)
    mock_request.return_value.ok = False
    mock_request.return_value.content = error_body.encode()

    with pytest.raises(ManusAPIError) as excinfo:
        client.get_task("nonexistent")

    err = excinfo.value
    assert err.status_code == 404
    assert "not_found" in str(err)
    assert "Task not found" in str(err)
    assert "task.detail" in str(err)


@patch("requests.Session.request")
def test_raises_on_401_permission_denied(mock_request, client):
    error_body = '{"ok": false, "error": {"code": "permission_denied", "message": "Invalid or missing API key"}}'
    resp = make_response(401, text=error_body)
    resp.ok = False
    resp.content = error_body.encode()
    mock_request.return_value = resp

    with pytest.raises(ManusAPIError) as excinfo:
        client.create_task("hello")

    assert excinfo.value.status_code == 401
    assert "permission_denied" in str(excinfo.value)


@patch("requests.Session.request")
def test_raises_on_429_rate_limited(mock_request, client):
    error_body = '{"ok": false, "error": {"code": "rate_limited", "message": "Rate limit exceeded"}}'
    resp = make_response(429, text=error_body)
    resp.ok = False
    resp.content = error_body.encode()
    mock_request.return_value = resp

    with pytest.raises(ManusAPIError) as excinfo:
        client.list_tasks()

    assert excinfo.value.status_code == 429
    assert "rate_limited" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


@patch("requests.Session.request")
def test_empty_response_body_returns_empty_dict(mock_request, client):
    resp = make_response(200, text="")
    resp.content = b""
    mock_request.return_value = resp

    result = client.stop_task("task_abc123")

    assert result == {}


@patch("requests.Session.request")
def test_json_response_parsed_correctly(mock_request, client):
    payload = {"ok": True, "request_id": "req_9", "data": [{"id": "task_1"}, {"id": "task_2"}]}
    mock_request.return_value = make_response(200, payload)

    result = client.list_tasks()

    assert result == payload
    assert result["data"][0]["id"] == "task_1"
