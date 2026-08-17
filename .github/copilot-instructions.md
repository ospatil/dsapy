# Copilot Instructions

## Project

**dsapy** is an educational Data Structures & Algorithms repository. Every
implementation lives in a Jupyter Notebook under `notebooks/`, organized by
topic. `LEARNING_PATH.md` orders all notebooks into seven phases and is the entry
point for a reader. `main.py` and `scratchpad.py` are throwaway placeholders.

## Commands

```bash
make start          # launch JupyterLab (opens in Chrome incognito via config/)
make test           # execute every notebook end-to-end; inline asserts fail the run
make diagrams       # export docs/diagrams/*.drawio to notebooks/*/images/*.png
uv run black .      # format
uv run ruff check . # lint
```

**Package manager is `uv`**, not pip; dependencies are locked in `uv.lock`. Add
dev packages with `uv add --dev <package>`. Python is pinned by `.mise.toml` and
mise activates `.venv` on `cd`.

## Testing

There is no separate test suite -- **tests live inside the notebooks**. Each
implementation cell defines a `test_<name>()` function directly below the code
and calls it at the bottom of the same cell:

```python
def binary_search(arr, target):
    ...

def test_binary_search():
    arr = [2, 5, 8, 12, 16]
    assert binary_search(arr, 8) == 2
    assert binary_search(arr, 3) == -1
    assert binary_search([], 1) == -1  # cover the empty case

test_binary_search()
```

`make test` runs every notebook with `jupyter execute`, so a failing assert fails
the build. Rules for new code:

- Every algorithm cell needs asserts. Cover the empty input, single element, and
  duplicate/edge cases, not just the happy path.
- When output order is not unique (topological sort, hash iteration), assert the
  defining property with a helper such as `is_topological` or `is_min_heap`
  rather than one specific permutation.
- Cells titled "Python Built-in: ..." demonstrate stdlib equivalents and may use
  `print` instead of asserts.
- Notebooks must be independently executable: `make test` runs each one in a
  fresh kernel, so a notebook may not rely on names defined in another.

## Layout

```
notebooks/
  analysis/            00-quick-reference, notation, loops, recursion, space, amortized
  linked-lists/        singly, doubly, circular
  searching/           binary search
  sorting/             basic sorts, merge, quick, counting/radix
  hashing/             hash tables
  stacks-and-queues/   stacks and queues, monotonic stack
  trees/               binary tree, BST, AVL, heap, trie
  graphs/              basics, traversal, cycle detection, topological sort, dijkstra, union-find
  dynamic-programming/ dp intro
  techniques/          two pointers and sliding window
```

Each topic folder has an `images/` subfolder holding the PNGs its notebooks
reference. Diagram sources live in `docs/diagrams/` (`.drawio`, exported by
`scripts/build-diagrams.sh`) and `docs/diagrams/legacy/` (`.excalidraw`, exported
by hand). `scripts/setup.sh` installs the nbstripout git filter that strips
notebook outputs on commit.

## Notebook conventions

A notebook reads top to bottom as a lesson:

1. A markdown title cell -- `# Topic`, what it is, complexity table, when to use
   it. Every notebook starts with one.
2. Optional diagram cell -- `![Alt text](images/name.png)`.
3. Alternating markdown/code pairs: the markdown explains the idea and states
   **Time** and **Space**, the code implements it plus its tests.
4. A closing `# Python Built-in: ...` section mapping the hand-rolled structure
   to its stdlib counterpart (`bisect`, `heapq`, `deque`, `defaultdict`,
   `lru_cache`).

Also:

- Notebook filenames are lowercase kebab-case: `binary-search-tree.ipynb`.
- Functions and variables are `snake_case`; classes are `PascalCase`.
- Prefer plain functions taking the structure as the first argument (procedural,
  interview style) over wrapper classes, matching the existing notebooks.
- Standard library only -- no production dependencies.
- Python 3.14+, 4-space indent, max line length 80 (`.editorconfig`).
- Favour readability and educational clarity over micro-optimization; comment the
  non-obvious step rather than every line.
- Keep notebooks focused. Split a topic into a new notebook rather than growing
  one past roughly a dozen code cells, and link related notebooks with relative
  markdown links.
- Add a `LEARNING_PATH.md` entry in the right phase for every new notebook.
