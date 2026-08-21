# Data Structures and Algorithms in Python

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ospatil/dsapy/HEAD)

## Prerequisites

* **mise** - manages Python version and activates the virtual environment automatically
* **uv** - package manager

## Setup

```bash
uv sync
bash scripts/setup.sh  # generate the paired .ipynb for each Markdown notebook
```

mise will activate the correct Python version and `.venv` automatically when you `cd` into the repo.

## Run

```bash
make start
```

## Notebook format

Notebooks are **authored as Markdown**. Each `notebooks/**/*.md` is the source of truth and the
only version git tracks; [Jupytext](https://jupytext.readthedocs.io/) keeps a paired `.ipynb`
beside it (gitignored) so JupyterLab has something to open. Edit either file and the pair updates
on save.

```bash
make sync   # regenerate the .ipynb pairs, e.g. after a fresh clone
```

A fresh clone therefore contains no `.ipynb` at all until `scripts/setup.sh` or `make sync` has
run. The pairs are also invisible in editors that hide gitignored files - set
`"explorer.excludeGitIgnore": false` in VS Code to see them. Because pairing is driven by
modification time, editing both halves of a pair while JupyterLab is closed makes `make sync`
report a conflict rather than silently pick a winner.

Binder needs the same treatment: `requirements.txt` installs Jupytext and `postBuild` generates
the pairs when the image is built, since the launched session would otherwise show only Markdown
files.

The reason for all of this is that these notebooks are mostly prose, and prose belongs in a format
that diffs and merges. As a side effect the notebooks render readably on GitHub, and there is no
need for `nbstripout`, since Markdown carries no outputs.

## Testing

Each notebook embeds inline `assert`-based tests next to the implementations. To verify every
notebook still runs and all assertions pass, execute them end-to-end:

```bash
make test
```

Each `.md` is converted and executed with `jupytext --execute`; a failing assertion fails the run.

## Approach

Notes you write for yourself have one hard requirement: they have to work when you come back cold
months later. That goal drives the way every notebook is written, so the conventions below are
deliberate rather than stylistic.

**Explain the idea, not the steps.** A transcript of what happens on each iteration, or a numbered
restatement of the loop body, teaches nothing that reading the code doesn't teach faster. What
doesn't survive a long gap is *why* the algorithm is shaped the way it is. So each section aims to
answer, in this order:

1. **The reframe** - the question the algorithm is really answering. Often the whole insight. "For
   each bar, how wide a rectangle can it support at its own height?" makes the monotonic stack
   inevitable.
2. **The mental model** - what the state *means*, not what it does. `prev` is not "the previous
   node", it is the head of the part already reversed. Naming the role makes the code follow.
3. **Where it came from** - the naive version and the specific pain that forces the fix. BFS
   expands in ring order, which only works when every edge costs the same; swap the queue for a
   min-heap and you have Dijkstra. Arriving at an algorithm as a repair beats being handed it.
4. **Why the clever step is safe** - every algorithm has a moment where it throws work away or
   commits irrevocably, and that moment is where intuition breaks. Justify it explicitly.
5. **What is load-bearing** - what breaks if you remove this piece. "Introduce a single negative
   edge and the argument collapses." Cold, you don't forget the steps, you forget which parts are
   structural.

**Write it for a 13-year-old.** Not simplified content - simple language for real content. Short
sentences, one idea each, no unexplained vocabulary. Precise terms like *amortized* or *invariant*
are welcome, but the plain idea comes first and the term is attached to it afterwards, never the
reverse: "the cheap appends pre-pay for the expensive one; that's what *amortized* means." No
chattiness, and no analogy that doesn't map exactly onto the mechanism, since a decorative metaphor
is worse than none - you'll push it further than it goes.

**Every notebook opens with a card.** A short mental-model block right under the title, as a
blockquote with two labelled halves: **Mental model.** is the one idea unifying everything
below, and **Load-bearing:** is what breaks if you remove a piece - the part you'll get
wrong cold. It's what you read when you don't need the whole notebook. A notebook holding
several major algorithms gets one card per algorithm rather than one for the file.

**Worked examples where the shape of the state is itself the insight**, and nowhere else. A trace of
the stack shrinking and growing earns its space; a trace of a loop incrementing a counter does not.

**Code comments explain the local mechanics; concepts live in the prose.** An insight buried in a
trailing comment is invisible when you're skimming.

**Tests double as documentation.** Inline asserts pin down the edge cases the prose claims to
handle, so the claims can't quietly rot.

## Upgrading

### Diagrams

Diagrams are authored as `.drawio` files in `docs/diagrams/` (sketch style) and exported to PNGs in the matching `notebooks/<topic>/images/` folder via the [draw.io](https://www.drawio.com/) desktop app.

```bash
make diagrams
```

A `.drawio` file is mxGraph XML, so a diagram can be written or edited as text and exported headlessly - the desktop app is only the export engine, and opening it in the GUI is optional. A single-page file exports to `<name>.png`; a multi-page file exports one PNG per page as `<name>-<page name>.png`. New diagrams need an entry in the `OUTPUT_MAP` in `scripts/build-diagrams.sh` naming their destination folder. Validate a hand-edited source before exporting, because a bare `&` makes it invalid XML and draw.io will still report success while dropping everything after that point:

```bash
python3 -c "import xml.dom.minidom,sys; xml.dom.minidom.parse(sys.argv[1])" docs/diagrams/<name>.drawio
```

`.github/copilot-instructions.md` carries the full conventions: house style, palette, and the failure modes worth knowing.

`docs/diagrams/legacy/` holds three older `.excalidraw` sources. Two are in use (`bigo` → `big-o.png`, `min-heap`); `analysis` is retained but no longer referenced. They predate the draw.io pipeline and are exported by hand from [excalidraw.com](https://excalidraw.com/).

A diagram is only worth keeping when its spatial arrangement carries something prose can't carry cheaply - a shape changing, a mapping between two layouts, per-level sums. A before/after of an operation whose name already states the outcome does not qualify, and a source with no `OUTPUT_MAP` entry was cut on those grounds.

### Python version

1. Install and pin the new version: `mise use python@<version>` (updates `.mise.toml` automatically)
2. Update `requires-python` in `pyproject.toml` if changing minor version
3. Recreate the venv:

   ```bash
   rm -rf .venv
   uv sync
   ```

### Dependencies

```bash
uv lock --upgrade   # upgrade all packages
uv sync             # install upgraded packages into .venv
```

To upgrade a single package: `uv lock --upgrade-package <package> && uv sync`
