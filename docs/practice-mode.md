# Practice mode - spec

Not built. This is the design, the reasoning behind it, and what "done" means, so
the work can start cold without re-deriving any of it.

## The gap

The repo has 30 notebooks, 174 Python cells, **118 `test_*` functions**, 170
implementation functions and 33 mental-model cards. Between them they support two
of the three things memory needs, and neither of the two is the one that rots:

| Mode | Supported by | Trains |
|---|---|---|
| Recognition | the notebooks, `LEARNING_PATH.md` | "yes, I have seen this" |
| Recall of the idea | `RECALL.md`, cards behind `<details>` | "I can say why it works" |
| **Production of the code** | **nothing** | **"I can write it from an empty cell"** |

The card tells you `hi` starts at `len(arr)` and not `len(arr) - 1` for
`lower_bound`. It does not catch that your fingers wrote `len(arr) - 1` anyway.
Reading a card and writing the loop are different acts, and only the second one
fails in the way that matters.

The second gap is scheduling. `LEARNING_PATH.md` is a single-pass checklist with
no notion of *when to come back*, so practice collapses into reopening whichever
notebook was open last time.

The thing that makes this cheap: **every implementation cell already carries its
own `test_<name>()` directly below it.** A grader for 118 items exists. Nothing
needs to be authored to make practice checkable - only removed.

## Scope

Two pieces. A generator that strips the notebooks into practice notebooks, and a
ledger that decides what to strip today.

Two further ideas were considered and deferred rather than dropped; they are at
the bottom with the reasons, so they are not rediscovered as if new.

## Piece 1: `scripts/build-practice.py`

Derives `practice/<topic>/<name>.md` from each notebook: the prose and the card
stay, the implementation bodies go, the tests stay verbatim. You open it in
JupyterLab, type the implementation, run the cell, and the asserts grade you.

**Generated, gitignored, never committed** - the same contract as the paired
`.ipynb` and as `RECALL.md`. A committed practice notebook is a second copy of
every algorithm in the repo that drifts the moment a notebook is edited, and a
half-finished attempt is worse: it is wrong code sitting in git, indistinguishable
from a real implementation to anything that greps. Add `practice/` to
`.gitignore`, next to the `notebooks/**/*.ipynb` rule and for the same reason.

### Input

`notebooks/**/*.md`, excluding `*checkpoint*` and excluding a `SKIP` set: the six
`analysis/` notebooks. They hold 0 test functions between them - their exercise is
"name the complexity of this loop", not "write this function", and
`00-quick-reference.md` is already the answer key. That is a different drill; see
Deferred.

### Per-cell transformation

A fenced `python` cell is copied **verbatim** when any of these holds:

- it defines no function other than `test_*`;
- its heading starts `# Python Built-in` (nine such sections; they demonstrate
  `bisect`, `heapq`, `deque`, `lru_cache` and print rather than assert - there is
  nothing to practice and stripping them breaks the cell);
- every function it defines is scaffolding (below).

Otherwise, each implementation function's body is replaced by `...` and every
`def test_*` plus its trailing call is kept exactly as written.

### Resolve strip targets by name across the notebook, not per cell

The obvious rule - "strip a function that has a test in the same fence" - is
wrong, and `avl-tree.md` is the counterexample: cells 1-4 define `height`,
`rotate_right`, `rebalance` and `insert` with no test in the fence, because their
tests arrive several cells later. Per-cell matching hands you the AVL rotations
already written, which is most of the notebook's value.

The rule is: **collect the names called from any `def test_*` body anywhere in the
notebook, then strip those wherever they are defined.** This subsumes the AVL case
without special-casing it. The other 31 cells that define a function with no
co-located test are all scaffolding, `Python Built-in` demos, or analysis
notebooks, and are already handled above.

### Scaffolding is an explicit `(notebook, name)` allowlist

Tests call their helpers too, so name-resolution alone would strip `to_list` and
`create_test_bst` and leave the practice notebook unable to run. Those must
survive.

**A name-prefix heuristic for this does not work, and the repo has the
counterexamples ready.** `build_heap` is the O(n) heap construction the notebook
exists to teach. `make_set` is a union-find primitive. `is_balanced` is the
balanced-parentheses algorithm. All three would be preserved by a
`build_*`/`make_*`/`is_*` rule, and all three are exactly what you came to
practice.

Worse, the same name means different things in different notebooks: `build_adj`
is the lesson in `graph-basics.md` and reused plumbing in `graph-traversal.md`. So
the allowlist is keyed by `(notebook, function)`, not by name, and each entry
carries a one-line reason - the same shape as `EXEMPT` in `build-recall.py`, for
the same reason: an unexplained exception becomes permanent.

Starting set, to be confirmed against the file while implementing:

- `to_list` (three linked-list notebooks) - turns a list into a Python list so the
  asserts can compare
- `create_test_bst`, `create_test_tree`, `create_trie` - fixed fixtures the tests
  are written against
- `is_topological`, `is_min_heap`, `is_max_heap`, `is_partitioned`,
  `is_avl_balanced` - property checkers, used because output order is not unique
  (`AGENTS.md`, Testing, names the first two)
- `build_adj` **in `graph-traversal.md` only**

### Levels

One flag, `--level`, because the right amount of help depends on how the card went
two minutes ago, not on which notebook it is:

| Level | Prose | Signature | Docstring | Tests |
|---|---|---|---|---|
| `hint` (default) | kept | kept | kept | kept |
| `cold` | card only | kept | dropped | kept |
| `blank` | card only | **dropped** | dropped | kept |

`blank` emits no stub at all - just the card and the tests. The test calls the
function, so the signature is recoverable from the assert, which makes
reconstructing it part of the exercise rather than a guessing game.

### Output must stay executable

The generated `.md` keeps the jupytext YAML header so `make sync` pairs it like
any other notebook, and `practice/` mirrors the `notebooks/` folder names.

## Piece 2: the ledger

`practice/log.jsonl`, append-only, one object per attempt:

```json
{"date": "2026-08-30", "item": "trees/heap.md:sift_down", "level": "cold",
 "outcome": "hint", "note": "swapped the child comparison, sifted up instead"}
```

`outcome` is one of `clean` / `hint` / `failed`. Re-queue by Leitner box - `clean`
→ 3 weeks, `hint` → 1 week, `failed` → next session. Not SM-2: at 118 items the
scheduler's precision is far below the noise in your own grading, and a half-page
of interval arithmetic is a thing to maintain rather than a thing to use.

**The note is the load-bearing field, not the date.** "Off-by-one in the `hi`
update", "marked visited on dequeue instead of enqueue" *is* the curriculum; the
dates are only bookkeeping around it. A ledger that records outcomes and not notes
tells you what you failed and never why, which is the half you cannot reconstruct
later.

The log is gitignored with the rest of `practice/`. It is a record of your own
misses, it merges badly, and nothing in the repo should depend on it.

## Sequencing rules the tooling has to respect

These decide whether the practice works at all, and two of them constrain what
`make drill` may print:

- **Never queue in `LEARNING_PATH.md` order.** That order is right for learning
  and actively wrong for practice: merge sort primes quick sort's partition, so
  you drill a warm cache and read the result as retention. The selection must
  interleave topics - one graph, one tree, one technique.
- **Tier the items.** Uniform coverage of 118 functions is the wrong allocation.
  Roughly 40 stay hot (binary search variants, BFS/DFS, BST delete, heap sift, the
  two-pointer patterns, DP intro); the rest - radix sort, circular linked lists -
  come round quarterly. The tier list is hand-written and lives in the script.
- **The card comes first, out loud, before anything is opened.** It is two minutes
  and it sets the level for the rest of the session.

## Commands

```bash
make practice            # regenerate practice/ at the default level
make practice LEVEL=cold # ... or a harder one
make drill               # print what is due, interleaved; one line per item
```

`make practice` must be safe to re-run. It regenerates from the notebooks, so it
**overwrites** anything typed into `practice/`; say so in the target's comment,
because losing a half-finished attempt to a habitual `make practice` is a mistake
worth designing out rather than remembering.

## Done means

1. `make practice` produces a `practice/` tree that `make sync` pairs and every
   notebook in it executes as far as the first stripped function - and fails there
   on an assert, not on a `NameError` or a `SyntaxError`. A practice notebook that
   dies of a missing helper is a broken generator, not a hard exercise.
2. Restoring every stripped body from the source reproduces a tree that passes
   `make test`. This is the anti-drift check, and it must compare *executed
   results*, not text: it is the only thing standing between this and a generator
   that silently stops stripping something.
3. `avl-tree.md` cells 1-4 come out stripped - the specific case a per-cell rule
   gets wrong.
4. `build_heap`, `make_set`, `is_balanced` and `graph-basics.md`'s `build_adj`
   come out stripped; `to_list`, `create_test_bst` and the `is_*` property
   checkers come out intact.
5. `practice/` is gitignored and `git status` is clean after a run.
6. `make test` is unchanged and still passes. Practice mode adds a target; it
   does not become something the build depends on.

## Deferred, with reasons

- **Perturbation drills.** Mutate one load-bearing line - `lo <= hi` → `lo < hi`,
  mark visited on dequeue, drop path compression - predict which assert fails and
  why, then run. The repo is unusually ready for it: every card's
  **Load-bearing:** half already names the target, and the mutations are
  mechanically generatable. It trains debugging rather than typing, so it
  alternates with the above rather than replacing it. Deferred only because the
  generator is the prerequisite - the mutation script wants the same cell parser.
- **Cue-first drilling (problem → technique).** Problem statements with the topic
  label stripped; name the structure and justify it before writing anything. The
  real miss is not writing a monotonic stack, it is failing to see that a problem
  is monotonic-stack-shaped, and organising notebooks by structure trains the
  retrieval in the wrong direction. Deferred because it is the one item here with
  real authoring cost: nothing in the repo can generate the problem statements.
- **A complexity quiz over `analysis/01-05`.** The drill those notebooks actually
  want, and the reason they are in `SKIP`. Different generator, different output
  shape - a question bank, not a stripped notebook.

## Trap

`*.spec` is gitignored - it arrives with the PyInstaller block in the generated
section of `.gitignore`, several hundred lines above anything hand-written. A
design document named `practice.spec` would be invisible to `git add -A` and
nothing would report it. Hence `.md`.
