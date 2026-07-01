"""Tests for the website-traffic-checker skill's scripts/estimate_traffic.py."""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / ".claude"
    / "skills"
    / "website-traffic-checker"
    / "scripts"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "estimate_traffic", SKILL_SCRIPTS_DIR / "estimate_traffic.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def et():
    return _load_module()


# --- build_request ---------------------------------------------------------


def test_build_request_basic(et):
    req = et.build_request("Example.com", api_key="abc123")
    assert req["params"]["domain"] == "example.com"
    assert req["headers"]["Authorization"] == "Bearer abc123"
    assert req["params"]["keyword_limit"] == et.MAX_KEYWORDS
    assert req["params"]["page_limit"] == et.MAX_PAGES


def test_build_request_clamps_keyword_and_page_limits(et):
    req = et.build_request("example.com", keyword_limit=999999, page_limit=999999)
    assert req["params"]["keyword_limit"] == et.MAX_KEYWORDS
    assert req["params"]["page_limit"] == et.MAX_PAGES


def test_build_request_empty_domain_raises(et):
    with pytest.raises(et.TrafficAPIError):
        et.build_request("")


def test_build_request_no_api_key(et):
    req = et.build_request("example.com")
    assert req["headers"]["Authorization"] == ""


# --- parse_response ----------------------------------------------------------


def test_parse_response_full_data(et):
    raw = {
        "data": {
            "total_visits": 100000,
            "organic_traffic": 40000,
            "bounce_rate": 0.45,
            "keywords_ranked": 3200,
            "top_countries": ["US", "GB"],
            "channels": {"organic": 0.4, "direct": 0.3},
            "device_split": {"desktop": 0.6, "mobile": 0.4},
        }
    }
    metrics = et.parse_response(raw)
    assert metrics["total_visits"] == 100000
    assert metrics["is_partial"] is False
    assert metrics["missing_fields"] == []


def test_parse_response_missing_fields_marks_partial(et):
    raw = {"data": {"total_visits": 100000}}
    metrics = et.parse_response(raw)
    assert metrics["is_partial"] is True
    assert "organic_traffic" in metrics["missing_fields"]
    assert metrics["organic_traffic"] is None
    # Never silently defaults missing numeric fields to 0.
    assert metrics["bounce_rate"] is None


def test_parse_response_handles_flat_shape_without_data_key(et):
    raw = {"total_visits": 500, "organic_traffic": 200, "bounce_rate": 0.5, "keywords_ranked": 10}
    metrics = et.parse_response(raw)
    assert metrics["total_visits"] == 500
    assert metrics["is_partial"] is False


def test_parse_response_empty_dict(et):
    metrics = et.parse_response({})
    assert metrics["is_partial"] is True
    assert len(metrics["missing_fields"]) == len(et.REQUIRED_METRIC_FIELDS)


# --- estimate_traffic (mocked HTTP) ------------------------------------------


def _mock_response(status_code=200, json_data=None, headers=None, raise_json_error=False):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    if raise_json_error:
        resp.json.side_effect = ValueError("bad json")
    else:
        resp.json.return_value = json_data or {}
    return resp


def test_estimate_traffic_success(et):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(
        200,
        {
            "data": {
                "total_visits": 1000,
                "organic_traffic": 400,
                "bounce_rate": 0.4,
                "keywords_ranked": 50,
            }
        },
    )
    result = et.estimate_traffic("example.com", session=fake_session)
    assert result["ok"] is True
    assert result["total_visits"] == 1000
    fake_session.get.assert_called_once()
    _, kwargs = fake_session.get.call_args
    assert kwargs["params"]["domain"] == "example.com"


def test_estimate_traffic_rate_limited(et):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(429, headers={"Retry-After": "30"})
    result = et.estimate_traffic("example.com", session=fake_session)
    assert result["ok"] is False
    assert result["status_code"] == 429
    assert "rate limited" in result["error"].lower()


def test_estimate_traffic_not_found(et):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(404)
    result = et.estimate_traffic("nonexistent-domain.example", session=fake_session)
    assert result["ok"] is False
    assert result["status_code"] == 404


def test_estimate_traffic_timeout(et):
    fake_session = MagicMock()
    fake_session.get.side_effect = requests.exceptions.Timeout()
    result = et.estimate_traffic("example.com", session=fake_session)
    assert result["ok"] is False
    assert "timed out" in result["error"]


def test_estimate_traffic_connection_error(et):
    fake_session = MagicMock()
    fake_session.get.side_effect = requests.exceptions.ConnectionError("dns fail")
    result = et.estimate_traffic("example.com", session=fake_session)
    assert result["ok"] is False
    assert "connection error" in result["error"]


def test_estimate_traffic_invalid_json(et):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(200, raise_json_error=True)
    result = et.estimate_traffic("example.com", session=fake_session)
    assert result["ok"] is False
    assert "invalid json" in result["error"].lower()


def test_estimate_traffic_unexpected_status(et):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(500)
    result = et.estimate_traffic("example.com", session=fake_session)
    assert result["ok"] is False
    assert result["status_code"] == 500


def test_estimate_traffic_partial_response_marks_missing_fields(et):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(200, {"data": {"total_visits": 999}})
    result = et.estimate_traffic("example.com", session=fake_session)
    assert result["ok"] is True
    assert result["is_partial"] is True
    assert "bounce_rate" in result["missing_fields"]


def test_estimate_traffic_uses_requests_module_when_no_session_given(et):
    # Patch the module-level `requests` reference that estimate_traffic() falls
    # back to when no session is injected, verifying the default code path.
    with patch.object(et, "requests") as mock_requests:
        mock_requests.exceptions = requests.exceptions
        mock_requests.get.return_value = _mock_response(
            200, {"data": {"total_visits": 1, "organic_traffic": 1, "bounce_rate": 0.1, "keywords_ranked": 1}}
        )
        result = et.estimate_traffic("example.com")
    assert result["ok"] is True
    mock_requests.get.assert_called_once()
