---
jupyter:
  jupytext:
    cell_metadata_filter: -all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.19.5
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Cycle Detection

Both variants are [DFS](graph-traversal.md) with one extra piece of bookkeeping, and both
run in **O(V + E)**. The bookkeeping differs because "already visited" means different
things in an undirected and a directed graph - which is the whole story of this notebook.

> **Mental model.** Undirected and directed graphs need different algorithms here, and that
> difference is the notebook. In an undirected graph, bumping into a visited neighbour is
> normal, because it is usually just the edge you walked in on - so you ignore the vertex
> you came from, and any *other* visited neighbour proves there is a second way in. In a
> directed graph, bumping into a visited vertex is also normal: the diamond
> `0→1, 0→2, 1→3, 2→3` reaches 3 twice and has no cycle. So "visited" is too blunt a
> question to ask. The three colours ask a sharper one - is this vertex still on the path
> I am standing on right now?
>
> **Load-bearing:** colour 1 means "on the recursion stack at this very moment", not
> "seen before". That is the only state that proves a cycle. Leave a vertex at colour 1
> after it finishes and every diamond looks like a cycle; drop the parent check in the
> undirected version and every single edge does.


## One question, two prices

DFS splits the edges into the ones it walks down, the **tree edges**, and the ones whose far
end is already visited. A non-tree edge closes a cycle exactly when its far end lies **on the
path you are standing on**: the tree path between the two ends, plus that edge, is the loop.
An edge to one of your own ancestors is called a **back edge**. Both algorithms below ask that
one question. They differ only in what it costs to answer.

In an undirected graph it is free, because no non-tree edge can join two separate branches.
Take any edge `u-x` and suppose `u` is discovered first. The edge sits in `u`'s adjacency
list, so it gets scanned while `u` is still on the stack: either `x` is unvisited and becomes
`u`'s child, or `x` was discovered by some other route in the meantime. Either way `x` is
discovered before `u` finishes, which makes it a descendant of `u`. Every edge therefore
joins two vertices on one root-to-leaf path, so **"visited" already means "on my path"** and
there is nothing left to distinguish.

That leaves exactly one false positive. Every undirected edge is stored twice, so the first
thing DFS at `x` sees is `x-u` pointing straight back at its own parent - the tree edge it
just walked in on, not a second route. Exclude that one edge and the rule is complete.

A directed graph loses the free ride. The diamond `0→1, 0→2, 1→3, 2→3` reaches 3 from two
different branches, and the second arrival is a **cross edge**, not a cycle. So "visited" is
now a statement about history, and history cannot separate a cycle from a shortcut. Ancestry
has to be carried explicitly, which is what the colours do: one bit says "seen", and seen is
not the question.

So the two rules are not arbitrary; each is the cheapest question its graph allows:

| | What proves a cycle | Why |
|---|---|---|
| Undirected | a visited neighbour that is not the parent | visited already means same path, so only the edge walked in on needs excluding |
| Directed | a neighbour still on the recursion stack | visited means nothing, so the path is tracked by hand |


## Undirected graph: parent tracking

The naive rule "a visited neighbour means a cycle" fires on every edge in the graph, because
of the double storage above: `dfs(x, u)` always sees `u` sitting in `x`'s list. The fix is to
pass the vertex the call came from and skip it. `-1` is the sentinel parent for a root, since
no vertex has that index.

Worth knowing what that exclusion actually says. It is written `v != parent`, so it excludes
a **vertex**, not the specific edge that was traversed. In a simple graph those are the same
thing, since one edge joins `u` and `v` and no vertex joins itself. Two edge cases come out
of the gap between them:

- **A self loop is caught**, because no vertex is ever its own parent. At the root, `v == u`
  and `parent == -1`, so the check fires. This is the one place the sentinel value matters:
  make it a real index like `0` and the self loop at vertex 0 goes silently undetected while
  the triangle and every other test still pass.
- **A parallel pair `u=v` is caught, but from the upper end.** Standing at `v`, both copies
  of `u` look like the parent and both get skipped. The report comes when DFS returns to `u`
  and meets the second copy of `v` in `u`'s own list: visited now, and not `u`'s parent.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. `visited[u] = True` on entry, and **never cleared** - it records history only.
   Ancestry is not stored anywhere, it comes free from the argument in step 2.
2. Every call carries the vertex it came from as `parent`; the outer loop starts
   each component with `parent = -1`. **The sentinel must not be a real vertex
   index:** with `0`, the graph `[[0]]` reports no cycle.
3. The outer loop must try every vertex, or a cycle in a second component is
   never reached.
4. Unvisited neighbour: recurse, and **propagate the result up** with
   `if dfs(v, u): return True`. Calling `dfs(v, u)` bare discards it, and the bug
   hides: the triangle `0-1-2-0` still returns `True`, while `0-1, 1-2, 1-3, 2-3`
   returns `False`.
5. Visited neighbour: cycle **only if `v != parent`**. Drop that and the two-edge
   tree `0-1, 0-2` reports a cycle.
6. Falling out of the loop means every neighbour was a child or the parent, so
   return `False`.

```python
def has_cycle_undirected(adj):
    """Detect a cycle in an undirected graph using DFS with parent tracking."""
    visited = [False] * len(adj)

    def dfs(u, parent):
        visited[u] = True
        for v in adj[u]:
            if not visited[v]:
                if dfs(v, u):
                    return True
            elif v != parent:  # visited and not the parent -> cycle
                return True
        return False

    for u in range(len(adj)):
        if not visited[u] and dfs(u, -1):
            return True
    return False


def test_has_cycle_undirected():
    # triangle 0-1-2-0
    assert has_cycle_undirected([[1, 2], [0, 2], [0, 1]]) is True
    # square 0-1-2-3-0: the closing edge is only reached at the last vertex
    assert has_cycle_undirected([[1, 3], [0, 2], [1, 3], [0, 2]]) is True
    # tree 0-1, 0-2
    assert has_cycle_undirected([[1, 2], [0], [0]]) is False
    # path 0-1-2-3: every visited neighbour is the parent
    assert has_cycle_undirected([[1], [0, 2], [1, 3], [2]]) is False
    # empty, single-vertex and edgeless graphs
    assert has_cycle_undirected([]) is False
    assert has_cycle_undirected([[]]) is False
    assert has_cycle_undirected([[], [], []]) is False
    # self loop: caught because no vertex is its own parent
    assert has_cycle_undirected([[0]]) is True
    assert has_cycle_undirected([[1], [0, 2], [1, 2]]) is True  # loop at 2
    # parallel edge 0=1 - a cycle in a multigraph, reported from vertex 0
    assert has_cycle_undirected([[1, 1], [0, 0]]) is True
    # cycle hides in the second component - the outer loop must reach it
    assert has_cycle_undirected([[1], [0], [3, 4], [2, 4], [2, 3]]) is True
    # forest of two trees
    assert has_cycle_undirected([[1], [0], [3], [2]]) is False


test_has_cycle_undirected()
```

## Directed graph: three colors

Parent tracking does not transfer, and not because it is too weak. It is answering a question
this graph never asks: `u → v` does not store a reverse edge, so there is nothing to exclude,
and `0 → 1, 1 → 0` is a genuine cycle that excluding the parent would hide.

What is needed instead is the ancestry that undirected DFS handed over for free. A vertex has
three genuinely different positions relative to the current walk, which is one more than a
boolean can hold:

| Color | Meaning |
|---|---|
| 0 | unvisited |
| 1 | on the current recursion stack (in progress) |
| 2 | fully explored, everything below it is done |

Colour 1 is the recursion stack itself, written down. A neighbour at colour 1 is an ancestor,
the edge to it is a back edge, and that is a cycle.

The step that feels like cheating is ignoring colour 2, so here is why nothing escapes. Take
any cycle and look at whichever of its vertices DFS discovers first, call it `x`. The rest of
the cycle is reachable from `x` along the cycle itself, and none of it was visited at the
moment `x` was discovered, so DFS reaches all of it from inside `x`'s own call: every other
vertex on the cycle becomes a descendant of `x` and finishes before `x` does. That includes
`y`, the vertex sitting just before `x` on the cycle, so `y` scans its edge `y → x` while
still inside `x`'s call, which is while `x` is still colour 1. **The closing edge of a cycle
is always examined from below, while the top of the cycle is still on the stack**, so a
colour-2 vertex can only belong to a cycle that this rule has already caught.

Both halves of that, the safe skip and the catch, happen in one walk on
`adj = [[1, 2, 3], [2], [], [0]]`, which is `0 → 1`, `0 → 2`, `0 → 3`, `1 → 2`, and
`3 → 0`:

```
each row shows the whole colour array after the step, vertex 0 leftmost
indentation is recursion depth

dfs(0)                [1, 0, 0, 0]
  dfs(1)              [1, 1, 0, 0]   edge 0 → 1 finds colour 0
    dfs(2)            [1, 1, 1, 0]   edge 1 → 2 finds colour 0
    2 finishes        [1, 1, 2, 0]   no outgoing edges, so 2 turns colour 2
  1 finishes          [1, 2, 2, 0]
edge 0 → 2 sees 2     [1, 2, 2, 0]   skipped, not re-explored, not reported
  dfs(3)              [1, 2, 2, 1]   edge 0 → 3 finds colour 0
  edge 3 → 0 sees 1   [1, 2, 2, 1]   ancestor still on stack, cycle 0 → 3 → 0
```

Vertex 0 holds colour 1 across every row, which is what makes `3 → 0` readable as a back
edge at the moment it is scanned. Vertex 2 is reached twice by two different parents and is
not on the stack for the second visit, so its colour 2 is exactly the distinction a boolean
`visited` cannot draw.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. `color = [0] * len(adj)`, three states as tabled above. `color[u] = 1` is the
   first line of the call, `color[u] = 2` the line **after** the neighbour loop.
   Those two assignments bracket exactly the interval `u` spends on the stack.
2. **The `2` must sit outside the loop.** Inside it, a vertex with no outgoing
   edges never runs the loop body and so stays at 1 forever: on `[[], [0]]`,
   which is the single edge `1 → 0`, that reports a cycle that does not exist.
3. Neighbour at `1`: return `True`. At `0`: recurse and propagate with
   `if dfs(v): return True`. At `2`: **skip it**, no recursion, no report.
4. **Never reset a colour to `0` on the way out.** Detection stays correct, but
   colour 2 is the memo that keeps this linear; without it the walk enumerates
   paths instead of visiting vertices, and a 49-vertex chain of diamonds goes
   from 49 calls to 1,048,449.
5. No `parent` argument, and no `visited` list beside the colours. Colour 0
   already means unvisited.
6. Outer loop over every vertex, for the same reason as the undirected version.

```python
def has_cycle_directed(adj):
    """Detect a cycle in a directed graph using DFS with 3 colors."""
    # 0 = unvisited, 1 = in recursion stack, 2 = fully processed
    color = [0] * len(adj)

    def dfs(u):
        color[u] = 1  # mark as in-progress
        for v in adj[u]:
            if color[v] == 1:  # back edge -> cycle
                return True
            if color[v] == 0 and dfs(v):
                return True
        color[u] = 2  # fully processed
        return False

    for u in range(len(adj)):
        if color[u] == 0 and dfs(u):
            return True
    return False


def test_has_cycle_directed():
    # cycle 0 -> 1 -> 2 -> 0
    assert has_cycle_directed([[1], [2], [0]]) is True
    # 0 -> 1, 1 -> 0: a real cycle, and the case parent tracking would hide
    assert has_cycle_directed([[1], [0]]) is True
    # DAG 0 -> 1 -> 2
    assert has_cycle_directed([[1], [2], []]) is False
    # self loop
    assert has_cycle_directed([[0]]) is True
    # diamond 0->1, 0->2, 1->3, 2->3: vertex 3 is visited twice but finished,
    # so a plain "visited" check would report a false cycle here
    assert has_cycle_directed([[1, 2], [3], [3], []]) is False
    # cross edge 2 -> 1 into a finished branch: same false positive, no diamond
    assert has_cycle_directed([[1, 2], [], [1]]) is False
    # 1 -> 0 alone: 0 is a sink, and must still end up colour 2
    assert has_cycle_directed([[], [0]]) is False
    # parallel edges 0 -> 1 twice: not a cycle in a directed graph
    assert has_cycle_directed([[1, 1], []]) is False
    # empty and single-vertex graphs
    assert has_cycle_directed([]) is False
    assert has_cycle_directed([[]]) is False
    # two components: 0 -> 1 acyclic, 2 -> 3 -> 2 not
    assert has_cycle_directed([[1], [], [3], [2]]) is True
    assert has_cycle_directed([[1], [], [3], []]) is False


test_has_cycle_directed()
```

## Other Approaches

- **Undirected, iteratively:** [Union-Find](union-find.md) - if both
  endpoints of an edge already share a root, that edge closes a cycle.
- **Directed, without recursion:** run Kahn's algorithm from
  [Topological Sort](topological-sort.md) - if the result holds fewer than
  V vertices, a cycle blocked the rest.
