"""
treely.walker
~~~~~~~~~~~~~
Pure directory traversal.  Takes a ``TreeConfig`` and returns a ``WalkResult``
containing the root ``TreeNode`` tree, a list of code files to display, and
aggregate statistics.  No I/O other than reading the filesystem.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from .config import TreeConfig
from .filters import (
    ALWAYS_SKIP,
    GitignoreStack,
    is_binary_file,
    is_code_file,
    load_root_gitignore,
    matches_any,
    matches_path_any,
    parse_size,
    pathspec,
)
from .tree_node import TreeNode, WalkResult, WalkStats


# ── Sorting ───────────────────────────────────────────────────────────────────

def _sort_entries(entries: List[str], base: Path, sort: str) -> List[str]:
    """
    Split *entries* into dirs and files, sort each group according to *sort*,
    and return them concatenated (dirs always first).
    """
    dirs: List[str] = []
    files: List[str] = []
    for e in entries:
        (dirs if (base / e).is_dir() else files).append(e)

    if sort == "size":
        def _size(name: str) -> int:
            try:
                return (base / name).stat().st_size
            except OSError:
                return 0

        files.sort(key=_size, reverse=True)
        dirs.sort()

    elif sort == "mtime":
        def _mtime(name: str) -> float:
            try:
                return (base / name).stat().st_mtime
            except OSError:
                return 0.0

        dirs.sort(key=_mtime, reverse=True)
        files.sort(key=_mtime, reverse=True)

    elif sort == "ext":
        files.sort(key=lambda n: (os.path.splitext(n)[1].lower(), n.lower()))
        dirs.sort()

    else:  # "name" (default)
        dirs.sort(key=str.lower)
        files.sort(key=str.lower)

    return dirs + files


# ── Internal recursive walker ─────────────────────────────────────────────────

def _walk(
    path: Path,
    relative_path: str,
    depth: int,
    config: TreeConfig,
    gitignore_stack: GitignoreStack,
    git_status: Dict[str, str],
    ignore_patterns: List[str],
    exclude_patterns: List[str],
    max_size_bytes: Optional[int],
    stats: WalkStats,
    code_files: List[Path],
    parent_node: TreeNode,
) -> None:
    """Recursively populate *parent_node*.children."""

    if config.level != -1 and depth >= config.level:
        return

    # ── List directory ────────────────────────────────────────────────────────
    try:
        raw_entries = os.listdir(path)
    except PermissionError:
        err_node = TreeNode(
            name="[Permission Denied]",
            path=path,
            is_dir=False,
            error="permission",
        )
        parent_node.children.append(err_node)
        return

    # ── Filter entries ────────────────────────────────────────────────────────
    filtered: List[str] = []
    for entry in raw_entries:
        full = path / entry
        is_dir = os.path.isdir(str(full)) and not os.path.islink(str(full))

        # Always-skip set (e.g. __pycache__, .DS_Store) - unless --all
        if entry in ALWAYS_SKIP and not config.all:
            continue

        # Hidden items  (dirs starting with '.' are also hidden)
        if not config.all and entry.startswith("."):
            continue

        # --ignore patterns
        if ignore_patterns and matches_any(entry, ignore_patterns):
            continue

        # gitignore check (dirs get trailing slash added for spec matching)
        if config.use_gitignore and pathspec:
            rel = (relative_path + "/" + entry) if relative_path else entry
            check_path = rel + "/" if is_dir else rel
            if gitignore_stack.matches(check_path) or gitignore_stack.matches(rel):
                continue

        # --pattern applies to files only (always descend into directories)
        if config.pattern and not is_dir:
            import fnmatch as _fnm
            if not _fnm.fnmatch(entry, config.pattern):
                continue

        # --dirs-only / --files-only
        if config.dirs_only and not is_dir:
            continue
        if config.files_only and is_dir:
            continue

        filtered.append(entry)

    # ── Sort ──────────────────────────────────────────────────────────────────
    combined = _sort_entries(filtered, path, config.sort)

    # ── Build TreeNode children ───────────────────────────────────────────────
    for entry in combined:
        full = path / entry
        is_symlink = os.path.islink(str(full))
        is_dir = full.is_dir()
        ext = os.path.splitext(entry)[1].lower()
        rel_entry = (relative_path + "/" + entry) if relative_path else entry

        # Git status lookup
        git_stat: Optional[str] = git_status.get(rel_entry)
        # For directories, check if any child is dirty (use dir key if present)
        if git_stat is None and is_dir:
            git_stat = git_status.get(rel_entry + "/")

        # Symlink target
        symlink_target: Optional[str] = None
        if is_symlink:
            try:
                symlink_target = os.readlink(str(full))
            except OSError:
                symlink_target = None

        # File size
        size: Optional[int] = None
        if not is_dir:
            try:
                size = full.stat().st_size
            except OSError:
                pass

        # Binary detection (only for code candidates)
        binary = False
        if not is_dir and is_code_file(entry, ext):
            binary = is_binary_file(full)

        node = TreeNode(
            name=entry if not config.full_path else str(full.resolve()),
            path=full,
            is_dir=is_dir,
            size=size,
            is_symlink=is_symlink,
            symlink_target=symlink_target,
            git_status=git_stat,
            is_binary=binary,
            extension=ext,
        )

        # ── Code-file collection ──────────────────────────────────────────────
        if config.code and not is_dir and not binary:
            if is_code_file(entry, ext):
                # Honour --exclude patterns against the relative path
                if not (exclude_patterns and matches_path_any(rel_entry, exclude_patterns)):
                    # Honour --max-size
                    if max_size_bytes is None or (size is not None and size <= max_size_bytes):
                        code_files.append(full)

        # ── Stats ─────────────────────────────────────────────────────────────
        if is_dir:
            stats.dirs += 1
        else:
            stats.files += 1
            if size is not None:
                stats.total_bytes += size

        parent_node.children.append(node)

        # ── Recurse into directories ──────────────────────────────────────────
        if is_dir and (not is_symlink or config.follow_symlinks):
            child_stack = gitignore_stack.child()
            # Load nested .gitignore if present
            if config.use_gitignore and pathspec:
                nested_gi = full / ".gitignore"
                if nested_gi.is_file():
                    child_stack.push(rel_entry, nested_gi)

            _walk(
                path=full,
                relative_path=rel_entry,
                depth=depth + 1,
                config=config,
                gitignore_stack=child_stack,
                git_status=git_status,
                ignore_patterns=ignore_patterns,
                exclude_patterns=exclude_patterns,
                max_size_bytes=max_size_bytes,
                stats=stats,
                code_files=code_files,
                parent_node=node,
            )


# ── Public API ────────────────────────────────────────────────────────────────

def walk(root: Path, config: TreeConfig, git_status: Dict[str, str]) -> WalkResult:
    """
    Walk *root* according to *config* and return a :class:`WalkResult`.

    Parameters
    ----------
    root:
        The directory to scan.
    config:
        Runtime configuration object.
    git_status:
        Mapping of ``{relative_path: status_char}`` from
        :func:`treely.git.get_git_info`.
    """
    stats = WalkStats()
    code_files: List[Path] = []

    ignore_patterns = config.ignore.split("|") if config.ignore else []
    exclude_patterns = config.exclude.split("|") if config.exclude else []
    max_size_bytes: Optional[int] = None
    if config.max_size:
        try:
            max_size_bytes = parse_size(config.max_size)
        except ValueError:
            pass  # Validation in main.py already caught this

    # Build root gitignore stack
    gitignore_stack = GitignoreStack()
    if config.use_gitignore and pathspec:
        gitignore_stack = load_root_gitignore(root)

    # Root node
    root_node = TreeNode(
        name=root.name or str(root),
        path=root,
        is_dir=True,
    )

    _walk(
        path=root,
        relative_path="",
        depth=0,
        config=config,
        gitignore_stack=gitignore_stack,
        git_status=git_status,
        ignore_patterns=ignore_patterns,
        exclude_patterns=exclude_patterns,
        max_size_bytes=max_size_bytes,
        stats=stats,
        code_files=code_files,
        parent_node=root_node,
    )

    return WalkResult(root=root_node, code_files=code_files, stats=stats)
