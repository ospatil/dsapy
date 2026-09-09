#!/usr/bin/env python3
"""Focused tests for the binary-search practice-mode prototype."""

import ast
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build-practice.py"
SPEC = importlib.util.spec_from_file_location("build_practice", SCRIPT)
build_practice = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_practice)

EXPECTED_TARGETS = [
    "binary_search",
    "binary_search_rec",
    "lower_bound",
    "upper_bound",
    "search_rotated",
]


def function_records(markdown):
    """Map top-level function names to exact source and AST nodes."""
    records = {}
    for code in build_practice.python_cells(markdown):
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                records[node.name] = (ast.get_source_segment(code, node), node)
    return records


def is_ellipsis(statement):
    return (
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Constant)
        and statement.value.value is Ellipsis
    )


class BuildPracticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = build_practice.SOURCE.read_text()
        cls.source_functions = function_records(cls.source)
        cls.test_names = {
            name for name in cls.source_functions if name.startswith("test_")
        }

    def assert_python_cells_parse(self, markdown):
        for code in build_practice.python_cells(markdown):
            ast.parse(code)

    def assert_graders_preserved(self, rendered):
        generated = function_records(rendered)
        for name in self.test_names:
            self.assertEqual(
                generated[name][0],
                self.source_functions[name][0],
                f"changed grader {name}",
            )
            self.assertIn(f"{name}()", rendered)

    def test_strip_targets_are_the_five_lesson_functions(self):
        self.assertEqual(
            build_practice.strip_targets(self.source),
            EXPECTED_TARGETS,
        )

    def test_hint_keeps_signatures_docstrings_and_graders(self):
        rendered = build_practice.render_practice(self.source, "hint")
        generated = function_records(rendered)

        for name in EXPECTED_TARGETS:
            source_node = self.source_functions[name][1]
            generated_node = generated[name][1]
            self.assertTrue(is_ellipsis(generated_node.body[-1]))
            self.assertEqual(
                ast.get_docstring(generated_node, clean=False),
                ast.get_docstring(source_node, clean=False),
            )

        self.assert_graders_preserved(rendered)
        self.assert_python_cells_parse(rendered)

    def test_cold_keeps_only_card_headings_signatures_and_code(self):
        rendered = build_practice.render_practice(self.source, "cold")
        generated = function_records(rendered)

        self.assertIn("> **Mental model.**", rendered)
        self.assertIn("## Lower Bound (First Occurrence)", rendered)
        self.assertNotIn("The changes from plain binary search", rendered)
        for name in EXPECTED_TARGETS:
            node = generated[name][1]
            self.assertEqual(len(node.body), 1)
            self.assertTrue(is_ellipsis(node.body[0]))
            self.assertIsNone(ast.get_docstring(node))

        self.assert_graders_preserved(rendered)
        self.assert_python_cells_parse(rendered)

    def test_blank_removes_signatures_but_keeps_graders(self):
        rendered = build_practice.render_practice(self.source, "blank")
        generated = function_records(rendered)

        for name in EXPECTED_TARGETS:
            self.assertNotIn(name, generated)
        self.assert_graders_preserved(rendered)
        self.assert_python_cells_parse(rendered)

    def test_builtin_cell_is_unchanged_at_every_level(self):
        builtin_source = self.source_functions["bisect_search"][0]
        for level in build_practice.LEVELS:
            rendered = build_practice.render_practice(self.source, level)
            generated = function_records(rendered)
            self.assertEqual(generated["bisect_search"][0], builtin_source)

    def test_every_level_keeps_metadata_and_overwrite_warning(self):
        for level in build_practice.LEVELS:
            rendered = build_practice.render_practice(self.source, level)
            self.assertTrue(rendered.startswith("---\n"))
            self.assertIn("Generated practice file", rendered)
            self.assertIn("# Binary Search", rendered)

    def test_cli_writes_an_explicit_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "binary-search.md"
            result = build_practice.main(["--level", "cold", "--output", str(output)])
            self.assertEqual(result, 0)
            self.assertEqual(
                output.read_text(),
                build_practice.render_practice(self.source, "cold"),
            )


if __name__ == "__main__":
    unittest.main()
