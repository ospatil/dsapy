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


## Undirected graph: parent tracking

The naive rule "a visited neighbour means a cycle" is wrong here, because every edge is
stored twice: DFS at `v` always sees the parent `u` it just came from.

So the rule becomes: a visited neighbour that is **not the parent** was reached by some
other route, and two routes to the same vertex close a cycle.

`-1` is the sentinel parent for a root, since no vertex has that index.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Ordinary DFS, except every call carries **the vertex it came from** as
   `parent`. The outer loop starts each component with `parent = -1`.
2. Unvisited neighbour: recurse, and propagate a `True` straight up.
3. Already-visited neighbour: a cycle **only if `v != parent`**.
4. **That check exists because an undirected edge is stored twice.** Standing on
   `1` after arriving from `0`, the list `adj[1]` contains `0`, which is visited.
   Without the exclusion every single edge reports a cycle: the two-edge tree
   `0-1, 0-2` comes back `True`.
5. The outer loop must cover every vertex, or a cycle hiding in a second
   component is missed.
6. **Return values have to be propagated deliberately.** `dfs(v, u)` is wrapped
   in an `if` rather than called bare, since a `True` found deep in the recursion
   is otherwise discarded.

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
    # tree 0-1, 0-2
    assert has_cycle_undirected([[1, 2], [0], [0]]) is False
    # empty and single-vertex graphs
    assert has_cycle_undirected([]) is False
    assert has_cycle_undirected([[]]) is False
    # cycle hides in the second component - the outer loop must reach it
    assert has_cycle_undirected([[1], [0], [3, 4], [2, 4], [2, 3]]) is True
    # forest of two trees
    assert has_cycle_undirected([[1], [0], [3], [2]]) is False


test_has_cycle_undirected()
```

## Directed graph: three colors

Parent tracking does not transfer, because in a directed graph the thing it protects against
is not the problem. The question has to change shape: "have I seen this vertex?" is about
*history*, and history cannot tell a cycle from a shortcut. "Is this vertex on the path I am
standing on right now?" is about the *present*, and only that distinguishes them.

That is why one bit is not enough. A vertex needs three states, because it can be in three
genuinely different situations relative to the current walk:

| Color | Meaning |
|---|---|
| 0 | unvisited |
| 1 | on the current recursion stack (in progress) |
| 2 | fully explored, everything below it is done |

Meeting a color-1 vertex means an edge points back to one of your own ancestors, and an
edge like that is exactly a cycle. It has a name, a **back edge**. Meeting color 2 is a
forward or cross edge: harmless.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

Three states, not two: `0` untouched, `1` on the current path, `2` finished.

1. Set `color[u] = 1` on entry, and `color[u] = 2` **after** the neighbour loop.
2. Neighbour with `color == 1`: cycle. It is an ancestor on the path you are
   standing on right now, so the edge closes a loop.
3. Neighbour with `color == 0`: recurse.
4. Neighbour with `color == 2`: **ignore it.** It is finished, reachable from
   here, and provably not on the current path.
5. **State `2` is the whole reason this is not just `has_cycle_undirected`.** A
   plain visited flag cannot tell "I am inside this vertex's call" from "I
   finished it earlier", and reports the diamond `0->1, 0->2, 1->3, 2->3` as
   cyclic even though it is a DAG.
6. No `parent` argument here. In a directed graph the reverse edge is not
   implied, so `u -> v` and `v -> u` really is a cycle.

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
    # DAG 0 -> 1 -> 2
    assert has_cycle_directed([[1], [2], []]) is False
    # self loop
    assert has_cycle_directed([[0]]) is True
    # diamond 0->1, 0->2, 1->3, 2->3: vertex 3 is visited twice but finished,
    # so a plain "visited" check would report a false cycle here
    assert has_cycle_directed([[1, 2], [3], [3], []]) is False
    # cycle in the second component
    assert has_cycle_directed([[1], [], [3], [2]]) is True


test_has_cycle_directed()
```

## Other Approaches

- **Undirected, iteratively:** [Union-Find](union-find.md) - if both
  endpoints of an edge already share a root, that edge closes a cycle.
- **Directed, without recursion:** run Kahn's algorithm from
  [Topological Sort](topological-sort.md) - if the result holds fewer than
  V vertices, a cycle blocked the rest.
