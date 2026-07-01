"""Tests for the stock-analysis skill's scripts/fetch_quote.py."""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / ".claude"
    / "skills"
    / "stock-analysis"
    / "scripts"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("fetch_quote", SKILL_SCRIPTS_DIR / "fetch_quote.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def fq():
    return _load_module()


def _chart_payload(closes, symbol="AAPL", currency="USD"):
    timestamps = list(range(1_700_000_000, 1_700_000_000 + len(closes) * 86400, 86400))
    return {
        "chart": {
            "result": [
                {
                    "meta": {
                        "symbol": symbol,
                        "currency": currency,
                        "regularMarketPrice": closes[-1] if closes else None,
                        "fiftyTwoWeekHigh": max(closes) if closes else None,
                        "fiftyTwoWeekLow": min(closes) if closes else None,
                    },
                    "timestamp": timestamps,
                    "indicators": {"quote": [{"close": closes}]},
                }
            ],
            "error": None,
        }
    }


# --- build_request -----------------------------------------------------------


def test_build_request_uppercases_symbol(fq):
    req = fq.build_request("aapl")
    assert req["url"].endswith("/AAPL")


def test_build_request_empty_symbol_raises(fq):
    with pytest.raises(fq.InvalidTickerError):
        fq.build_request("")


def test_build_request_invalid_interval_raises(fq):
    with pytest.raises(fq.InvalidTickerError):
        fq.build_request("AAPL", interval="3d")


def test_build_request_invalid_range_raises(fq):
    with pytest.raises(fq.InvalidTickerError):
        fq.build_request("AAPL", range_="20y")


# --- parse_chart_response -----------------------------------------------------


def test_parse_chart_response_success(fq):
    parsed = fq.parse_chart_response(_chart_payload([100.0, 101.0, 105.0]))
    assert parsed["error"] is None
    assert parsed["symbol"] == "AAPL"
    assert parsed["closes"] == [100.0, 101.0, 105.0]


def test_parse_chart_response_filters_none_closes(fq):
    payload = _chart_payload([100.0, 101.0, 105.0])
    payload["chart"]["result"][0]["indicators"]["quote"][0]["close"] = [100.0, None, 105.0]
    parsed = fq.parse_chart_response(payload)
    assert parsed["closes"] == [100.0, 105.0]


def test_parse_chart_response_invalid_ticker_error_object(fq):
    payload = {"chart": {"result": None, "error": {"code": "Not Found", "description": "No data found, symbol may be delisted"}}}
    parsed = fq.parse_chart_response(payload)
    assert parsed["error"] is not None
    assert parsed["closes"] == []


def test_parse_chart_response_empty_result_list(fq):
    parsed = fq.parse_chart_response({"chart": {"result": [], "error": None}})
    assert parsed["error"] is not None


def test_parse_chart_response_all_none_closes(fq):
    payload = _chart_payload([1, 2, 3])
    payload["chart"]["result"][0]["indicators"]["quote"][0]["close"] = [None, None, None]
    parsed = fq.parse_chart_response(payload)
    assert parsed["error"] is not None
    assert "no valid close" in parsed["error"]


def test_parse_chart_response_malformed_input(fq):
    parsed = fq.parse_chart_response({})
    assert parsed["error"] is not None


# --- compute_metrics -----------------------------------------------------------


def test_compute_metrics_percent_change_and_sma(fq):
    metrics = fq.compute_metrics([100.0, 110.0, 121.0], sma_window=3)
    assert metrics["latest_close"] == 121.0
    assert metrics["percent_change"] == pytest.approx(21.0)
    assert metrics["sma"] == pytest.approx((100.0 + 110.0 + 121.0) / 3)


def test_compute_metrics_sma_window_larger_than_data(fq):
    metrics = fq.compute_metrics([100.0, 110.0], sma_window=20)
    assert metrics["sma_window"] == 2
    assert metrics["sma"] == pytest.approx(105.0)


def test_compute_metrics_empty_closes(fq):
    metrics = fq.compute_metrics([])
    assert metrics["latest_close"] is None
    assert metrics["percent_change"] is None
    assert metrics["sma"] is None


def test_compute_metrics_zero_first_close_avoids_division_by_zero(fq):
    metrics = fq.compute_metrics([0.0, 5.0])
    assert metrics["percent_change"] is None
    assert metrics["latest_close"] == 5.0


# --- fetch_quote (mocked HTTP) --------------------------------------------------


def _mock_response(status_code=200, json_data=None, raise_json_error=False):
    resp = MagicMock()
    resp.status_code = status_code
    if raise_json_error:
        resp.json.side_effect = ValueError("bad json")
    else:
        resp.json.return_value = json_data or {}
    return resp


def test_fetch_quote_success(fq):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(200, _chart_payload([100.0, 105.0, 110.25]))
    result = fq.fetch_quote("aapl", session=fake_session)
    assert result["ok"] is True
    assert result["symbol"] == "AAPL"
    assert result["latest_close"] == 110.25
    assert result["percent_change"] == pytest.approx(10.25)
    fake_session.get.assert_called_once()


def test_fetch_quote_invalid_ticker_never_calls_network(fq):
    fake_session = MagicMock()
    result = fq.fetch_quote("", session=fake_session)
    assert result["ok"] is False
    fake_session.get.assert_not_called()


def test_fetch_quote_api_reports_invalid_ticker(fq):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(
        200, {"chart": {"result": None, "error": {"description": "No data found, symbol may be delisted"}}}
    )
    result = fq.fetch_quote("NOTREAL", session=fake_session)
    assert result["ok"] is False
    assert "no data found" in result["error"].lower() or "delisted" in result["error"].lower()


def test_fetch_quote_rate_limited(fq):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(429)
    result = fq.fetch_quote("AAPL", session=fake_session)
    assert result["ok"] is False
    assert result["status_code"] == 429


def test_fetch_quote_not_found_status(fq):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(404)
    result = fq.fetch_quote("ZZZZZ", session=fake_session)
    assert result["ok"] is False
    assert result["status_code"] == 404


def test_fetch_quote_timeout(fq):
    fake_session = MagicMock()
    fake_session.get.side_effect = requests.exceptions.Timeout()
    result = fq.fetch_quote("AAPL", session=fake_session)
    assert result["ok"] is False
    assert "timed out" in result["error"]


def test_fetch_quote_connection_error(fq):
    fake_session = MagicMock()
    fake_session.get.side_effect = requests.exceptions.ConnectionError("dns fail")
    result = fq.fetch_quote("AAPL", session=fake_session)
    assert result["ok"] is False
    assert "connection error" in result["error"]


def test_fetch_quote_invalid_json_response(fq):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(200, raise_json_error=True)
    result = fq.fetch_quote("AAPL", session=fake_session)
    assert result["ok"] is False
    assert "invalid json" in result["error"].lower()


def test_fetch_quote_request_params_include_symbol(fq):
    fake_session = MagicMock()
    fake_session.get.return_value = _mock_response(200, _chart_payload([1.0, 2.0]))
    fq.fetch_quote("msft", region="US", interval="1d", range_="5d", session=fake_session)
    _, kwargs = fake_session.get.call_args
    assert kwargs["params"]["range"] == "5d"
    assert kwargs["params"]["interval"] == "1d"
