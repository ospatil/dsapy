# dsapy - agent instructions

Conventions for anyone, human or agent, working in this repo. Diagram authoring
lives in a separate on-demand skill (`skills/diagrams/SKILL.md`), because it is
long and only matters when you are actually drawing something.

Each file here has exactly one copy; the per-tool paths are symlinks to it, so
there is no second version to keep in sync. `CLAUDE.md` points at this file
(Claude Code reads `CLAUDE.md`, not `AGENTS.md`), and `.claude/skills/diagrams/`
and `.kiro/skills/diagrams/` both point at the canonical skill. Edit the real
file - `AGENTS.md` or `skills/diagrams/SKILL.md` - never a link.

`HANDOFF.md` carries what this file does not: the state of work in flight, and
the decisions and traps behind the way the repo is set up. Read it before
starting work, and update its "Current state" section when work lands.

## Project

**dsapy** is an educational Data Structures & Algorithms repository. Every
implementation lives in a Jupyter Notebook under `notebooks/`, organized by
topic. Notebooks are **authored as Markdown** and paired to `.ipynb` by
[Jupytext](https://jupytext.readthedocs.io/) (see `jupytext.toml`): the `.md` is
the source of truth and the only file git tracks, the `.ipynb` is a gitignored
local build artifact that JupyterLab opens. Editing either updates the pair on
save. `LEARNING_PATH.md` orders all notebooks into seven phases and is the entry
point for a reader. `main.py` and `scratchpad.py` are throwaway placeholders.

## Commands

```bash
make start          # launch JupyterLab (opens in Chrome incognito via config/)
make sync           # regenerate the paired .ipynb after a fresh clone
make recall         # rebuild RECALL.md from the notebooks' mental-model cards
make test           # execute every notebook end-to-end; inline asserts fail the run
make diagrams       # export docs/diagrams/*.drawio to notebooks/*/images/*.png
uv run black .        # format (Python files only - see below)
uv run ruff check .   # lint
```

**Do not swap `black` for `ruff format`.** Ruff formats Python inside Markdown
fenced blocks, so `ruff format .` rewrites all the notebooks and flattens the
aligned trailing comments (`# 𝛳(log n)`, `# T(n/2)`) that the lessons rely on.
Black only touches `.py`, which is why it is still here.

`RECALL.md` is generated from the cards by `scripts/build-recall.py` and must not
be hand-edited; `make test` runs the script in `--check` mode and fails if a card
changed without the page being rebuilt, or if a notebook has no card at all. Add
a card when adding a notebook - or, if it genuinely warrants none, add it to
`EXEMPT` in that script with the reason.

**Package manager is `uv`**, not pip; dependencies are locked in `uv.lock`. Add
dev packages with `uv add --dev <package>`. Python is pinned by `.mise.toml` and
mise activates `.venv` on `cd`. The root `requirements.txt` is for Binder only,
which needs Jupytext to turn the Markdown sources into notebooks; `postBuild`
generates the pairs at image build time.

## Testing

There is no separate test suite - **tests live inside the notebooks**. Each
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

`make test` converts each `.md` with `jupytext --execute`, so a failing assert
fails the build. Rules for new code:

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
by hand). `scripts/setup.sh` generates the paired `.ipynb` for each Markdown
notebook and is run once after cloning.

## Notebook conventions

A notebook reads top to bottom as a lesson:

1. A markdown title cell - `# Topic`, what it is, complexity table, when to use
   it, then a **mental-model card**: a blockquote with exactly two labelled
   halves, `**Mental model.**` (the one idea unifying the notebook) and
   `**Load-bearing:**` (what breaks if you remove a piece - the part you get
   wrong cold). Use those two labels verbatim so the card is findable by eye in
   every notebook. A notebook holding several major algorithms gets one card per
   algorithm, at the head of each section, rather than one for the file.
2. Optional diagram cell - `![Alt text](images/name.png)`.
3. Alternating markdown/code pairs: the markdown explains the idea and states
   **Time** and **Space**, the code implements it plus its tests.
4. A closing `# Python Built-in: ...` section mapping the hand-rolled structure
   to its stdlib counterpart (`bisect`, `heapq`, `deque`, `defaultdict`,
   `lru_cache`).

Also:

- Notebook filenames are lowercase kebab-case: `binary-search-tree.md`.
- Functions and variables are `snake_case`; classes are `PascalCase`.
- Prefer plain functions taking the structure as the first argument (procedural,
  interview style) over wrapper classes, matching the existing notebooks.
- Standard library only - no production dependencies.
- Python 3.14+, 4-space indent, max line length 80 (`.editorconfig`).
- Favour readability and educational clarity over micro-optimization; comment the
  non-obvious step rather than every line.
- Keep notebooks focused. Split a topic into a new notebook rather than growing
  one past roughly a dozen code cells, and link related notebooks with relative
  markdown links.
- Add a `LEARNING_PATH.md` entry in the right phase for every new notebook.

## Explanation style

The reader is the author returning cold after months. Explain the idea, never the
steps: a per-iteration transcript or a numbered restatement of the loop body is
noise, because the code already says that. Each section should answer, in order:

1. **The reframe** - the question the algorithm is really answering, which is
   often the whole insight.
2. **The mental model** - what the state *means*, not what it does. `prev` is
   "the head of the part already reversed", not "the previous node".
3. **Where it came from** - the naive version and the specific pain that forces
   the fix, so the algorithm arrives as a repair rather than a fact.
4. **Why the clever step is safe** - the moment it throws work away or commits
   irrevocably is where intuition breaks; justify it.
5. **What is load-bearing** - what breaks if you remove this piece.

Write it for a 13-year-old: short sentences, one idea each, no unexplained
vocabulary. Precise terms (*amortized*, *invariant*, *tail call*) are welcome,
but state the plain idea first and attach the term to it afterwards, never the
reverse. No chattiness, and no analogy that doesn't map exactly onto the
mechanism.

Add a worked example only where the shape of the state is itself the insight (a
stack growing and shrinking, stale heap entries) - not for a loop that
increments a counter. Keep concepts in the prose and leave code comments for
local mechanics, since an insight in a trailing comment is invisible when
skimming.
