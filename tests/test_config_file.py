"""
tests/test_config_file.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Tests for treely.config_file: TOML loading, defaults application, and profile
system.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from treely.config import TreeConfig
from treely.config_file import (
    apply_config_file,
    find_config_file,
    list_profiles,
    load_config_file,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_toml(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


_SAMPLE_TOML = """\
[defaults]
use_gitignore = true
show_size = true
theme = "dark"
no_banner = true

[profiles.llm]
code = true
copy = false
no_banner = true
use_gitignore = true
exclude = "*.lock|dist/*"
token_count = true

[profiles.docs]
format = "markdown"
summary = true
show_size = true
"""


# ── find_config_file ──────────────────────────────────────────────────────────

class TestFindConfigFile:
    def test_explicit_path_found(self, tmp_path):
        cfg = tmp_path / "my.toml"
        _write_toml(cfg, "[defaults]\n")
        result = find_config_file(str(cfg))
        assert result == cfg

    def test_explicit_path_missing_returns_none(self, tmp_path):
        result = find_config_file(str(tmp_path / "nonexistent.toml"))
        assert result is None

    def test_none_when_no_config_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # No treely.toml / .treely.toml in tmp_path
        result = find_config_file(None)
        # May or may not find a global config; just ensure no crash
        assert result is None or result.is_file()

    def test_finds_treely_toml_in_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = tmp_path / "treely.toml"
        _write_toml(cfg, "[defaults]\n")
        result = find_config_file(None)
        assert result == cfg

    def test_finds_dot_treely_toml_in_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = tmp_path / ".treely.toml"
        _write_toml(cfg, "[defaults]\n")
        result = find_config_file(None)
        assert result == cfg


# ── load_config_file ──────────────────────────────────────────────────────────

@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="tomllib built-in only on Python 3.11+ (use tomli for older versions)",
)
class TestLoadConfigFile:
    def test_loads_valid_toml(self, tmp_path):
        cfg = tmp_path / "treely.toml"
        _write_toml(cfg, _SAMPLE_TOML)
        data = load_config_file(cfg)
        assert "defaults" in data
        assert data["defaults"]["use_gitignore"] is True

    def test_loads_profiles_section(self, tmp_path):
        cfg = tmp_path / "treely.toml"
        _write_toml(cfg, _SAMPLE_TOML)
        data = load_config_file(cfg)
        assert "profiles" in data
        assert "llm" in data["profiles"]
        assert "docs" in data["profiles"]

    def test_returns_empty_on_invalid_toml(self, tmp_path):
        cfg = tmp_path / "bad.toml"
        cfg.write_text("not valid toml }{{\n")
        data = load_config_file(cfg)
        assert data == {}

    def test_returns_empty_on_missing_file(self, tmp_path):
        data = load_config_file(tmp_path / "missing.toml")
        assert data == {}


# ── apply_config_file ─────────────────────────────────────────────────────────

class TestApplyConfigFile:
    def _make_data(self):
        """Simulate parsed TOML data."""
        return {
            "defaults": {
                "use_gitignore": True,
                "show_size": True,
                "theme": "dark",
                "no_banner": True,
            },
            "profiles": {
                "llm": {
                    "code": True,
                    "token_count": True,
                    "use_gitignore": True,
                    "exclude": "*.lock|dist/*",
                },
                "docs": {
                    "format": "markdown",
                    "summary": True,
                },
            },
        }

    def test_defaults_applied(self):
        config = TreeConfig()
        data = self._make_data()
        config = apply_config_file(config, data)
        assert config.use_gitignore is True
        assert config.show_size is True
        assert config.theme == "dark"
        assert config.no_banner is True

    def test_profile_overrides_defaults(self):
        config = TreeConfig()
        data = self._make_data()
        config = apply_config_file(config, data, profile="docs")
        assert config.format == "markdown"
        assert config.summary is True
        assert config.show_size is True  # from defaults

    def test_llm_profile(self):
        config = TreeConfig()
        data = self._make_data()
        config = apply_config_file(config, data, profile="llm")
        assert config.code is True
        assert config.token_count is True
        assert config.exclude == "*.lock|dist/*"

    def test_unknown_profile_does_not_crash(self, capsys):
        config = TreeConfig()
        data = self._make_data()
        apply_config_file(config, data, profile="nonexistent")
        captured = capsys.readouterr()
        assert "Warning" in captured.err

    def test_empty_file_data_returns_unchanged(self):
        config = TreeConfig()
        original_theme = config.theme
        config = apply_config_file(config, {})
        assert config.theme == original_theme

    def test_dash_normalised_to_underscore(self):
        config = TreeConfig()
        data = {"defaults": {"no-banner": True, "show-size": True}}
        config = apply_config_file(config, data)
        assert config.no_banner is True
        assert config.show_size is True


# ── list_profiles ─────────────────────────────────────────────────────────────

class TestListProfiles:
    def test_returns_profile_names(self):
        data = {"profiles": {"a": {}, "b": {}, "c": {}}}
        assert set(list_profiles(data)) == {"a", "b", "c"}

    def test_empty_when_no_profiles(self):
        assert list_profiles({}) == []

    def test_empty_when_no_profiles_key(self):
        assert list_profiles({"defaults": {}}) == []

# ── Import behaviour ──────────────────────────────────────────────────────────

class TestTomlImport:
    def test_has_toml_flag_set_correctly(self):
        from treely.config_file import _HAS_TOML
        assert _HAS_TOML is True
