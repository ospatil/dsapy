# Copilot Instructions

## Project

**dsapy** is an educational Data Structures & Algorithms repository. All implementations live in Jupyter Notebooks under `notebooks/`, organized by topic. `main.py` and `scratchpad.py` are minimal placeholders.

## Commands

```bash
make start         # Launch JupyterLab (opens in Chrome incognito)
uv run black .     # Format code
uv run ruff check . # Lint code
```

**Package manager is `uv`**, not pip. Dependencies are locked in `uv.lock`. To add dev packages:
```bash
uv add --dev <package>
```

There is no test suite.

## Architecture

All substantive code lives in `notebooks/` organized by topic:

- `analysis/` — Big-O notation, loop complexity, recursion, space complexity
- `linked-lists/` — Singly, doubly, circular
- `sorting/` — Basic sorts, merge sort, quick sort
- `trees/` — Binary tree, BST, heap
- `graphs/` — Graph basics
- `hashing/` — Hash tables
- `misc/` — Additional structures

`docs/` contains Excalidraw/Draw.io diagrams for visual concepts. `scripts/build-diagrams.sh` exports the `.drawio` sources in `docs/diagrams/` to PNGs; `scripts/setup.sh` installs the nbstripout git filter after cloning.

## Conventions

- **Python 3.14+** (pinned via `.mise.toml`, managed by mise)
- **Indentation**: 4 spaces for Python, 2 spaces for other files (`.editorconfig`)
- **Max line length**: 80 characters
- **No production dependencies** — all algorithm implementations use the Python standard library only
- Notebook filenames use lowercase kebab-case (e.g., `binary-search-tree.ipynb`)
- New topic notebooks go in the appropriate `notebooks/<topic>/` subdirectory
- Code in notebooks should prioritize readability and educational clarity over optimization
