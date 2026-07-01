import sys
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "seo-audit" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))
