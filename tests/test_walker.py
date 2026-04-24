"""
tests/test_walker.py
~~~~~~~~~~~~~~~~~~~~
Integration tests for treely.walker.walk — verifies tree structure, filtering,
gitignore support, depth limiting, sorting, and code-file collection.
"""
from __future__ import annotations

from treely.config import TreeConfig
from treely.walker import walk


def _names(node) -> list[str]:
    """Collect direct child names of a TreeNode."""
    return [c.name for c in node.children]


def _all_names(node, names=None) -> list[str]:
    """Recursively collect ALL descendant names."""
    if names is None:
        names = []
    for child in node.children:
        names.append(child.name)
        _all_names(child, names)
    return names


# ── Basic structure ────────────────────────────────────────────────────────────

class TestBasicWalk:
    def test_root_node_defaults(self, simple_project):
        config = TreeConfig(root_path=str(simple_project))
        result = walk(simple_project, config, {})
        assert result.root.is_dir
        assert result.root.name == simple_project.name

    def test_stats_counted(self, simple_project):
        config = TreeConfig(root_path=str(simple_project))
        result = walk(simple_project, config, {})
        # src/, tests/, dist/ + their files
        assert result.stats.dirs >= 2
        assert result.stats.files >= 3

    def test_top_level_children_present(self, simple_project):
        config = TreeConfig(root_path=str(simple_project))
        result = walk(simple_project, config, {})
        top = _names(result.root)
        assert "src" in top
        assert "tests" in top
        assert "README.md" in top

    def test_hidden_files_excluded_by_default(self, simple_project):
        config = TreeConfig(root_path=str(simple_project))
        result = walk(simple_project, config, {})
        top = _names(result.root)
        assert ".gitignore" not in top

    def test_hidden_files_shown_with_all(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), all=True)
        result = walk(simple_project, config, {})
        top = _names(result.root)
        assert ".gitignore" in top


# ── Depth limiting ─────────────────────────────────────────────────────────────

class TestDepthLimit:
    def test_level_1_no_children_descend(self, deep_project):
        config = TreeConfig(root_path=str(deep_project), level=1)
        result = walk(deep_project, config, {})
        for child in result.root.children:
            if child.is_dir:
                assert len(child.children) == 0, (
                    f"Expected no grandchildren at level=1 for {child.name}"
                )

    def test_level_2_allows_grandchildren(self, deep_project):
        config = TreeConfig(root_path=str(deep_project), level=2)
        result = walk(deep_project, config, {})
        all_names = _all_names(result.root)
        assert "file.txt" in all_names  # depth-1 files visible

    def test_unlimited_depth(self, deep_project):
        config = TreeConfig(root_path=str(deep_project), level=-1)
        result = walk(deep_project, config, {})
        all_names = _all_names(result.root)
        assert "deep.py" in all_names  # depth-2 files reachable


# ── Gitignore filtering ────────────────────────────────────────────────────────

class TestGitignoreFiltering:
    def test_gitignore_excludes_dist(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), use_gitignore=True)
        result = walk(simple_project, config, {})
        top = _names(result.root)
        assert "dist" not in top

    def test_nested_gitignore_excludes_subdir_files(self, nested_gitignore_project):
        config = TreeConfig(
            root_path=str(nested_gitignore_project),
            use_gitignore=True,
            all=True,
        )
        result = walk(nested_gitignore_project, config, {})
        all_names = _all_names(result.root)
        # root.log ignored by root gitignore (*.log)
        assert "root.log" not in all_names
        # sub.tmp ignored by subdir gitignore (*.tmp)
        assert "sub.tmp" not in all_names
        # code.py should be present
        assert "code.py" in all_names


# ── Ignore patterns ────────────────────────────────────────────────────────────

class TestIgnorePatterns:
    def test_ignore_by_name(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), ignore="dist")
        result = walk(simple_project, config, {})
        assert "dist" not in _names(result.root)

    def test_ignore_by_glob(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), ignore="*.md")
        result = walk(simple_project, config, {})
        assert "README.md" not in _names(result.root)

    def test_ignore_multiple_patterns(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), ignore="dist|*.md")
        result = walk(simple_project, config, {})
        top = _names(result.root)
        assert "dist" not in top
        assert "README.md" not in top


# ── --dirs-only / --files-only ────────────────────────────────────────────────

class TestDirsFilesOnly:
    def test_dirs_only(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), dirs_only=True)
        result = walk(simple_project, config, {})
        for child in result.root.children:
            assert child.is_dir, f"Expected only dirs, got file: {child.name}"

    def test_files_only(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), files_only=True)
        result = walk(simple_project, config, {})
        for child in result.root.children:
            assert not child.is_dir, f"Expected only files, got dir: {child.name}"


# ── Pattern filter ─────────────────────────────────────────────────────────────

class TestPatternFilter:
    def test_pattern_filters_files(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), pattern="*.py")
        result = walk(simple_project, config, {})
        # README.md should NOT appear since it doesn't match *.py
        all_names = _all_names(result.root)
        assert "README.md" not in all_names

    def test_pattern_still_descends_into_dirs(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), pattern="*.py")
        result = walk(simple_project, config, {})
        all_names = _all_names(result.root)
        # Python files inside src/ should be reachable
        assert "main.py" in all_names


# ── Sorting ────────────────────────────────────────────────────────────────────

class TestSorting:
    def test_default_sort_dirs_first(self, simple_project):
        config = TreeConfig(root_path=str(simple_project))
        result = walk(simple_project, config, {})
        children = result.root.children
        dirs = [c for c in children if c.is_dir]
        files = [c for c in children if not c.is_dir]
        # All dirs should appear before files
        if dirs and files:
            last_dir_idx = max(children.index(d) for d in dirs)
            first_file_idx = min(children.index(f) for f in files)
            assert last_dir_idx < first_file_idx

    def test_ext_sort_groups_by_extension(self, tmp_path):
        (tmp_path / "z.py").write_text("")
        (tmp_path / "a.md").write_text("")
        (tmp_path / "b.py").write_text("")
        (tmp_path / "c.md").write_text("")
        config = TreeConfig(root_path=str(tmp_path), sort="ext")
        result = walk(tmp_path, config, {})
        names = [c.name for c in result.root.children]
        # .md files should be grouped together, .py files together
        md_indices = [names.index(n) for n in names if n.endswith(".md")]
        py_indices = [names.index(n) for n in names if n.endswith(".py")]
        assert max(md_indices) < min(py_indices) or max(py_indices) < min(md_indices)


# ── Code file collection ───────────────────────────────────────────────────────

class TestCodeFileCollection:
    def test_code_files_collected(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), code=True)
        result = walk(simple_project, config, {})
        assert len(result.code_files) > 0
        names = [f.name for f in result.code_files]
        assert "main.py" in names
        assert "utils.py" in names

    def test_binary_excluded_from_code(self, binary_project):
        config = TreeConfig(root_path=str(binary_project), code=True)
        result = walk(binary_project, config, {})
        names = [f.name for f in result.code_files]
        assert "image.png" not in names
        assert "data.bin" not in names
        assert "script.py" in names

    def test_exclude_pattern_removes_from_code(self, simple_project):
        config = TreeConfig(
            root_path=str(simple_project),
            code=True,
            exclude="src/*",
        )
        result = walk(simple_project, config, {})
        names = [f.name for f in result.code_files]
        assert "main.py" not in names
        assert "utils.py" not in names

    def test_max_size_skips_large_file(self, tmp_path):
        big = tmp_path / "big.py"
        big.write_text("x = 1\n" * 500_000)  # ~3.5 MB
        small = tmp_path / "small.py"
        small.write_text("y = 2\n")
        config = TreeConfig(root_path=str(tmp_path), code=True, max_size="100K")
        result = walk(tmp_path, config, {})
        names = [f.name for f in result.code_files]
        assert "big.py" not in names
        assert "small.py" in names


# ── Symlink handling ───────────────────────────────────────────────────────────

class TestSymlinks:
    def test_symlink_detected(self, symlink_project):
        config = TreeConfig(root_path=str(symlink_project))
        result = walk(symlink_project, config, {})
        link_nodes = [c for c in result.root.children if c.is_symlink]
        assert len(link_nodes) == 1
        assert link_nodes[0].name == "link_to_real"

    def test_symlink_not_followed_by_default(self, symlink_project):
        config = TreeConfig(root_path=str(symlink_project))
        result = walk(symlink_project, config, {})
        link_node = next(c for c in result.root.children if c.is_symlink)
        assert len(link_node.children) == 0

    def test_follow_symlinks_recurses(self, symlink_project):
        config = TreeConfig(root_path=str(symlink_project), follow_symlinks=True)
        result = walk(symlink_project, config, {})
        link_node = next(c for c in result.root.children if c.name == "link_to_real")
        assert len(link_node.children) > 0

    def test_symlink_dir_classified_as_dir_in_filter(self, symlink_project):
        config = TreeConfig(root_path=str(symlink_project))
        result = walk(symlink_project, config, {})
        link_node = next(c for c in result.root.children if c.name == "link_to_real")
        assert link_node.is_dir

    def test_dirs_only_includes_symlinked_dirs(self, symlink_project):
        config = TreeConfig(root_path=str(symlink_project), dirs_only=True)
        result = walk(symlink_project, config, {})
        names = [c.name for c in result.root.children]
        # Should be included because it's a symlink to a directory
        assert "link_to_real" in names

    def test_files_only_excludes_symlinked_dirs(self, symlink_project):
        config = TreeConfig(root_path=str(symlink_project), files_only=True)
        result = walk(symlink_project, config, {})
        names = [c.name for c in result.root.children]
        # Should be excluded because it's a symlink to a directory, not a file
        assert "link_to_real" not in names


# ── Git status annotation ──────────────────────────────────────────────────────

class TestGitStatus:
    def test_git_status_annotated(self, simple_project):
        git_status = {"src/main.py": "M", "README.md": "A"}
        config = TreeConfig(root_path=str(simple_project))
        result = walk(simple_project, config, git_status)
        all_nodes = _collect_all_nodes(result.root)
        main_py = next((n for n in all_nodes if n.name == "main.py"), None)
        readme = next((n for n in all_nodes if n.name == "README.md"), None)
        assert main_py is not None and main_py.git_status == "M"
        assert readme is not None and readme.git_status == "A"

    def test_no_git_status_when_empty_dict(self, simple_project):
        config = TreeConfig(root_path=str(simple_project))
        result = walk(simple_project, config, {})
        all_nodes = _collect_all_nodes(result.root)
        for node in all_nodes:
            assert node.git_status is None


def _collect_all_nodes(node, nodes=None):
    if nodes is None:
        nodes = []
    for child in node.children:
        nodes.append(child)
        _collect_all_nodes(child, nodes)
    return nodes
