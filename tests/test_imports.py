"""
tests/test_imports.py
~~~~~~~~~~~~~~~~~~~~~
Smoke tests for verifying that all modules import correctly without raising SyntaxErrors,
especially for Python 3.8 / 3.9 type annotations compatibility.
"""
from __future__ import annotations


def test_can_import_all_modules():
    import treely.config
    import treely.config_file
    import treely.filters
    import treely.git
    import treely.main
    import treely.output
    import treely.renderer
    import treely.theme
    import treely.tree_node
    import treely.utils
    import treely.walker

    # Asserting true essentially means no exception was raised during import
    assert True
