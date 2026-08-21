# Copilot Instructions

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
uv run black .      # format
uv run ruff check . # lint
```

`RECALL.md` is generated from the cards by `scripts/build-recall.py` and must not
be hand-edited; `make test` runs the script in `--check` mode and fails if a card
changed without the page being rebuilt.

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

## Diagrams

Sources are `.drawio` (mxGraph XML) in `docs/diagrams/`, exported to PNG under
`notebooks/<topic>/images/` by `make diagrams`. **No GUI is needed** - write the
XML directly and export headlessly. The draw.io desktop app is only the export
engine.

Workflow for a new diagram:

1. Write `docs/diagrams/<name>.drawio`.
2. Add an `OUTPUT_MAP` entry in `scripts/build-diagrams.sh` naming the
   destination `images/` folder. Without one, the source is not exported.
3. `make diagrams`. Single-page sources become `<name>.png`; multi-page sources
   become one `<name>-<page name>.png` per page.
4. Reference it as `![Alt text](images/<name>.png)`.

### When a diagram earns its place

Only when the spatial arrangement carries something prose cannot carry cheaply:
a shape changing, a mapping between two layouts, per-level sums. A before/after
of an operation whose name already states the outcome does not qualify - a
picture of "insert at front" teaches nothing the function name doesn't, and it
misses the part that is actually hard (the order of the two assignments).

Weak diagrams are not free even once drawn: they train the reader to scroll past
images. A source judged not to earn its place keeps its file but loses its
`OUTPUT_MAP` entry, so it can be revived or redrawn later.

Never degrade a working diagram to bolt on a new point - add a separate source.
Putting a diamond graph into `bfs-vs-dfs` to show the enqueue-marking trap would
have destroyed the visit-order contrast the diagram exists for, because BFS and
DFS visit that graph in the same order.

Replace a notebook's ASCII art only when the diagram strictly supersedes it.
Where compact ASCII is the cheaper carrier (the mirror-image left rotation, say),
keep it and let the diagram cover the case that needs the detail.

### House style

- Every shape and edge: `sketch=1;hachureGap=4;jiggle=2` (this repo's hand-drawn
  look; do not copy `curveFitting=1` from other repos).
- No `html=1` or `convertToSvg=1`. Those matter only for SVG export, and this
  repo exports PNG.
- Palette, standard draw.io pastels, fill/stroke: focus/root `#dae8fc`/`#6c8ebf`,
  good or after `#d5e8d4`/`#82b366`, highlight or the thing that moves
  `#fff2cc`/`#d6b656`, wrong or removed `#f8cecc`/`#b85450`, greyed out or
  discarded `#f5f5f5`/`#999`. Muted text `#999`, secondary text `#666`.
- Tree nodes: `ellipse`, 42-50 px square. Array cells: `rounded=0`, 45x35, spaced
  on a uniform grid so cells can be added programmatically later.
- Index and annotation labels: `text;fontSize=10;sketch=0;fontColor=#999;align=center;`.
- Traces and code-like content: `fontFamily=Courier New` so columns line up.
- Close with a caption in amber italic stating the takeaway, not a restatement of
  the picture.
- No em or en dashes in labels, matching the prose convention.

### Export output is version-specific

PNG bytes depend on the draw.io version, so the same source exported by two
different versions produces two different files with identical content. Pin the
version rather than treating one machine as authoritative:

**draw.io 31.3.1** is what this repo's PNGs are exported with. Any machine on
that version reproduces the same bytes, which is why the images can be
regenerated with `make diagrams` after a checkout instead of being shipped as
several megabytes of binary patch.

Two consequences worth knowing:

- Running `make diagrams` on a machine with a *different* version rewrites every
  output with no content change, and the next export on a matching machine
  rewrites them all back. If you upgrade, upgrade everywhere, and re-export in a
  single commit of its own.
- `--page-index` became **1-based** in v27.0.2 and was 0-based before, so
  multi-page sources fail loudly ("pages are numbered from 1") on older builds.
  `scripts/build-diagrams.sh` passes 1-based indices and therefore requires
  v27.0.2 or newer. An off-by-one here silently writes the wrong page into each
  file, so check a multi-page export by eye after touching that code.

### Three failure modes, all of which fail quietly

- **A bare `&` in an attribute makes the file invalid XML, and draw.io still
  reports a successful export with everything after that point missing.** Write
  `&amp;`, and validate every source before exporting:
  `python3 -c "import xml.dom.minidom,sys; xml.dom.minidom.parse(sys.argv[1])" <file>`
- **A label wider than its cell wraps into the row below.** Always view the
  exported PNG before considering the diagram done.
- **Numbers in diagrams drift from the code.** Simulate anything numeric rather
  than reasoning it out. Two long-standing diagrams here carried wrong values (a
  count array that dropped an element, a level sum of `9cn/19` for `9cn/16`), and
  the first draft of the BFS marking diagram claimed an incorrect visit order.
