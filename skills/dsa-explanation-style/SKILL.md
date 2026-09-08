---
name: dsa-explanation-style
description: Use this style whenever explaining an algorithm, data structure, or function during DSA/interview-prep study - especially when asked to "explain", "walk through", "why does this work", or to explain something "independently"/"on its own" without leaning on a related concept. Goal is intuition drilled into memory, not a narrated code read-through.
---

# DSA explanation style

The reader already knows how to code. They do not need syntax explained. What
they need is the ONE idea that makes the algorithm inevitable, so it survives
in memory under interview pressure, not a description of what each line does.

## Structure, in order

1. **Anchor idea first.** Before any code or step-by-step, state in 1-2
   sentences the single insight/invariant that makes everything else fall
   out. If you can't compress it to one sentence, you haven't found it yet,
   keep looking, don't skip this step.
2. **Name the state in plain English.** For every variable that isn't the
   obvious input (an extra pointer, an accumulator, a running best-so-far),
   give it a plain-English identity tied to what it *represents*, before it
   appears in any code. `curr` is "where the walk currently stands," `parent`
   is "the last real node it stood on," not "the current node" and "the
   previous node." Do this before the first snippet, so the reader has the
   vocabulary before the code starts using it.
3. **Explain the "why," not the "what."** Don't narrate steps ("first we do
   X, then Y"). Explain why each step is *necessary*, what breaks if you
   skip it or do it in the other order. Steps described without their reason
   don't stick.
4. **Tie to real code inline.** Quote small snippets (a line or two) exactly
   where you're pointing at them, rather than describing logic in the
   abstract and dropping a full code block afterward disconnected from the
   prose.
5. **Name the trap.** State the plausible-looking wrong way to do it, and
   exactly why it fails. A trap that's been named is a trap that gets
   recognized later; an unnamed correct method gets forgotten and
   reinvented incorrectly.
6. **Compress to one memorizable sentence at the end.** Something that could
   be recalled cold, without re-deriving the explanation. This is the line
   that's actually meant to stick.
7. **Offer exactly one next step** (trace an example, quiz, move to the next
   topic), never an open-ended "let me know if you have questions."

## Independence rule

If asked to explain something "on its own," "independently," or "without
comparing to X," do not use X as scaffolding at all, even implicitly (no
"like X but..."). Rebuild the explanation from the raw problem constraints
as if X were never mentioned. If the truest explanation of Y actually
requires contrasting with X, name that as a limitation instead of quietly
leaning on X anyway.

## Tone and format

- Terse and confident. No "I think", "basically", "essentially", "so
  basically" hedges.
- Don't restate the question or re-summarize what was just asked.
- No disclaimers, no "note that this is a simplification," no over-caveating.
- Bold sparingly, only the single most load-bearing phrase in a
  paragraph, not whole sentences and not every paragraph.
- Short paragraphs and bullets over long prose blocks.
- Skip basic definitions unless the definition itself is the load-bearing
  point (e.g., "invariant" is worth defining precisely; "loop" is not).
- No en or em dashes. Use commas, hyphens, or a full stop instead.

## Example of the difference

**Narrated (avoid):**
> First we set parent and curr to None and root. Then we loop while curr is
> not None. Inside the loop we set parent to curr. Then we check if curr's
> data equals the target...

**Intuition-first (use):**
> `curr` is where the walk currently stands. `parent` is the last real node
> it stood on, one step behind. A pointer only tells you what's ahead, never
> what's behind, and attaching a new node requires "behind": you can't link
> to `None`. Recursion gets "behind" for free from the call stack; without
> one, you carry it yourself, one step delayed, in `parent`.

## Worked example in this repo

`notebooks/trees/binary-search-tree.md`, section "Insert, iteratively," is
the reference instance of this style: the invariant reframed as "the one gap
consistent with every split above it," `curr`/`parent` named before the code,
the trap named inline in the recipe, and no line repeated between the prose
and the recipe.
