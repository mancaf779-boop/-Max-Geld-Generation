"""Unit tests for the shared cga_common.py helpers."""
import sys

import pandas as pd
import pytest

from . import conftest  # noqa: F401  (adds scripts dir to sys.path)

import cga_common as cc


# ------------------------- to_num / read_csv -------------------------------
def test_to_num_strips_commas_and_coerces():
    s = pd.Series(["1,000", "2,500.5", "not a number", None])
    out = cc.to_num(s)
    assert out.tolist() == [1000.0, 2500.5, 0.0, 0.0]


def test_read_csv_missing_file_exits(tmp_path):
    missing = tmp_path / "nope.csv"
    with pytest.raises(SystemExit):
        cc.read_csv(str(missing))


def test_read_csv_empty_file_exits(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    with pytest.raises(SystemExit):
        cc.read_csv(str(empty))


def test_read_csv_header_only_exits(tmp_path):
    header_only = tmp_path / "header_only.csv"
    header_only.write_text("Keyword,Volume\n")
    with pytest.raises(SystemExit):
        cc.read_csv(str(header_only))


def test_read_csv_reads_bom_and_data(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("﻿Keyword,Volume\nfoo,100\n", encoding="utf-8")
    df = cc.read_csv(str(path))
    assert list(df.columns) == ["Keyword", "Volume"]
    assert df.iloc[0]["Keyword"] == "foo"


# ------------------------- brand filtering ----------------------------------
def test_brand_token_variants_chatgpt_known_typos():
    variants = cc.brand_token_variants("chatgpt")
    assert "chat gpt" in variants
    assert "chatgpt" in variants


def test_brand_token_variants_unknown_brand_still_has_base_forms():
    variants = cc.brand_token_variants("Acme Tool")
    assert "acme tool" in variants
    assert "acme-tool" in variants
    assert "acmetool" in variants


def test_drop_brand_rows_removes_matching_keywords():
    df = pd.DataFrame({"Keyword": ["acme tool review", "generic search term", "buy acmetool now"]})
    variants = cc.brand_token_variants("acme tool")
    out = cc.drop_brand_rows(df, "Keyword", variants)
    assert list(out["Keyword"]) == ["generic search term"]


# ------------------------- page-type bucketing ------------------------------
def test_bucket_url_matches_known_rules():
    assert cc.bucket_url("https://example.com/blog/post") == "Blog"
    assert cc.bucket_url("https://example.com/tools/widget") == "Tools"
    assert cc.bucket_url("https://example.com/") == "Homepage"
    assert cc.bucket_url("https://example.com/random/page") == "Other"


def test_traffic_by_page_type_computes_share():
    df = pd.DataFrame({
        "URL": ["https://x.com/blog/a", "https://x.com/blog/b", "https://x.com/tools/c"],
        "Traffic": [100, 300, 600],
    })
    out = cc.traffic_by_page_type(df)
    blog_row = out[out["page_type"] == "Blog"].iloc[0]
    tools_row = out[out["page_type"] == "Tools"].iloc[0]
    assert blog_row["Traffic"] == 400
    assert tools_row["Traffic"] == 600
    assert pytest.approx(blog_row["share_%"], abs=0.1) == 40.0
    assert pytest.approx(tools_row["share_%"], abs=0.1) == 60.0


def test_traffic_by_page_type_missing_column_raises_keyerror():
    df = pd.DataFrame({"NotURL": ["a"], "NotTraffic": [1]})
    with pytest.raises(KeyError):
        cc.traffic_by_page_type(df)


def test_traffic_by_page_type_zero_traffic_no_divide_by_zero():
    df = pd.DataFrame({"URL": ["https://x.com/blog/a"], "Traffic": [0]})
    out = cc.traffic_by_page_type(df)
    assert out["share_%"].iloc[0] == 0.0


# ------------------------- trend math ---------------------------------------
def test_parse_trends_handles_valid_and_invalid_cells():
    assert cc.parse_trends("10, 20, 30") == [10.0, 20.0, 30.0]
    assert cc.parse_trends("10, bad, 30") == [10.0, 30.0]
    assert cc.parse_trends(None) == []
    assert cc.parse_trends(42) == []


def test_keyword_trajectories_empty_series_returns_zero():
    twelve, recent = cc.keyword_trajectories([], [])
    assert (twelve, recent) == (0.0, 0.0)


def test_keyword_trajectories_short_series_skipped():
    # Series shorter than 12 points must be skipped, not crash.
    twelve, recent = cc.keyword_trajectories([[1, 2, 3]], [10.0])
    assert (twelve, recent) == (0.0, 0.0)


def test_keyword_trajectories_growing_series():
    growing = list(range(10, 130, 10))  # 12 points, steadily increasing
    twelve, recent = cc.keyword_trajectories([growing], [100.0])
    assert twelve > 0
    assert recent > 0
    assert cc.direction_label(recent) == "Growing"


def test_keyword_trajectories_flat_series_is_stable():
    flat = [50.0] * 12
    twelve, recent = cc.keyword_trajectories([flat], [100.0])
    assert twelve == 0.0
    assert recent == 0.0
    assert cc.direction_label(recent) == "Stable / Maturing"


def test_direction_label_thresholds():
    assert cc.direction_label(15) == "Growing"
    assert cc.direction_label(10) == "Growing"
    assert cc.direction_label(-8) == "Declining"
    assert cc.direction_label(-20) == "Declining"
    assert cc.direction_label(0) == "Stable / Maturing"


# ------------------------- clustering ---------------------------------------
def test_assign_cluster_first_match_wins():
    rules = [("Translation", "translat"), ("Writing", "writ")]
    assert cc.assign_cluster("translate to spanish", rules) == "Translation"
    assert cc.assign_cluster("ai writing tool", rules) == "Writing"
    assert cc.assign_cluster("something else", rules) == "Other"
