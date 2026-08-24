"""
tests/test_size_options.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprehensive unit and integration tests for --show-size, --show-file-size,
--show-folder-size, and their interactions with depth limits, filters, and formats.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from treely.config import TreeConfig
from treely.main import main
from treely.renderer import Renderer
from treely.walker import walk


def run_main(args: list[str], capsys) -> tuple[str, str, int]:
    with patch.object(sys, "argv", ["treely"] + args):
        try:
            main()
            exit_code = 0
        except SystemExit as exc:
            exit_code = exc.code if isinstance(exc.code, int) else 0
    captured = capsys.readouterr()
    return captured.out, captured.err, exit_code


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def multi_level_project(tmp_path: Path) -> Path:
    """
    Detailed multi-level structure::
        root/
        ├── dir_a/ (150 B)
        │   ├── sub_a1/ (100 B)
        │   │   └── deep.txt (100 B)
        │   └── file_a.txt (50 B)
        ├── dir_b/ (200 B)
        │   └── sub_b1/ (200 B)
        │       └── sub_b2/ (200 B)
        │           └── file_b.py (200 B)
        ├── empty_dir/ (0 B)
        ├── root_file.md (30 B)
        └── .hidden_dir/ (40 B)
            └── hidden.txt (40 B)
    """
    root = tmp_path / "multi_level"
    root.mkdir()

    # dir_a
    (root / "dir_a").mkdir()
    (root / "dir_a" / "file_a.txt").write_bytes(b"a" * 50)
    (root / "dir_a" / "sub_a1").mkdir()
    (root / "dir_a" / "sub_a1" / "deep.txt").write_bytes(b"d" * 100)

    # dir_b
    (root / "dir_b").mkdir()
    (root / "dir_b" / "sub_b1").mkdir()
    (root / "dir_b" / "sub_b1" / "sub_b2").mkdir()
    (root / "dir_b" / "sub_b1" / "sub_b2" / "file_b.py").write_bytes(b"b" * 200)

    # empty_dir
    (root / "empty_dir").mkdir()

    # root_file
    (root / "root_file.md").write_bytes(b"r" * 30)

    # .hidden_dir
    (root / ".hidden_dir").mkdir()
    (root / ".hidden_dir" / "hidden.txt").write_bytes(b"h" * 40)

    return root


# ── TreeConfig helper tests ───────────────────────────────────────────────────


class TestTreeConfigSizeHelpers:
    def test_default_all_false(self):
        cfg = TreeConfig()
        assert cfg.should_show_file_size() is False
        assert cfg.should_show_folder_size() is False

    def test_show_size_enables_both(self):
        cfg = TreeConfig(show_size=True)
        assert cfg.should_show_file_size() is True
        assert cfg.should_show_folder_size() is True

    def test_show_file_size_only_files(self):
        cfg = TreeConfig(show_file_size=True)
        assert cfg.should_show_file_size() is True
        assert cfg.should_show_folder_size() is False

    def test_show_folder_size_only_folders(self):
        cfg = TreeConfig(show_folder_size=True)
        assert cfg.should_show_file_size() is False
        assert cfg.should_show_folder_size() is True

    def test_both_flags_enabled(self):
        cfg = TreeConfig(show_file_size=True, show_folder_size=True)
        assert cfg.should_show_file_size() is True
        assert cfg.should_show_folder_size() is True


# ── Multi-level directory sizing tests ────────────────────────────────────────


class TestMultiLevelDirectorySizing:
    def test_unlimited_depth_sizes(self, multi_level_project):
        cfg = TreeConfig(root_path=str(multi_level_project), show_size=True)
        result = walk(multi_level_project, cfg, {})

        # Check nodes
        children = {c.name: c for c in result.root.children}
        assert children["dir_a"].size == 150
        assert children["dir_b"].size == 200
        assert children["empty_dir"].size == 0
        assert children["root_file.md"].size == 30

        # Sub nodes
        sub_a1 = next(c for c in children["dir_a"].children if c.name == "sub_a1")
        assert sub_a1.size == 100

        # Total root size (excluding hidden dir because all=False)
        assert result.root.size == 150 + 200 + 0 + 30

    def test_unlimited_depth_with_all_flag(self, multi_level_project):
        cfg = TreeConfig(root_path=str(multi_level_project), show_size=True, all=True)
        result = walk(multi_level_project, cfg, {})
        children = {c.name: c for c in result.root.children}
        assert ".hidden_dir" in children
        assert children[".hidden_dir"].size == 40
        assert result.root.size == 150 + 200 + 0 + 30 + 40

    def test_level_1_computes_exact_folder_sizes(self, multi_level_project):
        cfg = TreeConfig(root_path=str(multi_level_project), level=1, show_size=True)
        result = walk(multi_level_project, cfg, {})

        children = {c.name: c for c in result.root.children}
        # Check that children are NOT expanded
        assert len(children["dir_a"].children) == 0
        assert len(children["dir_b"].children) == 0

        # Check that exact recursive sizes are computed
        assert children["dir_a"].size == 150
        assert children["dir_b"].size == 200
        assert children["empty_dir"].size == 0
        assert children["root_file.md"].size == 30
        assert result.root.size == 380

    def test_level_2_computes_subfolder_sizes(self, multi_level_project):
        cfg = TreeConfig(root_path=str(multi_level_project), level=2, show_size=True)
        result = walk(multi_level_project, cfg, {})

        children = {c.name: c for c in result.root.children}
        assert children["dir_a"].size == 150
        sub_a1 = next(c for c in children["dir_a"].children if c.name == "sub_a1")
        assert sub_a1.size == 100
        # sub_b1 is at depth 2; its children should be empty due to level=2, but its size is 200
        sub_b1 = next(c for c in children["dir_b"].children if c.name == "sub_b1")
        assert len(sub_b1.children) == 0
        assert sub_b1.size == 200


# ── Renderer tests with various flags ─────────────────────────────────────────


class TestRendererDisplayModes:
    def test_show_size_renders_all_badges(self, multi_level_project):
        cfg = TreeConfig(root_path=str(multi_level_project), show_size=True, level=1)
        result = walk(multi_level_project, cfg, {})
        renderer = Renderer(cfg)
        text = renderer.to_string(result)
        lines = [line.strip() for line in text.splitlines()]

        dir_a_line = next(line for line in lines if "dir_a/" in line)
        root_file_line = next(line for line in lines if "root_file.md" in line)

        assert "150.0B" in dir_a_line
        assert "30.0B" in root_file_line

    def test_show_file_size_only_renders_file_badges(self, multi_level_project):
        cfg = TreeConfig(root_path=str(multi_level_project), show_file_size=True, level=1)
        result = walk(multi_level_project, cfg, {})
        renderer = Renderer(cfg)
        text = renderer.to_string(result)
        lines = [line.strip() for line in text.splitlines()]

        dir_a_line = next(line for line in lines if "dir_a/" in line)
        root_file_line = next(line for line in lines if "root_file.md" in line)

        assert "[" not in dir_a_line
        assert "30.0B" in root_file_line

    def test_show_folder_size_only_renders_folder_badges(self, multi_level_project):
        cfg = TreeConfig(root_path=str(multi_level_project), show_folder_size=True, level=1)
        result = walk(multi_level_project, cfg, {})
        renderer = Renderer(cfg)
        text = renderer.to_string(result)
        lines = [line.strip() for line in text.splitlines()]

        dir_a_line = next(line for line in lines if "dir_a/" in line)
        empty_dir_line = next(line for line in lines if "empty_dir/" in line)
        root_file_line = next(line for line in lines if "root_file.md" in line)

        assert "150.0B" in dir_a_line
        assert "0.0B" in empty_dir_line
        assert "[" not in root_file_line

    def test_json_output_with_folder_and_file_sizes(self, multi_level_project):
        cfg = TreeConfig(root_path=str(multi_level_project), format="json")
        result = walk(multi_level_project, cfg, {})
        renderer = Renderer(cfg)
        data = json.loads(renderer.to_json(result))

        assert data["type"] == "directory"
        assert data["size_bytes"] == 380
        assert data["size_human"] == "380.0B"

        child_map = {c["name"]: c for c in data["children"]}
        assert child_map["dir_a"]["size_bytes"] == 150
        assert child_map["dir_b"]["size_bytes"] == 200
        assert child_map["empty_dir"]["size_bytes"] == 0
        assert child_map["root_file.md"]["size_bytes"] == 30


# ── CLI End-to-End Tests ──────────────────────────────────────────────────────


class TestCLIEndToEndSizeFlags:
    def test_cli_show_size_with_summary_and_level_1(self, multi_level_project, capsys):
        out, err, code = run_main(
            [
                str(multi_level_project),
                "-L",
                "1",
                "-a",
                "--show-size",
                "-s",
                "--no-banner",
                "--no-color",
            ],
            capsys,
        )
        assert code == 0
        assert err == ""
        # Check lines
        lines = [line.strip() for line in out.splitlines()]
        dir_a = next(line for line in lines if "dir_a/" in line)
        dir_b = next(line for line in lines if "dir_b/" in line)
        empty_dir = next(line for line in lines if "empty_dir/" in line)
        hidden_dir = next(line for line in lines if ".hidden_dir/" in line)
        root_file = next(line for line in lines if "root_file.md" in line)

        assert "150.0B" in dir_a
        assert "200.0B" in dir_b
        assert "0.0B" in empty_dir
        assert "40.0B" in hidden_dir
        assert "30.0B" in root_file
        assert "directories" in out and "files" in out

    def test_cli_show_file_size(self, multi_level_project, capsys):
        out, err, code = run_main(
            [str(multi_level_project), "-L", "1", "--show-file-size", "--no-banner", "--no-color"],
            capsys,
        )
        assert code == 0
        lines = [line.strip() for line in out.splitlines()]
        dir_a = next(line for line in lines if "dir_a/" in line)
        root_file = next(line for line in lines if "root_file.md" in line)

        assert "[" not in dir_a
        assert "30.0B" in root_file

    def test_cli_show_folder_size(self, multi_level_project, capsys):
        out, err, code = run_main(
            [
                str(multi_level_project),
                "-L",
                "1",
                "--show-folder-size",
                "--no-banner",
                "--no-color",
            ],
            capsys,
        )
        assert code == 0
        lines = [line.strip() for line in out.splitlines()]
        dir_a = next(line for line in lines if "dir_a/" in line)
        root_file = next(line for line in lines if "root_file.md" in line)

        assert "150.0B" in dir_a
        assert "[" not in root_file

    def test_cli_both_flags_simultaneously(self, multi_level_project, capsys):
        out, err, code = run_main(
            [
                str(multi_level_project),
                "-L",
                "1",
                "--show-file-size",
                "--show-folder-size",
                "--no-banner",
                "--no-color",
            ],
            capsys,
        )
        assert code == 0
        lines = [line.strip() for line in out.splitlines()]
        dir_a = next(line for line in lines if "dir_a/" in line)
        root_file = next(line for line in lines if "root_file.md" in line)

        assert "150.0B" in dir_a
        assert "30.0B" in root_file

    def test_cli_pattern_filter_affects_dir_size(self, multi_level_project, capsys):
        # Filter for *.py only -> dir_a has no .py files (0 B), dir_b has file_b.py (200 B)
        out, err, code = run_main(
            [
                str(multi_level_project),
                "-L",
                "1",
                "--pattern",
                "*.py",
                "--show-folder-size",
                "--no-banner",
                "--no-color",
            ],
            capsys,
        )
        assert code == 0
        lines = [line.strip() for line in out.splitlines()]
        dir_a = next(line for line in lines if "dir_a/" in line)
        dir_b = next(line for line in lines if "dir_b/" in line)

        assert "0.0B" in dir_a
        assert "200.0B" in dir_b
