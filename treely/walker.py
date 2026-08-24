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


def _sort_entries(entries: List[os.DirEntry], sort: str) -> List[os.DirEntry]:
    """
    Split *entries* into dirs and files, sort each group according to *sort*,
    and return them concatenated (dirs always first).
    """
    dirs: List[os.DirEntry] = []
    files: List[os.DirEntry] = []
    for e in entries:
        try:
            is_dir = e.is_dir()
        except OSError:
            is_dir = False
        (dirs if is_dir else files).append(e)

    if sort == "size":

        def _size(e: os.DirEntry) -> int:
            try:
                return e.stat().st_size
            except OSError:
                return 0

        files.sort(key=_size, reverse=True)
        dirs.sort(key=lambda e: e.name.lower())

    elif sort == "mtime":

        def _mtime(e: os.DirEntry) -> float:
            try:
                return e.stat().st_mtime
            except OSError:
                return 0.0

        dirs.sort(key=_mtime, reverse=True)
        files.sort(key=_mtime, reverse=True)

    elif sort == "ext":
        files.sort(key=lambda e: (os.path.splitext(e.name)[1].lower(), e.name.lower()))
        dirs.sort(key=lambda e: e.name.lower())

    else:  # "name" (default)
        dirs.sort(key=lambda e: e.name.lower())
        files.sort(key=lambda e: e.name.lower())

    return dirs + files


# ── Directory size calculation ────────────────────────────────────────────────


def _compute_dir_size(
    dir_path: Path,
    relative_path: str,
    config: TreeConfig,
    gitignore_stack: GitignoreStack,
    ignore_patterns: List[str],
) -> int:
    """
    Recursively compute the total size in bytes of all matching files within *dir_path*,
    taking into account active filters (hidden files, gitignore, ignore patterns, pattern).
    """
    total = 0
    try:
        with os.scandir(dir_path) as entries:
            for entry in entries:
                try:
                    is_symlink = entry.is_symlink()
                    is_dir = entry.is_dir()
                except OSError:
                    continue

                name = entry.name

                # Always-skip set (e.g. __pycache__, .DS_Store) - unless --all
                if name in ALWAYS_SKIP and not config.all:
                    continue

                # Hidden items (dirs or files starting with '.')
                if not config.all and name.startswith("."):
                    continue

                # --ignore patterns
                if ignore_patterns and matches_any(name, ignore_patterns):
                    continue

                rel = (relative_path + "/" + name) if relative_path else name

                # gitignore check
                if config.use_gitignore and pathspec:
                    check_path = rel + "/" if is_dir else rel
                    if gitignore_stack.matches(check_path) or gitignore_stack.matches(rel):
                        continue

                if is_dir:
                    if not is_symlink or config.follow_symlinks:
                        child_stack = gitignore_stack.child()
                        if config.use_gitignore and pathspec:
                            nested_gi = Path(entry.path) / ".gitignore"
                            if nested_gi.is_file():
                                child_stack.push(rel, nested_gi)
                        total += _compute_dir_size(
                            Path(entry.path),
                            rel,
                            config,
                            child_stack,
                            ignore_patterns,
                        )
                else:
                    if config.pattern:
                        import fnmatch as _fnm

                        if not _fnm.fnmatch(name, config.pattern):
                            continue
                    if config.dirs_only:
                        continue
                    try:
                        total += entry.stat().st_size
                    except OSError:
                        pass
    except OSError:
        pass

    return total


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
    raw_entries = []
    try:
        with os.scandir(path) as it:
            raw_entries = list(it)
    except PermissionError:
        err_node = TreeNode(
            name="[Permission Denied]",
            path=path,
            is_dir=False,
            error="permission",
        )
        parent_node.children.append(err_node)
        return
    except OSError:
        return

    # ── Filter entries ────────────────────────────────────────────────────────
    filtered: List[os.DirEntry] = []
    for entry in raw_entries:
        try:
            is_dir = entry.is_dir()
        except OSError:
            continue

        name = entry.name

        # Always-skip set (e.g. __pycache__, .DS_Store) - unless --all
        if name in ALWAYS_SKIP and not config.all:
            continue

        # Hidden items  (dirs starting with '.' are also hidden)
        if not config.all and name.startswith("."):
            continue

        # --ignore patterns
        if ignore_patterns and matches_any(name, ignore_patterns):
            continue

        # gitignore check (dirs get trailing slash added for spec matching)
        if config.use_gitignore and pathspec:
            rel = (relative_path + "/" + name) if relative_path else name
            check_path = rel + "/" if is_dir else rel
            if gitignore_stack.matches(check_path) or gitignore_stack.matches(rel):
                continue

        # --pattern applies to files only (always descend into directories)
        if config.pattern and not is_dir:
            import fnmatch as _fnm

            if not _fnm.fnmatch(name, config.pattern):
                continue

        # --dirs-only / --files-only
        if config.dirs_only and not is_dir:
            continue
        if config.files_only and is_dir:
            continue

        filtered.append(entry)

    # ── Sort ──────────────────────────────────────────────────────────────────
    combined = _sort_entries(filtered, config.sort)

    # ── Build TreeNode children ───────────────────────────────────────────────
    for entry in combined:
        full = Path(entry.path)
        try:
            is_symlink = entry.is_symlink()
            is_dir = entry.is_dir()
        except OSError:
            continue

        name = entry.name
        ext = os.path.splitext(name)[1].lower()
        rel_entry = (relative_path + "/" + name) if relative_path else name

        # Git status lookup
        git_stat: Optional[str] = git_status.get(rel_entry)
        # For directories, check if any child is dirty (use dir key if present)
        if git_stat is None and is_dir:
            git_stat = git_status.get(rel_entry + "/")

        # Symlink target
        symlink_target: Optional[str] = None
        if is_symlink:
            try:
                symlink_target = os.readlink(entry.path)
            except OSError:
                symlink_target = None

        # File size
        size: Optional[int] = None
        if not is_dir:
            try:
                size = entry.stat().st_size
            except OSError:
                pass

        # Binary detection (only for code candidates)
        binary = False
        if not is_dir and is_code_file(name, ext):
            binary = is_binary_file(full)

        node = TreeNode(
            name=name if not config.full_path else str(full.resolve()),
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
            if is_code_file(name, ext):
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
        if is_dir:
            if not is_symlink or config.follow_symlinks:
                child_stack = gitignore_stack.child()
                # Load nested .gitignore if present
                if config.use_gitignore and pathspec:
                    nested_gi = full / ".gitignore"
                    if nested_gi.is_file():
                        child_stack.push(rel_entry, nested_gi)

                if config.level != -1 and depth + 1 >= config.level:
                    # Max visual depth reached; compute directory size without expanding children
                    node.size = _compute_dir_size(
                        dir_path=full,
                        relative_path=rel_entry,
                        config=config,
                        gitignore_stack=child_stack,
                        ignore_patterns=ignore_patterns,
                    )
                else:
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
                    # Sized bottom-up after children have been populated
                    node.size = sum(c.size for c in node.children if c.size is not None)
            else:
                try:
                    node.size = full.lstat().st_size
                except OSError:
                    node.size = 0


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

    if config.level == 0:
        root_node.size = _compute_dir_size(
            dir_path=root,
            relative_path="",
            config=config,
            gitignore_stack=gitignore_stack,
            ignore_patterns=ignore_patterns,
        )
    else:
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
        root_node.size = sum(c.size for c in root_node.children if c.size is not None)

    return WalkResult(root=root_node, code_files=code_files, stats=stats)
