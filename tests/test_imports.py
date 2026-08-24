"""
tests/test_imports.py
~~~~~~~~~~~~~~~~~~~~~
Smoke tests for verifying that all modules import correctly without raising SyntaxErrors,
especially for Python 3.8 / 3.9 type annotations compatibility.
"""

from __future__ import annotations


def test_can_import_all_modules():
    import treely.config  # noqa: F401
    import treely.config_file  # noqa: F401
    import treely.filters  # noqa: F401
    import treely.git  # noqa: F401
    import treely.main  # noqa: F401
    import treely.output  # noqa: F401
    import treely.renderer  # noqa: F401
    import treely.theme  # noqa: F401
    import treely.tree_node  # noqa: F401
    import treely.utils  # noqa: F401
    import treely.walker  # noqa: F401

    # Asserting true essentially means no exception was raised during import
    assert True
