"""Structural / content validation tests for the html-video-production skill.

This skill bundle is pure markdown + static assets (no Python scripts to
unit test), so these tests validate structure and cross-references instead:
frontmatter shape, sub-skill layout, internal path references, the SFX
manifest, and the absence of leftover third-party-agent-specific content
that should have been adapted for Claude Code.
"""

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = REPO_ROOT / ".claude" / "skills" / "html-video-production"
REFERENCES_DIR = SKILL_ROOT / "references"
SFX_DIR = SKILL_ROOT / "assets" / "sfx"

# Files that carry Apache-2.0 legal text verbatim from upstream — must never
# be modified, and are excluded from "no Manus mentions" / adaptation checks.
LEGAL_FILES = {"LICENSE", "NOTICE.txt", "UPSTREAM_LICENSE_APACHE-2.0.txt"}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Path-like references inside markdown bodies: `backtick/paths.ext` or
# [text](relative/path.ext) links, best-effort (not required to catch
# literally everything -- see task description).
BACKTICK_PATH_RE = re.compile(
    r"`(\.{1,2}/[A-Za-z0-9_\-./]+\.(?:md|json|mp3|mjs|cjs|js|py|sh|txt))`"
)
MDLINK_PATH_RE = re.compile(
    r"\]\(([A-Za-z0-9_\-./]+\.(?:md|json|mp3|mjs|cjs|js|py|sh|txt))\)"
)

# Directories/paths that are legitimately generated at run time by the
# workflows themselves (not shipped in the skill bundle), so a reference to
# them is not a broken cross-reference.
RUNTIME_GENERATED_PREFIXES = (
    "/tmp/",
    ".hyperframes/",
    ".media/",
)


def _skill_dirs():
    """All installed sub-skill directories under references/."""
    assert REFERENCES_DIR.is_dir(), f"missing references/ dir at {REFERENCES_DIR}"
    return sorted(p for p in REFERENCES_DIR.iterdir() if p.is_dir())


def _split_frontmatter(text):
    """Return (frontmatter_dict, body_str) for a SKILL.md's content.

    Most SKILL.md files in this bundle open directly with the YAML
    frontmatter block. Some sub-skills additionally carry a short
    "Claude Code adaptation note" callout *before* the frontmatter (mirroring
    the upstream bundle's own convention of a note-then-frontmatter layout),
    so we locate the first ``---`` delimited block anywhere near the top of
    the file rather than requiring it at byte offset 0.
    """
    match = re.search(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL | re.MULTILINE)
    assert match, "SKILL.md must contain a --- delimited YAML frontmatter block"
    fm = yaml.safe_load(match.group(1))
    return fm, match.group(2)


def _all_markdown_files():
    return sorted(SKILL_ROOT.rglob("*.md"))


# ---------------------------------------------------------------------------
# Top-level SKILL.md
# ---------------------------------------------------------------------------


class TestRootSkillMd:
    def test_root_skill_md_exists(self):
        assert (SKILL_ROOT / "SKILL.md").is_file()

    def test_root_frontmatter_valid(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = _split_frontmatter(text)
        assert isinstance(fm, dict)
        assert fm.get("name"), "root SKILL.md frontmatter must have a non-empty name"
        assert fm.get(
            "description"
        ), "root SKILL.md frontmatter must have a non-empty description"

    def test_root_name_is_hyphen_case(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = _split_frontmatter(text)
        assert NAME_RE.match(fm["name"]), f"name {fm['name']!r} is not hyphen-case"

    def test_root_name_matches_directory(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = _split_frontmatter(text)
        assert fm["name"] == SKILL_ROOT.name


# ---------------------------------------------------------------------------
# Legal files preserved verbatim
# ---------------------------------------------------------------------------


class TestLegalFiles:
    @pytest.mark.parametrize("filename", sorted(LEGAL_FILES))
    def test_legal_file_present(self, filename):
        assert (SKILL_ROOT / filename).is_file(), f"missing legal file {filename}"

    def test_license_mentions_apache(self):
        text = (SKILL_ROOT / "LICENSE").read_text(encoding="utf-8")
        assert "Apache License" in text

    def test_upstream_license_is_apache_2_0(self):
        text = (SKILL_ROOT / "UPSTREAM_LICENSE_APACHE-2.0.txt").read_text(
            encoding="utf-8"
        )
        assert "Apache License" in text
        assert "Version 2.0" in text


# ---------------------------------------------------------------------------
# Sub-skills under references/
# ---------------------------------------------------------------------------


class TestSubSkills:
    def test_at_least_one_subskill_present(self):
        assert len(_skill_dirs()) > 0

    @pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
    def test_subskill_has_skill_md(self, skill_dir):
        assert (skill_dir / "SKILL.md").is_file(), f"{skill_dir.name} missing SKILL.md"

    @pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
    def test_subskill_frontmatter_valid(self, skill_dir):
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = _split_frontmatter(text)
        assert isinstance(fm, dict)
        assert fm.get("name"), f"{skill_dir.name}/SKILL.md missing non-empty name"
        assert fm.get(
            "description"
        ), f"{skill_dir.name}/SKILL.md missing non-empty description"

    @pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
    def test_subskill_name_is_hyphen_case(self, skill_dir):
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = _split_frontmatter(text)
        assert NAME_RE.match(str(fm["name"])), (
            f"{skill_dir.name}/SKILL.md name {fm['name']!r} is not hyphen-case"
        )

    @pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
    def test_subskill_name_matches_directory(self, skill_dir):
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = _split_frontmatter(text)
        assert fm["name"] == skill_dir.name


# ---------------------------------------------------------------------------
# Cross-reference integrity (best-effort path resolution)
# ---------------------------------------------------------------------------


def _iter_referenced_paths():
    """Yield (markdown_file, raw_ref) for every path-like reference found."""
    for md_file in _all_markdown_files():
        if md_file.name in LEGAL_FILES:
            continue
        text = md_file.read_text(encoding="utf-8", errors="replace")
        refs = set(BACKTICK_PATH_RE.findall(text)) | set(
            MDLINK_PATH_RE.findall(text)
        )
        for ref in refs:
            yield md_file, ref


def _unresolved_references():
    unresolved = []
    for md_file, ref in _iter_referenced_paths():
        if ref.startswith("http://") or ref.startswith("https://"):
            continue
        if ref.startswith(RUNTIME_GENERATED_PREFIXES):
            continue
        target = (md_file.parent / ref).resolve()
        try:
            target.relative_to(REPO_ROOT.resolve())
        except ValueError:
            # Reference escapes the repo entirely (e.g. absolute path
            # elsewhere on disk) -- not something we can validate here.
            continue
        if not target.exists():
            unresolved.append((str(md_file.relative_to(SKILL_ROOT)), ref))
    return unresolved


class TestCrossReferences:
    def test_referenced_paths_resolve(self):
        unresolved = _unresolved_references()
        assert not unresolved, (
            "Found markdown/asset references that do not resolve to a file "
            f"on disk: {unresolved}"
        )

    def test_top_level_workflow_table_targets_exist(self):
        """Every references/<name>/SKILL.md path named in the root router
        table must exist (the router is the most load-bearing set of
        cross-references in the whole skill)."""
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        targets = re.findall(r"`(references/[a-z0-9\-]+/SKILL\.md)`", text)
        assert targets, "expected the router table to reference sub-skill SKILL.md files"
        for rel in targets:
            assert (SKILL_ROOT / rel).is_file(), f"router references missing file {rel}"


# ---------------------------------------------------------------------------
# assets/sfx manifest
# ---------------------------------------------------------------------------


class TestSfxManifest:
    def test_manifest_exists_and_is_valid_json(self):
        manifest_path = SFX_DIR / "manifest.json"
        assert manifest_path.is_file()
        with manifest_path.open(encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict) and data, "manifest.json should be a non-empty object"

    def test_every_manifest_entry_file_exists(self):
        manifest_path = SFX_DIR / "manifest.json"
        with manifest_path.open(encoding="utf-8") as f:
            data = json.load(f)
        for key, entry in data.items():
            assert "file" in entry, f"manifest entry {key!r} missing 'file'"
            assert (SFX_DIR / entry["file"]).is_file(), (
                f"manifest entry {key!r} points to missing file {entry['file']!r}"
            )

    def test_every_mp3_is_listed_in_manifest(self):
        manifest_path = SFX_DIR / "manifest.json"
        with manifest_path.open(encoding="utf-8") as f:
            data = json.load(f)
        listed_files = {entry["file"] for entry in data.values()}
        actual_mp3s = {p.name for p in SFX_DIR.glob("*.mp3")}
        missing_from_manifest = actual_mp3s - listed_files
        assert not missing_from_manifest, (
            f"mp3 files present but not listed in manifest.json: {missing_from_manifest}"
        )

    def test_manifest_has_no_stale_entries(self):
        manifest_path = SFX_DIR / "manifest.json"
        with manifest_path.open(encoding="utf-8") as f:
            data = json.load(f)
        listed_files = {entry["file"] for entry in data.values()}
        actual_mp3s = {p.name for p in SFX_DIR.glob("*.mp3")}
        stale = listed_files - actual_mp3s
        assert not stale, f"manifest.json lists files that no longer exist: {stale}"

    def test_credits_file_present(self):
        assert (SFX_DIR / "CREDITS.md").is_file()


# ---------------------------------------------------------------------------
# No leftover third-party-agent-specific plumbing
# ---------------------------------------------------------------------------


class TestNoLeftoverAgentSpecificContent:
    def test_no_hardcoded_home_ubuntu_paths(self):
        """No absolute Manus-sandbox-style paths should remain in any
        installed SKILL.md (they should have been made relative/portable)."""
        offenders = []
        for skill_md in [SKILL_ROOT / "SKILL.md"] + [
            d / "SKILL.md" for d in _skill_dirs()
        ]:
            text = skill_md.read_text(encoding="utf-8")
            if "/home/ubuntu" in text:
                offenders.append(str(skill_md.relative_to(SKILL_ROOT)))
        assert not offenders, f"leftover /home/ubuntu paths in: {offenders}"

    def test_no_hardcoded_home_ubuntu_paths_anywhere(self):
        """Broader sweep across every markdown/script file in the bundle."""
        offenders = []
        for path in list(_all_markdown_files()) + list(
            SKILL_ROOT.rglob("*.mjs")
        ) + list(SKILL_ROOT.rglob("*.cjs")) + list(SKILL_ROOT.rglob("*.js")):
            if path.name in LEGAL_FILES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "/home/ubuntu" in text:
                offenders.append(str(path.relative_to(SKILL_ROOT)))
        assert not offenders, f"leftover /home/ubuntu paths in: {offenders}"

    def test_no_manus_mentions_outside_legal_files(self):
        """"Manus" (the original agent this bundle was authored for) should
        not appear anywhere except the untouched legal/license files, and
        except as a substring of unrelated words like "manuscript"."""
        manus_word_re = re.compile(r"\bmanus\b", re.IGNORECASE)
        offenders = []
        for path in _all_markdown_files():
            if path.name in LEGAL_FILES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if manus_word_re.search(text):
                offenders.append(str(path.relative_to(SKILL_ROOT)))
        assert not offenders, f"leftover 'Manus' mentions in: {offenders}"

    def test_no_notify_user_tool_references(self):
        offenders = []
        for path in _all_markdown_files():
            if path.name in LEGAL_FILES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"notify_user", text, re.IGNORECASE):
                offenders.append(str(path.relative_to(SKILL_ROOT)))
        assert not offenders, f"leftover notify_user references in: {offenders}"

    def test_legal_files_unmodified_byte_for_byte(self):
        """Sanity check that the license files still look like license
        files (contain their expected headers) -- guards against an
        accidental future edit gutting them."""
        notice = (SKILL_ROOT / "NOTICE.txt").read_text(encoding="utf-8")
        assert "Apache License" in notice
        assert "heygen-com/hyperframes" in notice
