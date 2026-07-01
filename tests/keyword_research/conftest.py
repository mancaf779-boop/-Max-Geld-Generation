import json
import sys
from pathlib import Path

import pytest

SKILL_SCRIPTS = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "keyword-research" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))


def make_keywords(n=300, volume_col="Monthly Volume (US)", clusters=None):
    """Build a synthetic list of n keyword dicts spread across 5 clusters."""
    clusters = clusters or ["Cluster A", "Cluster B", "Cluster C", "Cluster D", "Cluster E"]
    priorities = ["High", "Medium", "Low"]
    kd_levels = ["Easy", "Medium", "Hard"]
    keywords = []
    for i in range(n):
        cluster = clusters[i % len(clusters)]
        keywords.append({
            "Keyword": f"keyword {i}",
            "Topic Cluster": cluster,
            "Search Intent": "Informational",
            volume_col: 100 + i,
            "Global Volume": 150 + i,
            "Keyword Difficulty (KD)": (i % 100),
            "KD Level": kd_levels[i % 3],
            "CPC": round(0.1 * (i % 10), 2),
            "Parent Topic": f"parent {i % 10}",
            "Recommended Content Type": "Blog Post",
            "Priority": priorities[i % 3],
        })
    return keywords


def make_full_payload(n=300, volume_col="Monthly Volume (US)"):
    return {
        "keywords": make_keywords(n, volume_col=volume_col),
        "competitors": [
            {"Domain": f"competitor{i}.com", "Traffic Share %": f"{i}%",
             "Traffic Value": f"${i * 1000}", "DR": 50 + i, "Observations": "Test observation."}
            for i in range(1, 21)
        ],
        "gaps": [
            {"Competitor Domain": f"competitor{i}.com", "Keyword Gap": f"gap keyword {i}",
             "Search Volume": 100 * i, "Recommended Action": "Create content."}
            for i in range(1, 21)
        ],
        "insights": {
            "tam": "100,000 monthly searches",
            "opportunities": "Focus on low KD queries.",
            "findings": [f"Finding {i}" for i in range(1, 6)],
            "recommendations": [f"Recommendation {i}" for i in range(1, 6)],
        },
    }


@pytest.fixture
def full_payload_path(tmp_path):
    payload = make_full_payload(300)
    path = tmp_path / "full_data.json"
    path.write_text(json.dumps(payload))
    return path
