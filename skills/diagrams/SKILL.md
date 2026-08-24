---
name: diagrams
description: Authoring and exporting the .drawio diagrams in docs/diagrams/ for this repo - house style and palette, when a diagram earns its place, the incremental export pipeline, and the failure modes that pass silently. Use when adding, editing, or exporting a diagram, or when touching scripts/build-diagrams.sh.
---

# Diagrams

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

## When a diagram earns its place

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

## House style

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

## Export output is version-specific, so the export is incremental

PNG bytes depend on the draw.io version: the same source exported by two
different versions gives two different files with identical content. A full
rebuild across a version change therefore rewrites every diagram for no reason,
and each page costs 10-20 seconds of Electron startup, so a full rebuild is also
several minutes.

`scripts/build-diagrams.sh` skips any source whose outputs are already newer than
it. Consequences worth knowing:

- **A diagram you did not touch is never re-exported**, so its bytes stay
  whatever version produced them. The committed PNGs are deliberately a mix of
  versions. They are visually consistent and the content is correct; uniformity
  is not worth megabytes of churn.
- **Editing a source rebuilds only that source**, using whatever draw.io you have.
- `FORCE=1 bash scripts/build-diagrams.sh` rebuilds everything. Only do that when
  you actually want a whole-set re-export, and commit it on its own.
- `--page-index` became **1-based** in v27.0.2 and was 0-based before, so
  multi-page sources fail loudly ("pages are numbered from 1") on older builds.
  The script passes 1-based indices and needs v27.0.2 or newer. An off-by-one
  here silently writes the wrong page into each file, so check a multi-page
  export by eye after touching that code.

## Three failure modes, all of which fail quietly

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
