#!/usr/bin/env python3
"""
estimate_traffic.py

A small, mock-testable client that wraps the traffic-estimate style API
described in references/api_reference.md (a Similarweb/Semrush/DataForSEO-
shaped "give me a domain, get back traffic + keyword metrics" endpoint) into
reusable functions:

    build_request(domain, ...)   -> dict          request payload/params
    parse_response(raw_json)     -> dict           normalized metrics
    estimate_traffic(domain,...) -> dict           does both + the HTTP call

Design goals (per the skill's Data Volume Constraints):
  - Never silently invent data: if a field is missing from the response, it
    is reported as None with the field listed under "missing_fields" rather
    than defaulted to 0.
  - Enforce the documented caps: keyword pulls <= 500, page pulls <= 1000.
  - Handle failure modes gracefully instead of raising: connection errors,
    timeouts, rate limiting (HTTP 429), and non-2xx responses all return a
    structured {"error": ...} dict instead of throwing, so callers (and the
    report-writing workflow) can mark a section "based on partial data"
    rather than crashing.

No live API key is required to exercise the request-building or
response-parsing logic; only estimate_traffic() makes a live network call,
and that call is what tests mock with unittest.mock.patch.
"""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_BASE_URL = "https://api.example-traffic-provider.com/v1/traffic"
DEFAULT_TIMEOUT_SECONDS = 15
MAX_KEYWORDS = 500
MAX_PAGES = 1000

REQUIRED_METRIC_FIELDS = (
    "total_visits",
    "organic_traffic",
    "bounce_rate",
    "keywords_ranked",
)


class TrafficAPIError(Exception):
    """Raised only for programmer errors (bad arguments), never for network/API failures."""


def build_request(
    domain: str,
    api_key: str | None = None,
    keyword_limit: int = MAX_KEYWORDS,
    page_limit: int = MAX_PAGES,
    country: str = "world",
) -> dict[str, Any]:
    """
    Build the request payload/params for a traffic-estimate lookup.

    Enforces the skill's mandatory data-volume caps: keyword_limit is clamped
    to MAX_KEYWORDS (500) and page_limit to MAX_PAGES (1000), matching the
    "Data Volume Constraints" section of SKILL.md.
    """
    if not domain or not domain.strip():
        raise TrafficAPIError("domain is required")

    return {
        "url": DEFAULT_BASE_URL,
        "headers": {
            "Authorization": f"Bearer {api_key}" if api_key else "",
            "Accept": "application/json",
        },
        "params": {
            "domain": domain.strip().lower(),
            "country": country or "world",
            "keyword_limit": min(keyword_limit, MAX_KEYWORDS),
            "page_limit": min(page_limit, MAX_PAGES),
        },
    }


def parse_response(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a raw API JSON response into the metrics dict used by the
    reporting workflow. Missing fields are reported as None (never defaulted
    to 0) and listed in "missing_fields" so the report can mark the section
    as based on partial data, per SKILL.md Step 1 / the writing rules.
    """
    data = raw.get("data", raw) if isinstance(raw, dict) else {}

    metrics: dict[str, Any] = {}
    missing: list[str] = []
    for field in REQUIRED_METRIC_FIELDS:
        if field in data and data[field] is not None:
            metrics[field] = data[field]
        else:
            metrics[field] = None
            missing.append(field)

    metrics["top_countries"] = data.get("top_countries", [])
    metrics["channels"] = data.get("channels", {})
    metrics["device_split"] = data.get("device_split", {})
    metrics["missing_fields"] = missing
    metrics["is_partial"] = bool(missing)

    return metrics


def estimate_traffic(
    domain: str,
    api_key: str | None = None,
    keyword_limit: int = MAX_KEYWORDS,
    page_limit: int = MAX_PAGES,
    country: str = "world",
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    session: "requests.Session | None" = None,
) -> dict[str, Any]:
    """
    Fetch and parse traffic metrics for a domain.

    Returns either:
      {"ok": True, "domain": ..., **parsed_metrics}
    or, on any failure (timeout, connection error, rate limit, bad status,
    invalid JSON):
      {"ok": False, "domain": ..., "error": "<human readable reason>", "status_code": <int|None>}

    This function never raises for network/API failures -- callers should
    check the "ok" key, matching the skill's "never silently fill gaps"
    policy (a failure is surfaced, not swallowed into fabricated data).
    """
    request = build_request(
        domain, api_key=api_key, keyword_limit=keyword_limit, page_limit=page_limit, country=country
    )
    http = session or requests

    try:
        response = http.get(
            request["url"],
            headers=request["headers"],
            params=request["params"],
            timeout=timeout,
        )
    except requests.exceptions.Timeout:
        return {"ok": False, "domain": domain, "error": "request timed out", "status_code": None}
    except requests.exceptions.ConnectionError as exc:
        return {"ok": False, "domain": domain, "error": f"connection error: {exc}", "status_code": None}
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "domain": domain, "error": f"request failed: {exc}", "status_code": None}

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        return {
            "ok": False,
            "domain": domain,
            "error": "rate limited" + (f" (retry after {retry_after}s)" if retry_after else ""),
            "status_code": 429,
        }

    if response.status_code == 404:
        return {"ok": False, "domain": domain, "error": "domain not found", "status_code": 404}

    if not (200 <= response.status_code < 300):
        return {
            "ok": False,
            "domain": domain,
            "error": f"unexpected status code {response.status_code}",
            "status_code": response.status_code,
        }

    try:
        raw = response.json()
    except ValueError:
        return {"ok": False, "domain": domain, "error": "invalid JSON in response", "status_code": response.status_code}

    metrics = parse_response(raw)
    return {"ok": True, "domain": domain, "status_code": response.status_code, **metrics}


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Estimate website traffic for a domain.")
    parser.add_argument("domain")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--country", default="world")
    args = parser.parse_args(argv)

    result = estimate_traffic(args.domain, api_key=args.api_key, country=args.country)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
