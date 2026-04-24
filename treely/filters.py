"""
treely.filters
~~~~~~~~~~~~~~
All filtering logic: code-file detection, binary-file heuristic, pattern
matching, size parsing, and a stacking gitignore resolver for nested
``.gitignore`` files.
"""
from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple

try:
    import pathspec  # type: ignore[import]
except ImportError:
    pathspec = None  # type: ignore[assignment]


# ── Code-file extension registry ─────────────────────────────────────────────

CODE_EXTENSIONS: Set[str] = {
    # Systems / compiled
    ".py", ".pyi",
    ".js", ".mjs", ".cjs",
    ".ts", ".mts",
    ".jsx", ".tsx",
    ".java",
    ".c", ".h",
    ".cpp", ".cc", ".cxx", ".hpp", ".hh",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".kt", ".kts",
    ".swift",
    ".m", ".mm",
    ".dart",
    ".scala",
    ".lua",
    ".pl", ".pm",
    ".r", ".R",
    ".jl",
    ".ex", ".exs",
    ".erl", ".hrl",
    ".clj", ".cljs", ".cljc",
    ".hs",
    ".elm",
    ".fs", ".fsx", ".fsi",
    ".ml", ".mli",
    ".nim",
    ".zig",
    ".v",
    # Shell / scripting
    ".sh", ".bash", ".zsh", ".fish",
    ".bat", ".cmd",
    ".ps1", ".psm1", ".psd1",
    # Web
    ".html", ".htm",
    ".css", ".scss", ".sass", ".less",
    ".svelte", ".vue", ".astro",
    # Data / config
    ".sql",
    ".xml",
    ".json", ".jsonc", ".json5",
    ".yaml", ".yml",
    ".toml",
    ".ini", ".cfg", ".conf",
    ".env",
    # Build
    ".make", ".mk",
    ".dockerfile",
    ".gradle",
    ".tf", ".hcl",
    # Docs
    ".md", ".mdx",
    ".rst",
    ".tex",
    # Misc
    ".proto",
    ".graphql", ".gql",
    ".tsbuildinfo",
    # dotfiles treated as code
    ".gitignore", ".gitattributes", ".dockerignore",
    ".editorconfig",
    ".debug",
}

# Extension-less filenames that are always treated as code
_CODE_NAMES: Set[str] = {
    "Makefile", "makefile", "GNUmakefile",
    "Dockerfile", "Containerfile",
    "Jenkinsfile", "Vagrantfile", "Procfile",
    "Gemfile", "Rakefile", "Guardfile",
    ".env", ".gitignore", ".gitattributes", ".dockerignore", ".editorconfig",
}

# Entries that are *always* hidden regardless of --all
ALWAYS_SKIP: Set[str] = {"__pycache__", ".DS_Store", "Thumbs.db", ".git"}


# ── Code-file detection ───────────────────────────────────────────────────────

def is_code_file(name: str, extension: str) -> bool:
    """
    Return ``True`` if a file should be included in ``--code`` output.
    Checks both the file extension and the file's base name.
    """
    if extension in CODE_EXTENSIONS:
        return True
    if name in _CODE_NAMES:
        return True
    # e.g. '.gitignore' as both name and pseudo-extension
    if not extension and f".{name.lower()}" in CODE_EXTENSIONS:
        return True
    return False


# ── Binary detection ─────────────────────────────────────────────────────────

def is_binary_file(path: Path, sample_bytes: int = 8192) -> bool:
    """
    Heuristic: read the first *sample_bytes* bytes; if a null byte is found
    the file is considered binary.  Returns ``False`` on any read error so we
    err on the side of inclusivity.
    """
    try:
        with open(path, "rb") as fh:
            chunk = fh.read(sample_bytes)
        if not chunk:
            return False

        # Allow standard UTF-16/32 text files (which intrinsically contain null bytes)
        # by checking for common Byte Order Marks to declare them as safe text blobs
        if chunk.startswith((b"\xff\xfe", b"\xfe\xff", b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
            return False

        return b"\x00" in chunk
    except OSError:
        return False


# ── Size parsing ──────────────────────────────────────────────────────────────

_SIZE_UNITS = {"B": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4}


def parse_size(size_str: str) -> int:
    """
    Parse a human-readable size string to bytes.

    Accepted formats: ``100``, ``1K``, ``1.5M``, ``2G`` (case-insensitive).
    Raises ``ValueError`` for invalid formats.
    """
    s = size_str.strip().upper()
    for suffix, multiplier in _SIZE_UNITS.items():
        if s.endswith(suffix):
            numeric = s[: -len(suffix)]
            try:
                return int(float(numeric) * multiplier)
            except ValueError:
                raise ValueError(f"Invalid size format: {size_str!r}") from None
    try:
        return int(s)
    except ValueError:
        raise ValueError(f"Invalid size format: {size_str!r}") from None


# ── Pattern matching ──────────────────────────────────────────────────────────

def matches_any(name: str, patterns: List[str]) -> bool:
    """Return ``True`` if *name* matches any of the glob *patterns*."""
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def matches_path_any(relative_path: str, patterns: List[str]) -> bool:
    """
    Return ``True`` if *relative_path* matches any of the glob *patterns*.
    Patterns can contain path separators (e.g. ``lib/*``).
    """
    for pat in patterns:
        if fnmatch.fnmatch(relative_path, pat):
            return True
        # Also try matching just the basename against the pattern
        if fnmatch.fnmatch(os.path.basename(relative_path), pat):
            return True
    return False


# ── Nested-gitignore resolver ─────────────────────────────────────────────────

class GitignoreStack:
    """
    Accumulates pathspec objects for every ``.gitignore`` encountered while
    recursively descending a directory tree.  Each spec is stored together
    with the *directory prefix* it governs (relative to the scan root).

    Usage::

        stack = GitignoreStack()
        # At root
        stack.push("", Path("/project/.gitignore"))
        # When descending into 'packages/'
        substack = stack.child()
        substack.push("packages", Path("/project/packages/.gitignore"))
        ignored = substack.matches("packages/lib/foo.js")
    """

    def __init__(self, specs: Optional[List[Tuple[str, Any]]] = None) -> None:
        self._specs: List[Tuple[str, Any]] = list(specs or [])

    # ------------------------------------------------------------------ public

    def push(self, dir_prefix: str, gitignore_path: Path) -> None:
        """Load a ``.gitignore`` file and register its spec for *dir_prefix*."""
        if pathspec is None:
            return
        try:
            with open(gitignore_path, encoding="utf-8", errors="ignore") as fh:
                spec = pathspec.PathSpec.from_lines("gitwildmatch", fh)
            self._specs.append((dir_prefix, spec))
        except OSError:
            pass

    def child(self) -> GitignoreStack:
        """Return a new stack that inherits the current specs (for recursion)."""
        return GitignoreStack(self._specs)

    def matches(self, relative_path: str) -> bool:
        """
        Return ``True`` if *relative_path* (relative to the scan root) is
        ignored by any spec in the stack.
        """
        for dir_prefix, spec in self._specs:
            if dir_prefix:
                # This spec only applies to paths inside its directory
                if not (
                    relative_path.startswith(dir_prefix + "/")
                    or relative_path == dir_prefix
                ):
                    continue
                local_path = relative_path[len(dir_prefix):].lstrip("/")
            else:
                local_path = relative_path

            if spec.match_file(local_path):
                return True
        return False


def load_root_gitignore(root: Path) -> GitignoreStack:
    """Create a ``GitignoreStack`` pre-loaded with the root ``.gitignore``."""
    stack = GitignoreStack()
    gi_path = root / ".gitignore"
    if gi_path.is_file():
        stack.push("", gi_path)
    return stack
