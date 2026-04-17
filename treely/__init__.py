"""
treely
~~~~~~
A modern, beautiful, and powerful command-line directory tree generator.

Public Python API::

    from treely import walk, TreeConfig, Renderer

    config = TreeConfig(root_path="/my/project", use_gitignore=True, code=True)
    result = walk(Path("/my/project"), config, git_status={})
    renderer = Renderer(config)
    print(renderer.to_string(result))
"""
from .config import TreeConfig
from .tree_node import TreeNode, WalkResult, WalkStats
from .walker import walk
from .renderer import Renderer
from .theme import THEME_NAMES, get_theme

__version__ = "2.0.0"
__author__ = "Rudra Mondal"
__license__ = "MIT"

__all__ = [
    "TreeConfig",
    "TreeNode",
    "WalkResult",
    "WalkStats",
    "walk",
    "Renderer",
    "get_theme",
    "THEME_NAMES",
    "__version__",
]
