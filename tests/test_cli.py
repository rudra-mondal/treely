"""
tests/test_cli.py
~~~~~~~~~~~~~~~~~
End-to-end / integration tests for the treely CLI entry point.
Uses ``argparse``-level invocation via ``main()`` with ``sys.argv`` patching
(faster and more reliable than subprocess for most cases).

A small number of tests use subprocess to verify the installed entry point.
"""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from treely import __version__
from treely.main import main


# ── Helper ────────────────────────────────────────────────────────────────────

def run_main(args: list[str], capsys) -> tuple[str, str, int]:
    """
    Run ``main()`` with *args* and return ``(stdout, stderr, exit_code)``.
    Handles SystemExit correctly.
    """
    with patch.object(sys, "argv", ["treely"] + args):
        try:
            main()
            exit_code = 0
        except SystemExit as exc:
            exit_code = exc.code if isinstance(exc.code, int) else 0
    captured = capsys.readouterr()
    return captured.out, captured.err, exit_code


# ── --version ─────────────────────────────────────────────────────────────────

class TestVersion:
    def test_version_exits_zero(self, capsys):
        _, _, code = run_main(["--version"], capsys)
        assert code == 0

    def test_version_string_present(self, capsys):
        out, err, _ = run_main(["--version"], capsys)
        combined = out + err
        assert __version__ in combined


# ── Basic tree ────────────────────────────────────────────────────────────────

class TestBasicTree:
    def test_runs_on_valid_dir(self, simple_project, capsys):
        _, err, code = run_main(
            [str(simple_project), "--no-banner", "--no-color"], capsys
        )
        assert code == 0
        assert err == ""

    def test_output_contains_project_name(self, simple_project, capsys):
        out, _, _ = run_main(
            [str(simple_project), "--no-banner", "--no-color"], capsys
        )
        assert simple_project.name in out

    def test_output_contains_src_dir(self, simple_project, capsys):
        out, _, _ = run_main(
            [str(simple_project), "--no-banner", "--no-color"], capsys
        )
        assert "src" in out

    def test_output_contains_readme(self, simple_project, capsys):
        out, _, _ = run_main(
            [str(simple_project), "--no-banner", "--no-color"], capsys
        )
        assert "README.md" in out


# ── Error handling ────────────────────────────────────────────────────────────

class TestErrorHandling:
    def test_invalid_dir_exits_nonzero(self, capsys):
        _, err, code = run_main(
            ["/absolutely/nonexistent/path/xyz", "--no-banner"], capsys
        )
        assert code != 0
        assert "Error" in err or "does not exist" in err

    def test_file_instead_of_dir_exits_nonzero(self, tmp_path, capsys):
        f = tmp_path / "file.txt"
        f.write_text("content")
        _, err, code = run_main([str(f), "--no-banner"], capsys)
        assert code != 0

    def test_exclude_without_code_is_error(self, simple_project, capsys):
        _, err, code = run_main(
            [str(simple_project), "--exclude", "*.log", "--no-banner"], capsys
        )
        assert code != 0

    def test_token_count_without_code_is_error(self, simple_project, capsys):
        _, err, code = run_main(
            [str(simple_project), "--token-count", "--no-banner"], capsys
        )
        assert code != 0

    def test_dirs_only_and_files_only_error(self, simple_project, capsys):
        _, err, code = run_main(
            [str(simple_project), "--dirs-only", "--files-only", "--no-banner"],
            capsys,
        )
        assert code != 0


# ── Filtering flags ───────────────────────────────────────────────────────────

class TestFilteringFlags:
    def test_level_limits_depth(self, deep_project, capsys):
        out, _, code = run_main(
            [str(deep_project), "--no-banner", "--no-color", "-L", "1"], capsys
        )
        assert code == 0
        # deep.py is at depth 2, should NOT appear
        assert "deep.py" not in out

    def test_dirs_only_hides_files(self, simple_project, capsys):
        out, _, code = run_main(
            [str(simple_project), "--no-banner", "--no-color", "--dirs-only"],
            capsys,
        )
        assert code == 0
        assert "README.md" not in out
        assert "src" in out

    def test_pattern_filters_files(self, simple_project, capsys):
        out, _, code = run_main(
            [str(simple_project), "--no-banner", "--no-color", "--pattern", "*.py"],
            capsys,
        )
        assert code == 0
        assert "README.md" not in out

    def test_summary_printed(self, simple_project, capsys):
        out, _, _ = run_main(
            [str(simple_project), "--no-banner", "--no-color", "-s"], capsys
        )
        assert "directories" in out and "files" in out

    def test_show_size_adds_badge(self, simple_project, capsys):
        out, _, _ = run_main(
            [str(simple_project), "--no-banner", "--no-color", "--show-size"],
            capsys,
        )
        assert any(sfx in out for sfx in ["B", "K", "M"])


# ── Output formats ────────────────────────────────────────────────────────────

class TestOutputFormats:
    def test_json_format_is_valid_json(self, simple_project, capsys):
        out, _, code = run_main(
            [str(simple_project), "--no-banner", "--format", "json"], capsys
        )
        assert code == 0
        data = json.loads(out)
        assert data["type"] == "directory"

    def test_markdown_format_has_fences(self, simple_project, capsys):
        out, _, code = run_main(
            [str(simple_project), "--no-banner", "--no-color", "--format", "markdown"],
            capsys,
        )
        assert code == 0
        assert "```" in out

    def test_text_format_default(self, simple_project, capsys):
        out, _, code = run_main(
            [str(simple_project), "--no-banner", "--no-color"], capsys
        )
        assert code == 0
        assert "├──" in out or "└──" in out


# ── Code output ───────────────────────────────────────────────────────────────

class TestCodeOutput:
    def test_code_flag_shows_content(self, simple_project, capsys):
        out, _, code = run_main(
            [str(simple_project), "--no-banner", "--no-color", "--code"],
            capsys,
        )
        assert code == 0
        assert "FILE CONTENTS" in out

    def test_exclude_removes_from_code(self, simple_project, capsys):
        out, _, code = run_main(
            [
                str(simple_project),
                "--no-banner",
                "--no-color",
                "--code",
                "--exclude",
                "src/*",
            ],
            capsys,
        )
        assert code == 0
        # main.py is in src/ — should not appear in code section
        # (tree still shows it, so check specifically that def main is absent
        # from the code section)
        assert "def main" not in out


# ── File output ───────────────────────────────────────────────────────────────

class TestFileOutput:
    def test_output_creates_file(self, simple_project, tmp_path, capsys):
        out_file = tmp_path / "output.txt"
        _, _, code = run_main(
            [str(simple_project), "--no-banner", "-o", str(out_file)],
            capsys,
        )
        assert code == 0
        assert out_file.exists()

    def test_output_file_contains_tree(self, simple_project, tmp_path, capsys):
        out_file = tmp_path / "output.txt"
        run_main(
            [str(simple_project), "--no-banner", "-o", str(out_file)],
            capsys,
        )
        content = out_file.read_text(encoding="utf-8")
        assert "src" in content
        assert "README.md" in content

    def test_output_file_has_no_ansi(self, simple_project, tmp_path, capsys):
        out_file = tmp_path / "output.txt"
        run_main(
            [str(simple_project), "--no-banner", "-o", str(out_file)],
            capsys,
        )
        content = out_file.read_text(encoding="utf-8")
        assert "\033[" not in content


# ── Theme flag ────────────────────────────────────────────────────────────────

class TestThemeFlag:
    @pytest.mark.parametrize("theme", ["default", "dark", "light", "minimal", "nord"])
    def test_theme_accepted(self, theme, simple_project, capsys):
        _, _, code = run_main(
            [str(simple_project), "--no-banner", "--no-color", "--theme", theme],
            capsys,
        )
        assert code == 0

# ── Config Precedence (B-1 Fix coverage) ──────────────────────────────────────

class TestConfigPrecedence:
    def test_file_theme_not_overridden_by_default(self, simple_project, tmp_path):
        config_file = tmp_path / "treely.toml"
        config_file.write_text('[defaults]\ntheme = "nord"')
        from treely.main import _build_config, _build_parser
        parser = _build_parser()
        args = parser.parse_args([str(simple_project), "--config", str(config_file)])
        config = _build_config(args)
        assert config.theme == "nord"

    def test_file_sort_not_overridden_by_default(self, simple_project, tmp_path):
        config_file = tmp_path / "treely.toml"
        config_file.write_text('[defaults]\nsort = "mtime"')
        from treely.main import _build_config, _build_parser
        parser = _build_parser()
        args = parser.parse_args([str(simple_project), "--config", str(config_file)])
        config = _build_config(args)
        assert config.sort == "mtime"

    def test_explicit_cli_flag_overrides_file(self, simple_project, tmp_path):
        config_file = tmp_path / "treely.toml"
        config_file.write_text('[defaults]\ntheme = "nord"')
        from treely.main import _build_config, _build_parser
        parser = _build_parser()
        args = parser.parse_args([str(simple_project), "--theme", "dark", "--config", str(config_file)])
        config = _build_config(args)
        assert config.theme == "dark"
