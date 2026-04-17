"""
tests/test_renderer.py
~~~~~~~~~~~~~~~~~~~~~~
Tests for the Renderer class: text, JSON, and Markdown output modes.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from treely.config import TreeConfig
from treely.renderer import Renderer
from treely.walker import walk


def _render_text(project: Path, **kw) -> str:
    """Helper: walk *project* and return plain text output."""
    config = TreeConfig(root_path=str(project), no_banner=True, **kw)
    result = walk(project, config, {})
    renderer = Renderer(config)
    return renderer.to_string(result)


# ── Text format ───────────────────────────────────────────────────────────────

class TestTextFormat:
    def test_root_name_in_output(self, simple_project):
        out = _render_text(simple_project)
        assert simple_project.name in out

    def test_tree_structure_characters(self, simple_project):
        out = _render_text(simple_project)
        # Tree connectors should be present
        assert "├──" in out or "└──" in out

    def test_summary_line(self, simple_project):
        out = _render_text(simple_project, summary=True)
        assert "directories" in out
        assert "files" in out

    def test_no_ansi_in_plain_output(self, simple_project):
        out = _render_text(simple_project)
        assert "\033[" not in out

    def test_size_badge_shown(self, simple_project):
        out = _render_text(simple_project, show_size=True)
        # Should contain a size indicator like "1.2K" or "256B"
        assert any(sfx in out for sfx in ["B", "K", "M", "G"])

    def test_code_content_included(self, simple_project):
        out = _render_text(simple_project, code=True)
        assert "FILE CONTENTS" in out
        assert "main.py" in out

    def test_code_content_has_file_text(self, simple_project):
        out = _render_text(simple_project, code=True)
        assert "def main" in out or "print" in out


# ── JSON format ───────────────────────────────────────────────────────────────

class TestJsonFormat:
    def test_valid_json(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), format="json")
        result = walk(simple_project, config, {})
        renderer = Renderer(config)
        out = renderer.to_json(result)
        data = json.loads(out)
        assert isinstance(data, dict)

    def test_root_is_directory(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), format="json")
        result = walk(simple_project, config, {})
        data = json.loads(Renderer(config).to_json(result))
        assert data["type"] == "directory"

    def test_children_list_present(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), format="json")
        result = walk(simple_project, config, {})
        data = json.loads(Renderer(config).to_json(result))
        assert "children" in data
        assert isinstance(data["children"], list)

    def test_file_node_has_extension(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), format="json")
        result = walk(simple_project, config, {})
        data = json.loads(Renderer(config).to_json(result))

        def find_file(node, ext):
            if node.get("type") == "file" and node.get("extension") == ext:
                return node
            for child in node.get("children", []):
                found = find_file(child, ext)
                if found:
                    return found
            return None

        py_file = find_file(data, ".py")
        assert py_file is not None

    def test_summary_added_to_json(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), format="json", summary=True)
        result = walk(simple_project, config, {})
        data = json.loads(Renderer(config).to_json(result))
        assert "_summary" in data
        assert "directories" in data["_summary"]
        assert "files" in data["_summary"]


# ── Markdown format ───────────────────────────────────────────────────────────

class TestMarkdownFormat:
    def test_fenced_code_block(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), format="markdown")
        result = walk(simple_project, config, {})
        out = Renderer(config).to_markdown(result)
        assert "```" in out

    def test_h1_heading(self, simple_project):
        config = TreeConfig(root_path=str(simple_project), format="markdown")
        result = walk(simple_project, config, {})
        out = Renderer(config).to_markdown(result)
        assert out.startswith("# ")

    def test_code_section_uses_language_tags(self, simple_project):
        config = TreeConfig(
            root_path=str(simple_project),
            format="markdown",
            code=True,
        )
        result = walk(simple_project, config, {})
        out = Renderer(config).to_markdown(result)
        assert "```python" in out

    def test_summary_in_italic(self, simple_project):
        config = TreeConfig(
            root_path=str(simple_project),
            format="markdown",
            summary=True,
        )
        result = walk(simple_project, config, {})
        out = Renderer(config).to_markdown(result)
        assert "_" in out and "directories" in out


# ── Token count ───────────────────────────────────────────────────────────────

class TestTokenCount:
    def test_token_count_appears(self, simple_project):
        config = TreeConfig(
            root_path=str(simple_project),
            code=True,
            token_count=True,
        )
        result = walk(simple_project, config, {})
        out = Renderer(config).to_string(result)
        assert "token" in out.lower()

    def test_token_count_is_numeric(self, simple_project):
        config = TreeConfig(
            root_path=str(simple_project),
            code=True,
            token_count=True,
        )
        result = walk(simple_project, config, {})
        out = Renderer(config).to_string(result)
        # Should contain digits
        import re
        assert re.search(r"\d+", out)

class TestTokenCountConsole:
    def test_to_console_token_count_correct_value(self, simple_project, capsys):
        config = TreeConfig(
            root_path=str(simple_project),
            code=True,
            token_count=True,
            no_color=True,
        )
        result = walk(simple_project, config, {})
        renderer = Renderer(config)
        renderer.to_console(result)
        out = capsys.readouterr().out
        assert "tokens" in out.lower()

class TestWindowsEncoding:
    def test_rule_does_not_crash_with_ascii_only(self, simple_project, capsys):
        config = TreeConfig(
            root_path=str(simple_project),
            code=True,
            no_color=True,
        )
        result = walk(simple_project, config, {})
        renderer = Renderer(config)
        # Should not raise UnicodeEncodeError
        renderer.to_console(result)
        out = capsys.readouterr().out
        # Rich safe_box degrades horizontal lines to ASCII or compatible
        assert "FILE CONTENTS" in out
