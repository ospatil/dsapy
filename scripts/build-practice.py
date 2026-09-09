#!/usr/bin/env python3
"""Generate a binary-search practice notebook from the authored lesson.

This is the one-notebook prototype for the full design in
``docs/practice-mode.md``. It deliberately supports only binary search while
its transformation rules are proved out.
"""

import argparse
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "notebooks/searching/binary-search.md"
OUTPUT = ROOT / "practice/searching/binary-search.md"
LEVELS = ("hint", "cold", "blank")

PYTHON_FENCE = re.compile(r"^```python\s*$")
CLOSING_FENCE = re.compile(r"^```\s*$")
SECTION_HEADING = re.compile(r"^## ")
BUILTIN_HEADING = re.compile(r"^#+ Python Built-in")
CARD_START = re.compile(r"^> \*\*Mental model\.\*\*")

WARNING = (
    "<!-- Generated practice file. Write your attempt here, but rerunning -->\n"
    "<!-- make practice-binary-search overwrites everything in this file. -->\n"
)


def _is_docstring(node):
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def _line_indent(line):
    return line[: len(line) - len(line.lstrip())]


def implementation_names(code):
    """Return top-level implementation names in one Python cell."""
    tree = ast.parse(code)
    return [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("test_")
    ]


def strip_implementations(code, level):
    """Replace top-level implementation bodies while preserving tests."""
    if level not in LEVELS:
        raise ValueError(f"unknown practice level: {level}")

    lines = code.splitlines(keepends=True)
    tree = ast.parse(code)
    functions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("test_")
    ]

    replacements = []
    for node in functions:
        if level == "blank":
            decorators = node.decorator_list
            start_line = decorators[0].lineno if decorators else node.lineno
            replacements.append((start_line - 1, node.end_lineno, []))
            continue

        first_statement = node.body[0]
        indent = _line_indent(lines[first_statement.lineno - 1])
        start = first_statement.lineno - 1
        if level == "hint" and _is_docstring(first_statement):
            start = first_statement.end_lineno
        replacements.append((start, node.end_lineno, [f"{indent}...\n"]))

    for start, end, replacement in reversed(replacements):
        lines[start:end] = replacement
    return "".join(lines)


def _python_spans(lines):
    """Yield (opening index, closing index, code) for Python fences."""
    i = 0
    while i < len(lines):
        if not PYTHON_FENCE.match(lines[i].rstrip("\r\n")):
            i += 1
            continue
        closing = i + 1
        while closing < len(lines):
            if CLOSING_FENCE.match(lines[closing].rstrip("\r\n")):
                break
            closing += 1
        if closing == len(lines):
            raise ValueError("unclosed Python fence")
        yield i, closing, "".join(lines[i + 1 : closing])
        i = closing + 1


def python_cells(markdown):
    """Return every fenced Python cell in a Markdown notebook."""
    lines = markdown.splitlines(keepends=True)
    return [code for _, _, code in _python_spans(lines)]


def _split_sections(markdown):
    lines = markdown.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if SECTION_HEADING.match(line)]
    if not starts:
        return lines, []

    prelude = lines[: starts[0]]
    sections = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        sections.append(lines[start:end])
    return prelude, sections


def _is_builtin_section(section):
    return bool(section and BUILTIN_HEADING.match(section[0]))


def _transform_fences(lines, level, preserve=False):
    result = []
    cursor = 0
    for opening, closing, code in _python_spans(lines):
        result.extend(lines[cursor : opening + 1])
        transformed = code if preserve else strip_implementations(code, level)
        result.append(transformed)
        result.append(lines[closing])
        cursor = closing + 1
    result.extend(lines[cursor:])
    return result


def _card_from(prelude):
    for start, line in enumerate(prelude):
        if not CARD_START.match(line):
            continue
        end = start
        card = []
        while end < len(prelude):
            if prelude[end].startswith(">"):
                card.append(prelude[end])
                end += 1
                continue
            if (
                prelude[end].strip() == ""
                and end + 1 < len(prelude)
                and prelude[end + 1].startswith(">")
            ):
                card.append(prelude[end])
                end += 1
                continue
            break
        return "".join(card).rstrip()
    raise ValueError("binary-search notebook has no mental-model card")


def _minimal_prelude(prelude, notebook_lines):
    blocks = []
    if prelude and prelude[0].strip() == "---":
        closing = next(i for i in range(1, len(prelude)) if prelude[i].strip() == "---")
        blocks.append("".join(prelude[: closing + 1]).rstrip())

    title = next(line.rstrip() for line in prelude if line.startswith("# "))
    blocks.extend((title, _card_from(notebook_lines)))
    return "\n\n".join(blocks) + "\n\n"


def _minimal_section(section, level):
    cells = []
    preserve = _is_builtin_section(section)
    for opening, closing, code in _python_spans(section):
        transformed = code if preserve else strip_implementations(code, level)
        cell = section[opening] + transformed + section[closing]
        cells.append(cell.rstrip())
    if not cells:
        return ""
    return section[0].rstrip() + "\n\n" + "\n\n".join(cells) + "\n\n"


def _insert_warning(markdown):
    lines = markdown.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].strip() == "---":
        insert_at = (
            next(i for i in range(1, len(lines)) if lines[i].strip() == "---") + 1
        )
    lines[insert_at:insert_at] = ["\n", WARNING, "\n"]
    return "".join(lines)


def render_practice(markdown, level="hint"):
    """Render one practice notebook at the requested assistance level."""
    if level not in LEVELS:
        raise ValueError(f"unknown practice level: {level}")

    prelude, sections = _split_sections(markdown)
    if level == "hint":
        rendered = list(prelude)
        for section in sections:
            rendered.extend(
                _transform_fences(
                    section,
                    level,
                    preserve=_is_builtin_section(section),
                )
            )
        return _insert_warning("".join(rendered))

    rendered = [_minimal_prelude(prelude, markdown.splitlines(keepends=True))]
    rendered.extend(_minimal_section(section, level) for section in sections)
    return _insert_warning("".join(rendered).rstrip() + "\n")


def strip_targets(markdown):
    """Return implementation names stripped by this prototype."""
    _, sections = _split_sections(markdown)
    targets = []
    for section in sections:
        if _is_builtin_section(section):
            continue
        for _, _, code in _python_spans(section):
            targets.extend(implementation_names(code))
    return targets


def _resolve_output(path):
    return path if path.is_absolute() else ROOT / path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", choices=LEVELS, default="hint")
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help="output Markdown path (default: practice/searching/binary-search.md)",
    )
    args = parser.parse_args(argv)

    source = SOURCE.read_text()
    output = _resolve_output(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_practice(source, args.level))
    count = len(strip_targets(source))
    try:
        display = output.relative_to(ROOT)
    except ValueError:
        display = output
    print(f"wrote {display}: {args.level}, {count} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
