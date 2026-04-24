"""
treely.tree_node
~~~~~~~~~~~~~~~~
Pure data structures representing the directory tree. No I/O, no rendering.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TreeNode:
    """A single filesystem entry (file or directory) in the directory tree."""

    name: str
    path: Path
    is_dir: bool

    # Populated during walking
    children: list[TreeNode] = field(default_factory=list, repr=False)
    size: int | None = None          # bytes; None for dirs or on error
    is_symlink: bool = False
    symlink_target: str | None = None
    git_status: str | None = None    # 'M', 'A', '?', 'D', '!'
    is_binary: bool = False
    extension: str = ""                 # lower-case, e.g. ".py"
    error: str | None = None        # e.g. "[Permission Denied]"

    # ------------------------------------------------------------------ helpers

    @property
    def is_hidden(self) -> bool:
        """True if the entry name starts with a dot."""
        return self.name.startswith(".")

    @property
    def is_special(self) -> bool:
        """True for well-known config/infra files that get highlight treatment."""
        _SPECIAL = {
            ".env", ".env.local", ".env.example",
            ".gitignore", ".gitattributes", ".dockerignore",
            "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
            "Makefile", "makefile", "GNUmakefile",
            "pyproject.toml", "package.json", "Cargo.toml", "go.mod",
        }
        return self.name in _SPECIAL

    @property
    def display_name(self) -> str:
        """Name with trailing slash appended for directories."""
        return self.name + "/" if self.is_dir else self.name


@dataclass
class WalkStats:
    """Counters accumulated during directory traversal."""

    dirs: int = 0
    files: int = 0
    total_bytes: int = 0


@dataclass
class WalkResult:
    """Everything returned by a single walk() call."""

    root: TreeNode
    code_files: list[Path]
    stats: WalkStats
