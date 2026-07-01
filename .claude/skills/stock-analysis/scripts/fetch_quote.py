#!/usr/bin/env python3
"""
fetch_quote.py

A small client for the Yahoo-Finance-style `get_stock_chart` endpoint
documented in references/yahoo-api.md. Fetches a quote's historical chart
data and computes basic derived metrics:

    - latest close price
    - percent change over the requested range (first close -> last close)
    - simple moving average (SMA) over the closes

Functions:
    build_request(symbol, ...)  -> dict     request params for the chart endpoint
    parse_chart_response(raw)   -> dict     normalized {timestamps, closes, meta}
    compute_metrics(closes, sma_window)     -> dict derived metrics
    fetch_quote(symbol, ...)    -> dict     does all of the above + the HTTP call

No live API key/network is required to exercise build_request/parse_chart_response/
compute_metrics; only fetch_quote() performs the HTTP call, which is what tests
mock with unittest.mock.patch.
"""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
DEFAULT_TIMEOUT_SECONDS = 15
VALID_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"}
VALID_RANGES = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}


class InvalidTickerError(ValueError):
    """Raised when the symbol is empty/malformed before any network call is made."""


def build_request(
    symbol: str,
    region: str = "US",
    interval: str = "1d",
    range_: str = "1mo",
) -> dict[str, Any]:
    """Build the request URL/params for the get_stock_chart-style endpoint."""
    if not symbol or not symbol.strip():
        raise InvalidTickerError("symbol is required")
    if interval not in VALID_INTERVALS:
        raise InvalidTickerError(f"invalid interval: {interval!r}")
    if range_ not in VALID_RANGES:
        raise InvalidTickerError(f"invalid range: {range_!r}")

    symbol = symbol.strip().upper()
    return {
        "url": f"{DEFAULT_BASE_URL}/{symbol}",
        "params": {
            "region": region,
            "interval": interval,
            "range": range_,
            "includeAdjustedClose": "true",
        },
    }


def parse_chart_response(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a raw get_stock_chart JSON response into
    {"symbol", "currency", "timestamps", "closes", "error"}.

    Returns a dict with "error" set (and empty timestamps/closes) if the
    response is malformed, has no results, or Yahoo returned an error object
    (e.g. for an invalid ticker), instead of raising -- callers decide how to
    surface that to the user.
    """
    chart = raw.get("chart", {}) if isinstance(raw, dict) else {}

    api_error = chart.get("error")
    if api_error:
        description = api_error.get("description") if isinstance(api_error, dict) else str(api_error)
        return {
            "symbol": None,
            "currency": None,
            "timestamps": [],
            "closes": [],
            "error": description or "unknown API error",
        }

    results = chart.get("result") or []
    if not results:
        return {
            "symbol": None,
            "currency": None,
            "timestamps": [],
            "closes": [],
            "error": "no chart data returned (invalid ticker or unsupported range/interval)",
        }

    result = results[0]
    meta = result.get("meta", {})
    timestamps = result.get("timestamp", []) or []

    quotes = (result.get("indicators", {}).get("quote") or [{}])[0]
    closes = quotes.get("close", []) or []

    # Filter out trailing/interleaved None closes (common for the most recent,
    # still-forming bar) so derived metrics don't choke on them.
    cleaned_pairs = [(ts, c) for ts, c in zip(timestamps, closes) if c is not None]
    clean_timestamps = [p[0] for p in cleaned_pairs]
    clean_closes = [p[1] for p in cleaned_pairs]

    if not clean_closes:
        return {
            "symbol": meta.get("symbol"),
            "currency": meta.get("currency"),
            "timestamps": [],
            "closes": [],
            "error": "no valid close prices in response",
        }

    return {
        "symbol": meta.get("symbol"),
        "currency": meta.get("currency"),
        "timestamps": clean_timestamps,
        "closes": clean_closes,
        "regular_market_price": meta.get("regularMarketPrice"),
        "fifty_two_week_high": meta.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": meta.get("fiftyTwoWeekLow"),
        "error": None,
    }


def compute_metrics(closes: list[float], sma_window: int = 20) -> dict[str, Any]:
    """
    Compute percent change (first close -> last close) and a simple moving
    average over the last `sma_window` closes (or all closes if fewer are
    available).
    """
    if not closes:
        return {"latest_close": None, "percent_change": None, "sma": None, "sma_window": sma_window}

    first_close = closes[0]
    latest_close = closes[-1]

    percent_change = None
    if first_close not in (None, 0):
        percent_change = round((latest_close - first_close) / first_close * 100, 2)

    window = closes[-sma_window:] if sma_window > 0 else closes
    sma = round(sum(window) / len(window), 4) if window else None

    return {
        "latest_close": latest_close,
        "percent_change": percent_change,
        "sma": sma,
        "sma_window": min(sma_window, len(closes)),
    }


def fetch_quote(
    symbol: str,
    region: str = "US",
    interval: str = "1d",
    range_: str = "1mo",
    sma_window: int = 20,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    session: "requests.Session | None" = None,
) -> dict[str, Any]:
    """
    Fetch a quote's chart data and return normalized data plus derived metrics.

    Returns {"ok": True, ...} on success, or {"ok": False, "symbol":..., "error": ...}
    on any failure: invalid ticker/params, network error, timeout, rate limit,
    or a malformed/empty response. Never raises for those cases.
    """
    try:
        request = build_request(symbol, region=region, interval=interval, range_=range_)
    except InvalidTickerError as exc:
        return {"ok": False, "symbol": symbol, "error": str(exc)}

    http = session or requests
    try:
        response = http.get(request["url"], params=request["params"], timeout=timeout)
    except requests.exceptions.Timeout:
        return {"ok": False, "symbol": symbol, "error": "request timed out"}
    except requests.exceptions.ConnectionError as exc:
        return {"ok": False, "symbol": symbol, "error": f"connection error: {exc}"}
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "symbol": symbol, "error": f"request failed: {exc}"}

    if response.status_code == 429:
        return {"ok": False, "symbol": symbol, "error": "rate limited", "status_code": 429}
    if response.status_code == 404:
        return {"ok": False, "symbol": symbol, "error": "ticker not found", "status_code": 404}
    if not (200 <= response.status_code < 300):
        return {
            "ok": False,
            "symbol": symbol,
            "error": f"unexpected status code {response.status_code}",
            "status_code": response.status_code,
        }

    try:
        raw = response.json()
    except ValueError:
        return {"ok": False, "symbol": symbol, "error": "invalid JSON in response"}

    parsed = parse_chart_response(raw)
    if parsed.get("error"):
        return {"ok": False, "symbol": symbol, "error": parsed["error"]}

    metrics = compute_metrics(parsed["closes"], sma_window=sma_window)

    return {
        "ok": True,
        "symbol": parsed["symbol"] or symbol.upper(),
        "currency": parsed["currency"],
        "regular_market_price": parsed.get("regular_market_price"),
        "fifty_two_week_high": parsed.get("fifty_two_week_high"),
        "fifty_two_week_low": parsed.get("fifty_two_week_low"),
        **metrics,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Fetch a stock quote and derived metrics.")
    parser.add_argument("symbol")
    parser.add_argument("--region", default="US")
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--range", dest="range_", default="1mo")
    parser.add_argument("--sma-window", type=int, default=20)
    args = parser.parse_args(argv)

    result = fetch_quote(
        args.symbol, region=args.region, interval=args.interval, range_=args.range_, sma_window=args.sma_window
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
