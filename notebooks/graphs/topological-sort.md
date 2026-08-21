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

1. **DFS-based:** [depth-first search](graph-traversal.md), appending each vertex the
   moment it finishes, then reversing the result.
2. **BFS-based (Kahn's algorithm):** repeatedly take a vertex with in-degree 0
   and remove its outgoing edges.

**Time:** O(V + E) for both.

A valid order is usually not unique, so the tests below check the defining
property rather than one specific permutation.

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


### Checking an order

A DAG usually has many valid topological orders, so asserting one exact list would
make the tests brittle and would not really check the property.

This helper checks the definition directly: every vertex appears exactly once, and for
every edge (u, v) the position of u precedes the position of v. Building a
`position` map first makes each edge check O(1).

**Time:** O(V + E) &nbsp; **Space:** O(V)

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


def test_is_topological():
    assert is_topological(DAG, [5, 4, 2, 3, 1, 0]) is True
    assert is_topological(DAG, [4, 5, 2, 3, 1, 0]) is True  # also valid
    # 2 -> 3 is respected here but 3 -> 1 is not
    assert is_topological(DAG, [0, 1, 2, 3, 4, 5]) is False
    assert is_topological(DAG, [5, 4, 2, 3, 1]) is False  # missing a vertex


test_is_topological()
```

### DFS-based topological sort

The key observation: in a DFS, a vertex is *finished* only after everything reachable
from it is finished. So if you append each vertex at the moment it finishes, you build
the order backwards - reverse it and every vertex precedes its descendants.

```
DAG:  2→3, 3→1, 4→0, 4→1, 5→0, 5→2

finish order pushed on the stack:  0, 1, 3, 2, 4, 5
reversed:                          5, 4, 2, 3, 1, 0
```

Note this is *not* the same as preorder - appending on entry instead of on exit would
place a vertex before its descendants are known and can produce an invalid order.

**Time:** O(V + E) &nbsp; **Space:** O(V)

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
    order = topo_sort_dfs(DAG)
    assert is_topological(DAG, order)
    # a chain has exactly one valid order
    assert topo_sort_dfs([[1], [2], [3], []]) == [0, 1, 2, 3]
    # no edges - any permutation is valid
    assert is_topological([[], [], []], topo_sort_dfs([[], [], []]))
    assert topo_sort_dfs([]) == []


test_topo_sort_dfs()

print("DFS topo sort:", topo_sort_dfs(DAG))
```

## Kahn's Algorithm

Turn the definition into a rule: a vertex can be emitted as soon as nothing points at it
any more. Count in-degrees, seed a queue with every zero, and each time you emit a
vertex, decrement its neighbours - a neighbour dropping to 0 has had all its
prerequisites satisfied and joins the queue.

It doubles as a cycle detector for free: vertices inside a cycle keep each other's
in-degree above zero forever, so a result shorter than V proves a cycle exists.

**Time:** O(V + E) &nbsp; **Space:** O(V)

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
    order = topo_sort_bfs(DAG)
    assert is_topological(DAG, order)
    assert topo_sort_bfs([[1], [2], [3], []]) == [0, 1, 2, 3]
    # cycle 0 -> 1 -> 2 -> 0: nothing ever reaches in-degree 0
    assert topo_sort_bfs([[1], [2], [0]]) == []
    # partial order returned when only part of the graph is cyclic
    cyclic = [[1], [2], [1], []]  # 1 -> 2 -> 1 is a cycle, 3 is isolated
    assert len(topo_sort_bfs(cyclic)) < len(cyclic)


test_topo_sort_bfs()

print("Kahn's topo sort:", topo_sort_bfs(DAG))
```
