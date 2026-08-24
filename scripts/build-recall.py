#!/usr/bin/env python3
"""Generate RECALL.md from the mental-model cards embedded in the notebooks.

The cards live in the notebooks, where they orient you before you read the code.
This collects them into one page where the answer is hidden behind a <details>,
so the same text can be used the other way round: read the topic, try to rebuild
the idea from memory, then expand to check. Re-reading is a weak way to hold on
to something months later; trying to retrieve it first is a strong one.

Generated, never hand-edited - the notebooks stay the single source.

Usage: make recall          rebuild the page
       make test            runs this with --check and fails if the page is stale
                            or if a notebook carries no card (see EXEMPT)
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "RECALL.md")

CARD_START = re.compile(r"^> \*\*Mental model\.\*\*")
# Only H1s: a card sits either in the title cell or at the head of a major
# algorithm section, and both are `#`. Tracking the *nearest* heading of any
# level mislabels 11 of them, because several title cells end with subsections.
HEADING = re.compile(r"^# +(.*?)\s*$")
# A link inside a card is relative to the notebook's own folder. RECALL.md sits
# at the repo root, so those have to be rewritten or they 404 on GitHub.
RELATIVE_LINK = re.compile(r"\]\((?!https?:|#|/)([^)]+)\)")

# Every notebook is expected to open with a card. A notebook holding none used to
# be skipped in silence, which let the convention rot unnoticed - so absence is
# now an error under --check, and the deliberate exceptions are listed here.
EXEMPT = {
    # A condensed field guide over notebooks 01-05 rather than a lesson of its
    # own. Its one idea is "name the complexity of unfamiliar code on sight",
    # which is the page itself; a card would restate all of it.
    "notebooks/analysis/00-quick-reference.md",
}


def read(path):
    with open(path) as fh:
        return fh.read()


def rebase_links(line, notebook_dir):
    """Rewrite a card's relative links to be relative to the repo root."""

    def fix(match):
        target = match.group(1)
        anchor = ""
        if "#" in target:
            target, anchor = target.split("#", 1)
            anchor = "#" + anchor
        resolved = os.path.normpath(os.path.join(notebook_dir, target))
        return f"]({resolved}{anchor})"

    return RELATIVE_LINK.sub(fix, line)


def extract_cards(path):
    """Yield (heading, card_lines) for every card in a notebook, in file order."""
    lines = read(path).split("\n")
    notebook_dir = os.path.dirname(path)
    heading = None
    i = 0
    while i < len(lines):
        match = HEADING.match(lines[i])
        if match:
            heading = match.group(1)
        if CARD_START.match(lines[i]):
            card = []
            while i < len(lines) and (lines[i].startswith(">") or lines[i] == ""):
                # a blank line ends the blockquote unless the next line continues it
                if lines[i] == "":
                    if i + 1 < len(lines) and lines[i + 1].startswith(">"):
                        card.append(lines[i])
                        i += 1
                        continue
                    break
                card.append(rebase_links(lines[i], notebook_dir))
                i += 1
            yield heading, card
            continue
        i += 1


def learning_path_order():
    """Notebook paths in LEARNING_PATH.md order, so recall follows the lesson order."""
    seen = []
    for match in re.finditer(
        r"\((notebooks/[^)]+\.md)\)", read(os.path.join(ROOT, "LEARNING_PATH.md"))
    ):
        if match.group(1) not in seen:
            seen.append(match.group(1))
    return seen


HEADER = """# Recall

Every mental-model card from the notebooks, with the answers hidden.

Cold, after months away, this is the cheapest way back in. Read a topic, say the
idea out loud or sketch the loop, *then* expand the card and compare. The gap
between what you produced and what is written is the only part worth re-reading,
and it tells you which notebook to open.

Generated from the notebooks by `make recall` - edit the cards there, not here.
"""


def render():
    ordered = learning_path_order()
    found = sorted(
        f
        for f in glob.glob("notebooks/**/*.md", recursive=True)
        if "checkpoint" not in f
    )
    unlisted = [f for f in found if f not in ordered]
    if unlisted:
        print(
            f"warning: not in LEARNING_PATH, appended at the end: {unlisted}",
            file=sys.stderr,
        )

    out = HEADER.split("\n")
    total = 0
    missing = []
    for path in ordered + unlisted:
        if not os.path.exists(path):
            continue
        cards = list(extract_cards(path))
        if not cards:
            if path not in EXEMPT:
                missing.append(path)
            continue
        out.append(f"## [{os.path.basename(path)[:-3]}]({path})")
        out.append("")
        for heading, card in cards:
            out.append("<details>")
            out.append(f"<summary><strong>{heading}</strong></summary>")
            out.append("")
            out.extend(card)
            out.append("")
            out.append("</details>")
            out.append("")
            total += 1
    return "\n".join(out).rstrip() + "\n", total, missing


def report_missing(missing):
    print(
        "error: no mental-model card in:\n"
        + "".join(f"  {path}\n" for path in missing)
        + "Every notebook opens with a card (see README). Add one, or add the\n"
        "path to EXEMPT in this script if the notebook genuinely warrants none.",
        file=sys.stderr,
    )


def main():
    os.chdir(ROOT)
    text, total, missing = render()

    if "--check" in sys.argv:
        failed = False
        if missing:
            report_missing(missing)
            failed = True
        current = read(OUT) if os.path.exists(OUT) else ""
        if current != text:
            print(
                "RECALL.md is stale: a card changed but the page was not regenerated.\n"
                "Run `make recall`.",
                file=sys.stderr,
            )
            failed = True
        if failed:
            return 1
        print(f"RECALL.md is current ({total} cards)")
        return 0

    if missing:
        report_missing(missing)

    with open(OUT, "w") as fh:
        fh.write(text)
    print(f"wrote RECALL.md: {total} cards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
