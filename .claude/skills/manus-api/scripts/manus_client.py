#!/usr/bin/env python3
"""
ManusClient - minimal Python wrapper around the Manus v2 REST API.

Ground truth for base URL, auth header, and endpoint paths is
references/openapi_v2.json (servers[0].url == "https://api.manus.ai",
securitySchemes.ApiKeyAuth == {"type": "apiKey", "in": "header",
"name": "x-manus-api-key"}).

Usage:
    from manus_client import ManusClient

    client = ManusClient()  # reads MANUS_API_KEY from env
    task = client.create_task("Research the top 5 CRM tools for startups")
    print(task["task_id"], task["task_url"])

    result = client.get_task(task["task_id"])
    print(result["status"])
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

DEFAULT_BASE_URL = "https://api.manus.ai"
API_KEY_HEADER = "x-manus-api-key"
API_KEY_ENV_VAR = "MANUS_API_KEY"


class ManusAPIError(Exception):
    """Raised when the Manus API returns a non-2xx response.

    The exception message includes the HTTP status code and the raw
    response body so callers can see the API's error code/message
    (e.g. {"ok": false, "error": {"code": "...", "message": "..."}})
    without needing to catch a lower-level requests exception.
    """

    def __init__(self, status_code: int, method: str, url: str, body: str):
        self.status_code = status_code
        self.method = method
        self.url = url
        self.body = body
        super().__init__(
            f"Manus API request failed: {method} {url} -> HTTP {status_code}: {body}"
        )


class ManusClient:
    """Thin wrapper around the Manus v2 REST API.

    Every endpoint below corresponds 1:1 to a path in
    references/openapi_v2.json under /v2/*.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        session: Optional[requests.Session] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.environ.get(API_KEY_ENV_VAR)
        if not self.api_key:
            raise ValueError(
                f"No Manus API key provided. Pass api_key= or set the "
                f"{API_KEY_ENV_VAR} environment variable."
            )
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout

    # -- internals ---------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            API_KEY_HEADER: self.api_key,
        }

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        # Drop None values so optional filters/kwargs don't get sent as "None".
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}
        if json_body is not None:
            json_body = {k: v for k, v in json_body.items() if v is not None}

        response = self.session.request(
            method,
            url,
            headers=self._headers(),
            params=params,
            json=json_body,
            timeout=self.timeout,
        )

        if not response.ok:
            raise ManusAPIError(response.status_code, method, url, response.text)

        if not response.content:
            return {}
        return response.json()

    # -- tasks ---------------------------------------------------------

    def create_task(
        self,
        prompt: str,
        *,
        project_id: Optional[str] = None,
        locale: Optional[str] = None,
        interactive_mode: Optional[bool] = None,
        hide_in_task_list: Optional[bool] = None,
        share_visibility: Optional[str] = None,
        agent_profile: Optional[str] = None,
        connectors: Optional[List[str]] = None,
        enable_skills: Optional[List[str]] = None,
        force_skills: Optional[List[str]] = None,
        structured_output_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST /v2/task.create - start a new autonomous agent task.

        `prompt` becomes `message.content`. Returns a dict with
        task_id, task_title, task_url (see openapi_v2.json response
        schema for CreateTask).
        """
        message: Dict[str, Any] = {"content": prompt}
        if connectors is not None:
            message["connectors"] = connectors
        if enable_skills is not None:
            message["enable_skills"] = enable_skills
        if force_skills is not None:
            message["force_skills"] = force_skills

        body = {
            "message": message,
            "project_id": project_id,
            "locale": locale,
            "interactive_mode": interactive_mode,
            "hide_in_task_list": hide_in_task_list,
            "share_visibility": share_visibility,
            "agent_profile": agent_profile,
            "structured_output_schema": structured_output_schema,
        }
        return self._request("POST", "/v2/task.create", json_body=body)

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """GET /v2/task.detail - fetch a task's status and metadata."""
        return self._request("GET", "/v2/task.detail", params={"task_id": task_id})

    def list_tasks(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        order: Optional[str] = None,
        scope: Optional[str] = None,
        agent_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """GET /v2/task.list - list tasks with cursor pagination."""
        params = {
            "limit": limit,
            "cursor": cursor,
            "order": order,
            "scope": scope,
            "agent_id": agent_id,
            "project_id": project_id,
        }
        return self._request("GET", "/v2/task.list", params=params)

    def list_messages(
        self,
        task_id: str,
        *,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """GET /v2/task.listMessages - poll a task's event/message history."""
        params = {
            "task_id": task_id,
            "order": order,
            "limit": limit,
            "cursor": cursor,
        }
        return self._request("GET", "/v2/task.listMessages", params=params)

    def send_message(
        self,
        task_id: str,
        message: str,
        *,
        agent_profile: Optional[str] = None,
        structured_output_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST /v2/task.sendMessage - continue a task's conversation."""
        body = {
            "task_id": task_id,
            "message": {"content": message},
            "agent_profile": agent_profile,
            "structured_output_schema": structured_output_schema,
        }
        return self._request("POST", "/v2/task.sendMessage", json_body=body)

    def confirm_action(
        self,
        task_id: str,
        event_id: str,
        input: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST /v2/task.confirmAction - approve/answer a pending action.

        `event_id` is the `waiting_for_event_id` from the task's
        status_update event. `input` shape (if any) is defined by that
        event's `confirm_input_schema` (see task-lifecycle docs).
        """
        body = {"task_id": task_id, "event_id": event_id, "input": input}
        return self._request("POST", "/v2/task.confirmAction", json_body=body)

    def stop_task(self, task_id: str) -> Dict[str, Any]:
        """POST /v2/task.stop - stop a running task."""
        return self._request("POST", "/v2/task.stop", json_body={"task_id": task_id})

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """POST /v2/task.delete - permanently delete a task."""
        return self._request("POST", "/v2/task.delete", json_body={"task_id": task_id})

    def update_task(
        self,
        task_id: str,
        *,
        title: Optional[str] = None,
        share_visibility: Optional[str] = None,
        enable_visible_in_task_list: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """POST /v2/task.update - update task metadata."""
        body = {
            "task_id": task_id,
            "title": title,
            "share_visibility": share_visibility,
            "enable_visible_in_task_list": enable_visible_in_task_list,
        }
        return self._request("POST", "/v2/task.update", json_body=body)

    # -- webhooks --------------------------------------------------------

    def create_webhook(self, url: str, events: Optional[List[str]] = None) -> Dict[str, Any]:
        """POST /v2/webhook.create - register a webhook URL (API key only).

        Note: per openapi_v2.json, the CreateWebhook request body only
        documents a required `url` field; there is no `events` filter in
        the spec (all webhooks receive task_created/task_stopped events).
        The `events` parameter is accepted for forward-compatibility and
        convenience but is only sent if provided.
        """
        body: Dict[str, Any] = {"url": url}
        if events is not None:
            body["events"] = events
        return self._request("POST", "/v2/webhook.create", json_body=body)

    def list_webhooks(self) -> Dict[str, Any]:
        """GET /v2/webhook.list - list all webhooks on the account."""
        return self._request("GET", "/v2/webhook.list")

    def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """POST /v2/webhook.delete - remove a webhook."""
        return self._request(
            "POST", "/v2/webhook.delete", json_body={"webhook_id": webhook_id}
        )

    def get_webhook_public_key(self) -> Dict[str, Any]:
        """GET /v2/webhook.publicKey - fetch the key used to verify signatures."""
        return self._request("GET", "/v2/webhook.publicKey")


def _demo() -> None:  # pragma: no cover - manual/interactive use only
    """Small CLI demo. Requires a real MANUS_API_KEY to actually run."""
    client = ManusClient()

    print("Creating task...")
    created = client.create_task(
        "Research the top 5 project management tools for a 5-person startup "
        "and summarize pricing in a table."
    )
    task_id = created["task_id"]
    print(f"Created task {task_id}: {created.get('task_url')}")

    print("Polling task status...")
    import time

    while True:
        detail = client.get_task(task_id)
        status = detail.get("status")
        print(f"  status={status}")
        if status in ("stopped", "error"):
            break
        time.sleep(5)

    messages = client.list_messages(task_id, order="desc", limit=10)
    print("Latest messages:", messages)


if __name__ == "__main__":
    _demo()
