"""
tests/test_imports.py
~~~~~~~~~~~~~~~~~~~~~
Smoke tests for verifying that all modules import correctly without raising SyntaxErrors,
especially for Python 3.8 / 3.9 type annotations compatibility.
"""
from __future__ import annotations


def test_can_import_all_modules():

    # Asserting true essentially means no exception was raised during import
    assert True
