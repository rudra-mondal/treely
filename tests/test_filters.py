"""
tests/test_filters.py
~~~~~~~~~~~~~~~~~~~~~
Unit tests for treely.filters: code detection, binary detection, size
parsing, pattern matching, and the GitignoreStack.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from treely.filters import (
    GitignoreStack,
    is_binary_file,
    is_code_file,
    load_root_gitignore,
    matches_any,
    matches_path_any,
    parse_size,
)


# ── parse_size ────────────────────────────────────────────────────────────────

class TestParseSize:
    def test_integer_only(self):
        assert parse_size("1024") == 1024

    def test_bytes(self):
        assert parse_size("512B") == 512

    def test_kilobytes(self):
        assert parse_size("1K") == 1024

    def test_megabytes(self):
        assert parse_size("2M") == 2 * 1024 ** 2

    def test_gigabytes(self):
        assert parse_size("1G") == 1024 ** 3

    def test_float_megabytes(self):
        assert parse_size("1.5M") == int(1.5 * 1024 ** 2)

    def test_lowercase(self):
        assert parse_size("2m") == 2 * 1024 ** 2

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_size("not_a_size")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse_size("M")


# ── is_code_file ──────────────────────────────────────────────────────────────

class TestIsCodeFile:
    def test_python(self):
        assert is_code_file("main.py", ".py") is True

    def test_javascript(self):
        assert is_code_file("app.js", ".js") is True

    def test_makefile_no_extension(self):
        assert is_code_file("Makefile", "") is True

    def test_dockerfile_no_extension(self):
        assert is_code_file("Dockerfile", "") is True

    def test_gitignore_dotfile(self):
        assert is_code_file(".gitignore", "") is True

    def test_image_not_code(self):
        assert is_code_file("photo.png", ".png") is False

    def test_binary_not_code(self):
        assert is_code_file("archive.zip", ".zip") is False

    def test_env_file(self):
        assert is_code_file(".env", ".env") is True

    def test_rust(self):
        assert is_code_file("lib.rs", ".rs") is True

    def test_go(self):
        assert is_code_file("main.go", ".go") is True


# ── is_binary_file ────────────────────────────────────────────────────────────

class TestIsBinaryFile:
    def test_detects_null_bytes(self, tmp_path):
        p = tmp_path / "binary.bin"
        p.write_bytes(b"\x00\x01\x02\x03")
        assert is_binary_file(p) is True

    def test_text_file_not_binary(self, tmp_path):
        p = tmp_path / "code.py"
        p.write_text("print('hello')\n")
        assert is_binary_file(p) is False

    def test_missing_file_returns_false(self, tmp_path):
        p = tmp_path / "nonexistent.txt"
        assert is_binary_file(p) is False

    def test_empty_file_not_binary(self, tmp_path):
        p = tmp_path / "empty.txt"
        p.write_bytes(b"")
        assert is_binary_file(p) is False


# ── matches_any / matches_path_any ────────────────────────────────────────────

class TestPatternMatching:
    def test_matches_glob(self):
        assert matches_any("file.log", ["*.log"]) is True

    def test_no_match(self):
        assert matches_any("file.py", ["*.log"]) is False

    def test_multiple_patterns(self):
        assert matches_any("file.log", ["*.py", "*.log"]) is True

    def test_path_pattern_with_dir(self):
        assert matches_path_any("lib/CSInterface.js", ["lib/*"]) is True

    def test_path_pattern_no_match(self):
        assert matches_path_any("src/main.py", ["lib/*"]) is False

    def test_basename_pattern(self):
        assert matches_path_any("deep/nested/file.log", ["*.log"]) is True


# ── GitignoreStack ────────────────────────────────────────────────────────────

class TestGitignoreStack:
    def test_root_gitignore_ignores_file(self, tmp_path):
        gi = tmp_path / ".gitignore"
        gi.write_text("*.log\n")
        stack = GitignoreStack()
        stack.push("", gi)
        assert stack.matches("error.log") is True
        assert stack.matches("main.py") is False

    def test_root_gitignore_ignores_directory(self, tmp_path):
        gi = tmp_path / ".gitignore"
        gi.write_text("dist/\n")
        stack = GitignoreStack()
        stack.push("", gi)
        assert stack.matches("dist/") is True
        assert stack.matches("dist/package.js") is True

    def test_nested_gitignore_applies_only_within_dir(self, tmp_path):
        root_gi = tmp_path / ".gitignore"
        root_gi.write_text("*.log\n")
        sub_dir = tmp_path / "subdir"
        sub_dir.mkdir()
        sub_gi = sub_dir / ".gitignore"
        sub_gi.write_text("*.tmp\n")

        stack = GitignoreStack()
        stack.push("", root_gi)
        child = stack.child()
        child.push("subdir", sub_gi)

        # Root rule applies everywhere
        assert child.matches("root.log") is True
        # Subdir rule applies inside subdir
        assert child.matches("subdir/file.tmp") is True
        # Subdir rule does NOT apply at root
        assert child.matches("file.tmp") is False

    def test_child_inherits_parent_specs(self, tmp_path):
        gi = tmp_path / ".gitignore"
        gi.write_text("*.pyc\n")
        stack = GitignoreStack()
        stack.push("", gi)
        child = stack.child()
        assert child.matches("module.pyc") is True

    def test_load_root_gitignore(self, tmp_path):
        (tmp_path / ".gitignore").write_text("node_modules/\n*.log\n")
        stack = load_root_gitignore(tmp_path)
        assert stack.matches("node_modules/") is True
        assert stack.matches("error.log") is True
        assert stack.matches("main.py") is False

    def test_load_root_gitignore_missing_file(self, tmp_path):
        # Should not raise even if .gitignore doesn't exist
        stack = load_root_gitignore(tmp_path)
        assert stack.matches("anything.log") is False
