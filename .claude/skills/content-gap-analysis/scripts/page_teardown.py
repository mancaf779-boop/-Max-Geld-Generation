#!/usr/bin/env python3
"""Live page teardown for Finding 2 (depth gap).

Fetches one or more live URLs and reports the attributes the teardown table needs,
so the table is built from real data, not assumptions:
  - word count, H2 count
  - number of <table> elements (comparison tables)
  - images, embedded video
  - author byline / first-person signals
  - JSON-LD types present (BlogPosting, ItemList, FAQPage, SoftwareApplication,
    AggregateRating), datePublished / dateModified

Usage:
  python page_teardown.py https://example.com/tools/ai-image-generator \
                          https://competitor.com/best-x-tools
"""
import argparse
import json
import re
import sys
from urllib.request import Request, urlopen

UA = {"User-Agent": "Mozilla/5.0 (compatible; ContentGapBot/1.0)"}


def fetch(url, timeout=25):
    req = Request(url, headers=UA)
    with urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore"), r.status


def jsonld_types(html):
    types = []
    for m in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                        html, re.DOTALL | re.IGNORECASE):
        try:
            data = json.loads(m.strip())
        except Exception:
            for t in re.findall(r'"@type"\s*:\s*"([^"]+)"', m):
                types.append(t)
            continue
        for obj in (data if isinstance(data, list) else [data]):
            if isinstance(obj, dict):
                t = obj.get("@type")
                if isinstance(t, list):
                    types += t
                elif t:
                    types.append(t)
    return sorted(set(types))


def analyze_html(html, status=200):
    """Pure function: turn raw HTML into the teardown metrics dict.

    Split out from fetching so the parsing logic is unit-testable without
    making a live network call.
    """
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    words = len(re.findall(r"\w+", text))
    h2 = len(re.findall(r"<h2\b", html, re.IGNORECASE))
    tables = len(re.findall(r"<table\b", html, re.IGNORECASE))
    imgs = len(re.findall(r"<img\b", html, re.IGNORECASE))
    video = bool(re.search(r"<video\b|youtube\.com/embed|youtu\.be|vimeo\.com", html, re.IGNORECASE))
    # Case-insensitive so sentence-initial "We"/"Our" are counted too (E-E-A-T
    # signals are just as real at the start of a sentence).
    first_person = len(re.findall(r"\b(I|we|our|my|us)\b", text, re.IGNORECASE))
    author = bool(re.search(r'author|byline|written by|rel="author"', html, re.IGNORECASE))
    types = jsonld_types(html)
    has_date_mod = bool(re.search(r"dateModified", html))
    has_date_pub = bool(re.search(r"datePublished", html))
    return {
        "status": status,
        "word_count": words,
        "h2_count": h2,
        "table_count": tables,
        "image_count": imgs,
        "has_video": video,
        "first_person_mentions": first_person,
        "has_author_byline": author,
        "jsonld_types": types,
        "has_date_published": has_date_pub,
        "has_date_modified": has_date_mod,
    }


def teardown(url):
    """Fetch a URL live and return its teardown metrics dict, or None on failure."""
    try:
        html, status = fetch(url)
    except Exception as e:
        print(f"\n## {url}\n  FETCH FAILED: {e}")
        return None
    result = analyze_html(html, status)
    print_teardown(url, result)
    return result


def print_teardown(url, result):
    print(f"\n## {url}  (HTTP {result['status']})")
    print(f"  Word count (approx):   {result['word_count']:,}")
    print(f"  H2 sections:           {result['h2_count']}")
    print(f"  <table> elements:      {result['table_count']}")
    print(f"  Images:                {result['image_count']}")
    print(f"  Embedded video:        {'yes' if result['has_video'] else 'no'}")
    print(f"  Author/byline present: {'yes' if result['has_author_byline'] else 'no'}")
    print(f"  First-person mentions: {result['first_person_mentions']}")
    types = result["jsonld_types"]
    print(f"  JSON-LD @types:        {', '.join(types) if types else 'NONE'}")
    print(f"  datePublished / dateModified: {result['has_date_published']} / {result['has_date_modified']}")


def main():
    parser = argparse.ArgumentParser(
        description="Live page teardown: fetch URLs and report depth/quality signals.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("urls", nargs="+", help="One or more live URLs to tear down.")
    args = parser.parse_args()

    failures = 0
    for u in args.urls:
        if teardown(u) is None:
            failures += 1
    if failures == len(args.urls):
        sys.exit(f"ERROR: all {failures} URL(s) failed to fetch.")


if __name__ == "__main__":
    main()
