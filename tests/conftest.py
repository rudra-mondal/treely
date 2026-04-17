"""
tests/conftest.py
~~~~~~~~~~~~~~~~~
Shared pytest fixtures: reusable temporary directory structures for tests.
"""
from __future__ import annotations

import pytest
from pathlib import Path


@pytest.fixture
def simple_project(tmp_path: Path) -> Path:
    """
    A minimal project layout::

        my_project/
        ├── src/
        │   ├── main.py
        │   └── utils.py
        ├── tests/
        │   └── test_main.py
        ├── .gitignore
        ├── README.md
        └── dist/            ← ignored by .gitignore
            └── package.whl  ← binary
    """
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def main():\n    print('hello')\n")
    (tmp_path / "src" / "utils.py").write_text("def helper():\n    pass\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_main(): assert True\n")
    (tmp_path / "README.md").write_text("# My Project\n")
    (tmp_path / ".gitignore").write_text("*.pyc\n__pycache__/\ndist/\n*.whl\n")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "package.whl").write_bytes(b"\x00\x01binary\x00\x02data")
    return tmp_path


@pytest.fixture
def nested_gitignore_project(tmp_path: Path) -> Path:
    """
    A project with nested .gitignore files::

        project/
        ├── .gitignore        ← ignores *.log
        ├── included.py
        ├── root.log          ← ignored by root .gitignore
        └── subdir/
            ├── .gitignore    ← ignores *.tmp
            ├── code.py
            ├── sub.tmp       ← ignored by subdir .gitignore
            └── sub.log       ← NOT ignored (root rule is *.log relative to root)
    """
    (tmp_path / ".gitignore").write_text("*.log\n")
    (tmp_path / "included.py").write_text("x = 1\n")
    (tmp_path / "root.log").write_text("log entry\n")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / ".gitignore").write_text("*.tmp\n")
    (tmp_path / "subdir" / "code.py").write_text("y = 2\n")
    (tmp_path / "subdir" / "sub.tmp").write_text("temp file\n")
    return tmp_path


@pytest.fixture
def binary_project(tmp_path: Path) -> Path:
    """Project containing binary files that should be skipped from code output."""
    (tmp_path / "script.py").write_text("print('hi')\n")
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00binary")
    (tmp_path / "data.bin").write_bytes(b"\x00\x01\x02\x03binary")
    return tmp_path


@pytest.fixture
def deep_project(tmp_path: Path) -> Path:
    """Three-level deep project for depth-limiting tests."""
    for d1 in ("a", "b"):
        (tmp_path / d1).mkdir()
        (tmp_path / d1 / "file.txt").write_text("content")
        for d2 in ("x", "y"):
            (tmp_path / d1 / d2).mkdir()
            (tmp_path / d1 / d2 / "deep.py").write_text("deep = True")
    return tmp_path


@pytest.fixture
def symlink_project(tmp_path: Path) -> Path:
    """Project with a symbolic link."""
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    (real_dir / "file.py").write_text("x = 1")
    link = tmp_path / "link_to_real"
    link.symlink_to(real_dir)
    (tmp_path / "main.py").write_text("import x")
    return tmp_path
