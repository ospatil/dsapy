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

# Topological Sort

Linear ordering of vertices in a **DAG** such that for every edge (u, v), u
comes before v.

**Applications:** Task scheduling, build systems, course prerequisites.

**Only possible for DAGs** - if there's a cycle, no topological order exists. See
[Cycle Detection](cycle-detection.md).

## Two approaches

The definition is a constraint on pairs, not a formula for a list: for every edge `u → v`,
`u` sits somewhere before `v`. Turning a constraint into a procedure means picking an end to
work from, and the two ends give the two algorithms.

Work from the **front** of the output and the question is "who can go next?". A vertex is
ready when nothing still unplaced points at it. Count how many edges arrive at each vertex,
emit the zeros, and each emission releases whatever it pointed at. That is **Kahn's
algorithm**: readiness is the whole idea, and the in-degree count is the whole state.

Work from the **back** and the question inverts to "when am I allowed to be placed?". A
vertex can be placed only once everything reachable from it is placed. DFS already computes
that instant and calls it *finishing*, so the answer needs no separate bookkeeping - record
the order vertices finish in, then reverse it. That is the **DFS-based** version.

**Time:** O(V + E) for both.

> **Mental model.** An ordering exists only because the graph has no cycles, so "sort this
> DAG" and "does this graph have a cycle?" are one question asked twice. Kahn's algorithm
> makes that literal. It emits a vertex the moment nothing points at it any more, and
> vertices trapped in a cycle keep each other pointed at forever, so fewer than V vertices
> come out. The short answer *is* the cycle report.
>
> **Load-bearing:** the DFS version works because a vertex is appended only once
> everything reachable below it has finished. That builds the order backwards, so
> reversing the finish order is what makes every edge point forwards. Append on entry
> instead of on exit and the guarantee is gone.


## Checking an order

The constraint orders pairs joined by an edge and says nothing about any other pair, so a DAG
usually admits many valid orders. The two implementations below demonstrate this on the same
six-vertex graph: DFS returns `[5, 4, 2, 3, 1, 0]` and Kahn returns `[4, 5, 0, 2, 3, 1]`, and
both are correct. Which one you get depends on iteration order and, for Kahn, on the queue
discipline - swap the deque for a heap and you get the lexicographically smallest valid order
instead. **Asserting one exact list therefore pins an implementation detail rather than
correctness**, so what the tests check is the defining property.

The exception is a DAG whose edges already order every pair, which happens exactly when its
edges include a path running through all V vertices. Then there is one valid order and
asserting the list is fair; `[[1], [2], [3], []]` below is that case, and the six-vertex DAG
is not.

The helper checks the definition directly: every vertex appears exactly once, and for every
edge (u, v) the position of u precedes the position of v. Building a `position` map first
makes each edge check O(1).

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Check `order` is a permutation of `range(len(adj))` **before touching
   positions**, because it is guarding two different failures. A short order,
   which is what a cyclic graph produces, would otherwise raise `KeyError` from
   the lookup in step 3 rather than returning `False`; and a repeated vertex such
   as `[0, 0, 1]` satisfies every edge test while listing only two vertices.
2. Build `position`, mapping vertex to its index in the order.
3. Assert `position[u] < position[v]` for every edge `u → v`.

```python
def is_topological(adj, order):
    """True if order lists every vertex once and respects every edge."""
    if sorted(order) != list(range(len(adj))):
        return False
    position = {u: i for i, u in enumerate(order)}
    return all(position[u] < position[v] for u in range(len(adj)) for v in adj[u])


# DAG used by both implementations:
# 5 -> 0, 5 -> 2, 4 -> 0, 4 -> 1, 2 -> 3, 3 -> 1
DAG = [
    [],      # 0
    [],      # 1
    [3],     # 2 -> 3
    [1],     # 3 -> 1
    [0, 1],  # 4 -> 0, 4 -> 1
    [0, 2],  # 5 -> 0, 5 -> 2
]

# Two components, edges in both: 0 -> 1 and 2 -> 3.
DISCONNECTED = [[1], [], [3], []]


def test_is_topological():
    assert is_topological(DAG, [5, 4, 2, 3, 1, 0]) is True
    assert is_topological(DAG, [4, 5, 2, 3, 1, 0]) is True  # also valid
    assert is_topological(DAG, [4, 5, 0, 2, 3, 1]) is True  # what Kahn returns
    # 2 -> 3 is respected here but 3 -> 1 is not
    assert is_topological(DAG, [0, 1, 2, 3, 4, 5]) is False
    assert is_topological(DAG, [5, 4, 2, 3, 1]) is False  # missing a vertex
    # a repeated vertex: the edge checks pass, the permutation check does not
    assert is_topological([[1], []], [0, 0, 1]) is False
    # a cyclic graph produces no order at all, and that must not raise
    assert is_topological([[1], [2], [0]], []) is False


test_is_topological()
```

## DFS-based topological sort

Kahn's version needs a count of incoming edges, which means a pass over the whole graph before
it can start. DFS needs no such preparation, because the recursion already computes the thing
the ordering wants: the moment a vertex *finishes* is the moment everything below it is done.
The order is a by-product of the walk rather than something maintained alongside it.

The catch is that a by-product arrives backwards. A vertex finishes strictly after every
vertex reachable from it, so in finish order every edge points from a later entry to an
earlier one - a valid ordering with all its arrows the wrong way round. Reversing turns all of
them at once, which is why the reverse is not a tidying step but the step that makes the
output a topological order.

```
DAG:  2→3, 3→1, 4→0, 4→1, 5→0, 5→2

finish order pushed on the stack:  0, 1, 3, 2, 4, 5
reversed:                          5, 4, 2, 3, 1, 0
```

Appending on *entry* instead of on exit produces preorder, which places a vertex before its
descendants are known. On this DAG that gives `[0, 1, 2, 3, 4, 5]`, the exact list the checker
above rejects, and reversing it to `[5, 4, 3, 2, 1, 0]` does not rescue it either. Preorder
only ever orders a vertex against its own descendants; it says nothing about a vertex sitting
in a branch that was walked earlier, and `3 → 1` is exactly that, with 1 already emitted from
an earlier root by the time 3 is reached.

This version also cannot detect a cycle, and the reason is worth holding on to: it appends
every vertex exactly once, so **the output is always a full permutation of all V vertices**,
cyclic graph or not. There is no short answer to notice. `[[0]]`, a single self loop, returns
`[0]` with a straight face. Making it safe means adding the ancestry state from
[Cycle Detection](cycle-detection.md), where colour 2 is set at precisely the moment this
version appends: a neighbour still at colour 1 is a back edge, and that is the cycle.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Plain DFS. `visited` is history, set on entry and never cleared; `stack` is
   the finish order and is append-only.
2. Outer loop over every vertex, so a second component is not left out - on
   `0 → 1, 2 → 3` a single call from vertex 0 returns half the graph.
3. `stack.append(u)` **after** the neighbour loop, never before, so the append
   records finishing rather than arriving. **Above the loop it is preorder**,
   which gives `[0, 1, 2, 3, 4, 5]` here and is not a topological order.
4. Return `stack[::-1]`, which is a new reversed list. **`return stack.reverse()`
   returns `None`**, since it reverses in place and hands back nothing.
5. **This assumes a DAG and cannot tell you otherwise.** Given a cycle it returns
   a confident, full-length, wrong answer. Kahn's algorithm below detects that
   for free.

```python
def topo_sort_dfs(adj):
    """DFS-based topological sort. Assumes adj is a DAG."""
    visited = [False] * len(adj)
    stack = []

    def dfs(u):
        visited[u] = True
        for v in adj[u]:
            if not visited[v]:
                dfs(v)
        stack.append(u)  # push after all descendants processed

    for u in range(len(adj)):
        if not visited[u]:
            dfs(u)
    return stack[::-1]  # reverse gives topological order


def test_topo_sort_dfs():
    assert is_topological(DAG, topo_sort_dfs(DAG))
    # two components, both with edges - the outer loop has to reach the second
    assert is_topological(DISCONNECTED, topo_sort_dfs(DISCONNECTED))
    # a chain orders every pair, so it has exactly one valid order
    assert topo_sort_dfs([[1], [2], [3], []]) == [0, 1, 2, 3]
    # no edges - any permutation is valid
    assert is_topological([[], [], []], topo_sort_dfs([[], [], []]))
    assert topo_sort_dfs([]) == []
    # parallel edges 0 -> 1 twice: the second one finds 1 already visited
    assert topo_sort_dfs([[1, 1], []]) == [0, 1]
    # cycle blindness: full-length output, silently not a topological order
    cycle = [[1], [2], [0]]
    assert len(topo_sort_dfs(cycle)) == len(cycle)
    assert is_topological(cycle, topo_sort_dfs(cycle)) is False
    assert is_topological([[0]], topo_sort_dfs([[0]])) is False  # self loop


test_topo_sort_dfs()

print("DFS topo sort:", topo_sort_dfs(DAG))
```

## Kahn's Algorithm

Turn readiness into a number. `in_degree[v]` counts the vertices that still point at `v` and
have not been emitted yet, so `in_degree[v] == 0` reads directly as "every prerequisite of `v`
is already in the output". Seed the queue with the vertices that start that way, and each time
one is emitted, decrement its neighbours: a neighbour hitting 0 has just had its last
prerequisite satisfied and joins the queue.

The counts are the invisible part. On the existing six-vertex DAG, arrays are
indexed by vertex and the queue pops from the left:

```
start    in_degree [2, 2, 1, 1, 0, 0]   queue [4, 5]
emit 4   in_degree [1, 1, 1, 1, 0, 0]   queue [5]
emit 5   in_degree [0, 1, 0, 1, 0, 0]   queue [0, 2]
```

Vertex 0 waits after 4 removes one incoming edge. Only 5 removes its last one,
changing its count from 1 to 0 and making it ready. Vertex 2's count reaches 0 in
that same step. **The queue receives a vertex at the exact moment its final
prerequisite disappears.**

Cycle detection comes out of the same count rather than being bolted on. A vertex on a cycle
has a prerequisite that is itself downstream of that vertex, so its count never reaches 0, and
neither does the count of anything fed by it. The vertices missing from the result are exactly
those on a cycle or starved by one: `0 → 1, 1 → 2, 2 → 1, 2 → 3` returns `[0]`, holding back
the cycle `1 → 2 → 1` along with vertex 3 downstream of it. So `len(order) < n` is the cycle
report, and the gap names the culprits.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Build `in_degree` by walking every edge once: `in_degree[v] += 1` for each
   edge `u → v`. **Count arrivals, not departures.** `len(adj[u])` is out-degree,
   and seeding from that starts at the sinks and returns `[0, 1]` on the DAG here.
2. Seed the queue with **every** vertex at `0`, meaning everything ready before
   anything is emitted. A DAG can have several sources - this one has 4 and 5 -
   and seeding just the first returns `[4]`.
3. Pop `u`, append it to the order, then for each neighbour decrement
   `in_degree[v]`. **The decrement is what "remove `u` from the graph" means**,
   and it is what keeps the count equal to the number of *unemitted*
   prerequisites rather than the number of edges.
4. Enqueue `v` when the decrement leaves it at `0`, **testing after the
   decrement, not before**: reversing those two lines truncates the answer to
   `[4, 5]`. Each edge decrements once, so a count can never fall below 0 and
   `<= 0` behaves identically here; what matters is that a zero test exists at
   all. Enqueue on every decrement instead and vertices arrive once per incoming
   edge, giving `[4, 5, 0, 1, 0, 2, 3, 1]` with 1 emitted before 3.
5. **`len(order) < n` means a cycle** - the free check the DFS version lacks.
   No separate visited list: reaching 0 happens exactly once per vertex.

```python
from collections import deque


def topo_sort_bfs(adj):
    """
    Kahn's algorithm (BFS-based topological sort).

    Also detects cycles: a result with fewer than V vertices means the graph
    has a cycle.
    """
    n = len(adj)
    in_degree = [0] * n
    for u in range(n):
        for v in adj[u]:
            in_degree[v] += 1

    q = deque(u for u in range(n) if in_degree[u] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)
    return order  # len(order) < n means a cycle exists


def test_topo_sort_bfs():
    assert is_topological(DAG, topo_sort_bfs(DAG))
    assert is_topological(DISCONNECTED, topo_sort_bfs(DISCONNECTED))
    assert topo_sort_bfs([[1], [2], [3], []]) == [0, 1, 2, 3]
    assert is_topological([[], [], []], topo_sort_bfs([[], [], []]))
    assert topo_sort_bfs([]) == []
    # parallel edges 0 -> 1 twice: in_degree[1] is 2 and reaches 0 on the
    # second decrement, so 1 is enqueued exactly once
    assert topo_sort_bfs([[1, 1], []]) == [0, 1]
    # cycle 0 -> 1 -> 2 -> 0: nothing ever reaches in-degree 0
    assert topo_sort_bfs([[1], [2], [0]]) == []
    assert topo_sort_bfs([[0]]) == []  # self loop starves itself
    # partial order returned when only part of the graph is cyclic
    cyclic = [[1], [2], [1], []]  # 1 -> 2 -> 1 is a cycle, 3 is isolated
    assert topo_sort_bfs(cyclic) == [0, 3]
    # vertex 3 is not on the cycle but is starved by it, so it is held back too
    assert topo_sort_bfs([[1], [2], [1, 3], []]) == [0]


test_topo_sort_bfs()

print("Kahn's topo sort:", topo_sort_bfs(DAG))
```
