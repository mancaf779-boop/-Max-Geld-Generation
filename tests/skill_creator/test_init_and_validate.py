import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "skill-creator" / "scripts"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def init_skill_mod():
    return _load("init_skill", SCRIPTS_DIR / "init_skill.py")


@pytest.fixture()
def quick_validate_mod():
    return _load("quick_validate", SCRIPTS_DIR / "quick_validate.py")


class TestValidateSkillName:
    def test_valid_names(self, init_skill_mod):
        for name in ["a", "my-skill", "data-analyzer-2", "a-b-c"]:
            assert init_skill_mod.validate_skill_name(name) is None

    @pytest.mark.parametrize(
        "name",
        ["", "MySkill", "my_skill", "-leading", "trailing-", "double--hyphen", "a" * 65],
    )
    def test_invalid_names(self, init_skill_mod, name):
        assert init_skill_mod.validate_skill_name(name) is not None


class TestInitSkill:
    def test_creates_expected_structure(self, init_skill_mod, tmp_path):
        result = init_skill_mod.init_skill("my-new-skill", tmp_path)
        assert result == tmp_path / "my-new-skill"
        assert (result / "SKILL.md").exists()
        assert (result / "scripts" / "example.py").exists()
        assert (result / "references" / "api_reference.md").exists()
        assert (result / "templates" / "example_template.txt").exists()

        content = (result / "SKILL.md").read_text()
        assert content.startswith("---\nname: my-new-skill\n")
        assert "My New Skill" in content

    def test_rejects_invalid_name(self, init_skill_mod, tmp_path):
        assert init_skill_mod.init_skill("Invalid_Name", tmp_path) is None
        assert not (tmp_path / "Invalid_Name").exists()

    def test_refuses_to_overwrite_existing_dir(self, init_skill_mod, tmp_path):
        existing = tmp_path / "already-exists"
        existing.mkdir()
        assert init_skill_mod.init_skill("already-exists", tmp_path) is None


class TestQuickValidate:
    def _write_skill(self, tmp_path, name, frontmatter_extra="", body="Some content.\n"):
        skill_dir = tmp_path / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: does something useful{frontmatter_extra}\n---\n\n{body}"
        )
        return skill_dir

    def test_valid_skill_passes(self, quick_validate_mod, tmp_path):
        skill_dir = self._write_skill(tmp_path, "good-skill")
        ok, messages = quick_validate_mod.validate_skill(skill_dir)
        assert ok is True
        assert any("valid" in m.lower() for m in messages)

    def test_missing_skill_md(self, quick_validate_mod, tmp_path):
        skill_dir = tmp_path / "no-skill-md"
        skill_dir.mkdir()
        ok, messages = quick_validate_mod.validate_skill(skill_dir)
        assert ok is False
        assert any("SKILL.md not found" in m for m in messages)

    def test_empty_name_rejected(self, quick_validate_mod, tmp_path):
        skill_dir = tmp_path / "empty-name"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: \ndescription: something\n---\n\nBody\n"
        )
        ok, messages = quick_validate_mod.validate_skill(skill_dir)
        assert ok is False
        assert any("Name cannot be empty" in m for m in messages)

    def test_empty_description_rejected(self, quick_validate_mod, tmp_path):
        skill_dir = tmp_path / "empty-description"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: empty-description\ndescription: \n---\n\nBody\n"
        )
        ok, messages = quick_validate_mod.validate_skill(skill_dir)
        assert ok is False
        assert any("Description cannot be empty" in m for m in messages)

    def test_name_mismatch_warns_but_does_not_fail(self, quick_validate_mod, tmp_path):
        skill_dir = tmp_path / "actual-dir-name"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: different-name\ndescription: something\n---\n\nBody\n"
        )
        ok, messages = quick_validate_mod.validate_skill(skill_dir)
        assert ok is True
        assert any("does not match directory name" in m for m in messages)

    def test_unexpected_frontmatter_key_rejected(self, quick_validate_mod, tmp_path):
        skill_dir = tmp_path / "bad-key"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: bad-key\ndescription: something\nauthor: someone\n---\n\nBody\n"
        )
        ok, messages = quick_validate_mod.validate_skill(skill_dir)
        assert ok is False
        assert any("Unexpected key" in m for m in messages)

    def test_angle_brackets_in_description_rejected(self, quick_validate_mod, tmp_path):
        skill_dir = tmp_path / "angle-brackets"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: angle-brackets\ndescription: uses <tag> syntax\n---\n\nBody\n"
        )
        ok, messages = quick_validate_mod.validate_skill(skill_dir)
        assert ok is False
        assert any("angle brackets" in m for m in messages)

    def test_long_body_warns(self, quick_validate_mod, tmp_path):
        long_body = "\n".join(f"line {i}" for i in range(600))
        skill_dir = self._write_skill(tmp_path, "long-skill", body=long_body)
        ok, messages = quick_validate_mod.validate_skill(skill_dir)
        assert ok is True
        assert any("recommended max" in m for m in messages)

    def test_resolve_skill_path_by_name_uses_base(self, quick_validate_mod, tmp_path):
        resolved = quick_validate_mod.resolve_skill_path("some-skill", tmp_path)
        assert resolved == tmp_path / "some-skill"

    def test_resolve_skill_path_absolute_passthrough(self, quick_validate_mod, tmp_path):
        abs_path = tmp_path / "abs-skill"
        resolved = quick_validate_mod.resolve_skill_path(str(abs_path), tmp_path / "other-base")
        assert resolved == abs_path
