# Handoff

Why the repo is set up the way it is, for picking it up cold in a new session -
in Kiro CLI, Claude Code, or any other agent. `AGENTS.md` carries the
*conventions*; this file carries the *reasoning* behind them, plus whatever is
still open.

Deliberately not a status page. Branch position, commit lists, diffstats and test
results belong to `git log`, `git status` and `make test`, which report them
accurately for free - restating them here only produces a file that lies, and it
did exactly that twice in one afternoon. What those commands cannot tell you is
intent: what was decided, what was ruled out and why, what is still undecided.
That is everything below.

## Open threads

- **Pin black's target version, or don't.** `black --check` warns that Python
  3.14 cannot parse code formatted for 3.15, because `requires-python` is
  `>=3.14` while black assumes a newer target. Setting
  `target-version = ["py314"]` in `pyproject.toml` silences it. Left alone so far
  because black only touches the four `.py` files, none of which are lesson
  content.
- **`config/jupyter_notebook_config.py` is unformatted.** It is the one file
  `black` would rewrite. Reformatting it is safe but nobody has needed to.

## Decisions and traps

### The card convention was documented in three places and enforced in none

`scripts/build-recall.py` used to skip a notebook with no cards in silence
(`if not cards: continue`), so `make test` could detect a *stale* `RECALL.md` but
never an *absent* card - which is how five analysis notebooks quietly went
without one. `--check` now fails on absence too. A notebook that genuinely
warrants no card goes in `EXEMPT` in that script, with the reason written down.

`notebooks/analysis/00-quick-reference.md` is the only entry: it is a condensed
field guide over notebooks 01-05, so its one idea *is* the page.

### Why the agent setup is symlinks rather than copies

The conventions doc lived at `.github/copilot-instructions.md`, where the word
"Copilot" appeared exactly once in 243 lines - the H1. Nothing in it was
vendor-specific, but Kiro never loaded it (Kiro reads `AGENTS.md`, `README.md`,
`.kiro/steering/`, `.kiro/skills/`), so the most detailed statement of the
repo's conventions was invisible to the tool being used.

```
AGENTS.md                          always-loaded conventions (real file)
CLAUDE.md                       -> AGENTS.md
skills/diagrams/SKILL.md           on-demand diagram skill (real file)
.claude/skills/diagrams/SKILL.md -> ../../../skills/diagrams/SKILL.md
.kiro/skills/diagrams/SKILL.md   -> ../../../skills/diagrams/SKILL.md
```

**Edit the real file, never a link.** Claude Code reads `CLAUDE.md` and not
`AGENTS.md`, and the symlink is the bridge Anthropic's own docs recommend. Skills
use identical `SKILL.md` + `name`/`description` frontmatter in both tools, so only
the directory differs. The diagram section is split out because Anthropic targets
under 200 lines per `CLAUDE.md` and warns that longer files reduce adherence - the
original 243 exceeded it, and the diagram detail only matters while drawing.
Confirmed in both tools that the skill costs only its summary line until invoked.

### `ruff format` would rewrite every notebook

See the warning in `AGENTS.md` under Commands - that copy is authoritative. Short
version: it formats Python inside Markdown fenced blocks, so it flattens the
aligned trailing comments the lessons depend on. `black` is deliberate.

### Patches travel as gzipped base64, not raw `.patch`

```bash
# create (from commits; use --cached for staged-but-uncommitted work)
git diff HEAD~1 HEAD --binary | gzip -9 | base64 > latest.patch.gz.b64

# apply
base64 -d < latest.patch.gz.b64 | gunzip > latest.patch
git apply latest.patch
```

`.gitignore` wildcards `*.patch`, `*.patch.gz.b64` and `*.tar.xz.b64` so that
`git add -A` cannot sweep one into the commit and double the size of the very
patch being generated.

Rules learned the hard way:

- **`--binary` is mandatory whenever a PNG is involved.** Plain `git diff` emits
  only a "Binary files differ" placeholder, so the patch applies without the
  image and nothing complains.
- **Verify by round trip in a detached worktree, and assert the baseline differs
  first.** `git apply --check` against an equal or missing ref passes vacuously
  and prints success while comparing nothing; a failed `cd` produces the same
  false pass. Compare `git write-tree` on both sides - equal hashes prove the
  reconstruction is byte-identical, which eyeballing a diffstat does not.
- **For a wholesale diagram re-export, ship the images as an archive rather than
  a diff.** A diff carries the removed content verbatim, and rasterised image
  data is already compressed, so removals are what blow up the size. Measured on
  a 40-diagram re-export: 18.7 MB raw, of which 11.86 MB was image data, still
  14.2 MB after gzip. The same change shipped as `tar -cf - <dir> | xz -9 |
  base64` was 787 KB. Only worth it when most images changed; for a handful, the
  diff is smaller.

### Three `.drawio` sources have no `OUTPUT_MAP` entry on purpose

`binary-search-narrowing`, `sll-insert-delete`, `stack-vs-queue`. Their PNGs were
deleted in `7e84752`, the same commit that introduced `OUTPUT_MAP`, and
`skills/diagrams/SKILL.md` codifies the practice: a source judged not to earn its
place keeps its file but loses its entry, so it can be revived later. Not an
unfinished loose end - don't "fix" it by re-adding them.

### `6fd5ad3 upgrade deps` upgraded nothing

Every changed line in `uv.lock` is a `dist =`/`wheels =` entry gaining an
`upload-time` field, plus `revision = 2 -> 3`. It is a lockfile format migration
with zero version changes, so it carries no dependency drift and needs no
retesting.

### `.ipynb_checkpoints/` directories are harmless

They exist under `trees/`, `stacks-and-queues/` and `linked-lists/`. Gitignored,
and excluded from `make sync`, `make test` and the recall build. Local noise only.
