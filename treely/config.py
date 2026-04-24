"""
treely.config
~~~~~~~~~~~~~
Central configuration dataclass.  Every option the user can set lives here,
regardless of whether it came from a CLI flag, a config file, or a profile.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TreeConfig:
    """Holds all runtime configuration for a single treely invocation."""

    # ── Core ──────────────────────────────────────────────────────────────────
    root_path: str = "."

    # ── Tree display ──────────────────────────────────────────────────────────
    all: bool = False                   # show hidden files / dirs
    level: int = -1                     # max depth (-1 = unlimited)
    sort: str = "name"                  # name | size | mtime | ext
    dirs_only: bool = False
    files_only: bool = False
    full_path: bool = False             # print absolute paths
    follow_symlinks: bool = False       # recurse into symlinked directories
    show_size: bool = False
    summary: bool = False

    # ── Filtering ─────────────────────────────────────────────────────────────
    pattern: Optional[str] = None       # glob; applied to files only
    ignore: Optional[str] = None        # pipe-separated globs to hide from tree
    use_gitignore: bool = False

    # ── Code output ───────────────────────────────────────────────────────────
    code: bool = False
    exclude: Optional[str] = None       # pipe-separated globs; exclude from code
    max_size: Optional[str] = None      # e.g. "1M", "500K" — skip large files
    token_count: bool = False           # estimate LLM token count of code output

    # ── Git ───────────────────────────────────────────────────────────────────
    no_git: bool = False                # disable git status annotations

    # ── Rendering ─────────────────────────────────────────────────────────────
    theme: str = "default"
    no_color: bool = False
    no_banner: bool = False
    format: str = "text"               # text | json | markdown

    # ── Output ────────────────────────────────────────────────────────────────
    output: Optional[str] = None
    copy: bool = False

    # ── Config / profile (meta, not persisted in config file) ─────────────────
    profile: Optional[str] = None
    config_path: Optional[str] = None
