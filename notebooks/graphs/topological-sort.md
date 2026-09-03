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

**Recipe**

1. First check `order` is a permutation of all vertices, so a short or repeated
   result cannot pass.
2. Build `position`, mapping vertex to its index in the order.
3. Assert `position[u] < position[v]` for **every** edge `u -> v`.
4. **Assert the defining property, not one specific answer.** Most DAGs have many
   valid topological orders and the two algorithms below produce different ones,
   so comparing against a hard-coded list would test the implementation rather
   than the requirement.

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

Kahn's version needs a count of incoming edges, which means a pass over the whole graph before
it can start. DFS needs no such preparation, because the recursion already computes the thing
the ordering wants: the moment a vertex *finishes* is the moment everything below it is done.
The order is a by-product of the walk rather than something maintained alongside it.

The catch is that a by-product arrives backwards - descendants finish first - so the finish
order has to be reversed before it reads as a topological order.

```
DAG:  2→3, 3→1, 4→0, 4→1, 5→0, 5→2

finish order pushed on the stack:  0, 1, 3, 2, 4, 5
reversed:                          5, 4, 2, 3, 1, 0
```

Note this is *not* the same as preorder - appending on entry instead of on exit would
place a vertex before its descendants are known and can produce an invalid order.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Plain DFS with a `visited` list and an outer loop over every vertex.
2. `stack.append(u)` **after** the neighbour loop, never before.
3. **Appending on the way out is the entire algorithm.** A vertex is only pushed
   once everything reachable from it is already pushed, so it always lands
   *below* its own descendants. Move that line above the loop and you get
   preorder, which is not a topological order.
4. Return `stack[::-1]`. The deepest-finishing vertices sit at the bottom, and
   reversing puts the ones with no prerequisites first.
5. **This assumes a DAG and cannot tell you otherwise.** Given a cycle it returns
   a confident, wrong answer. Kahn's algorithm below detects that for free.

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

**Recipe**

1. Count `in_degree` for every vertex by walking all edges once. **Count
   arrivals, `in_degree[v] += 1` for each edge `u -> v`, not departures.**
2. Seed the queue with every vertex of in-degree `0`: the vertices with no
   prerequisites.
3. Pop `u`, append it to the order, then for each neighbour `v` decrement
   `in_degree[v]` and enqueue it **only when it reaches exactly `0`**.
4. **Decrementing is "remove u from the graph".** A vertex becomes available the
   moment its last prerequisite is emitted, and testing `== 0` rather than `<= 0`
   is what enqueues it exactly once.
5. **`len(order) < n` means a cycle.** Vertices inside a cycle each wait on
   another one in the same cycle, so their in-degree never falls to zero and they
   are never emitted. This is the free cycle check the DFS version lacks.

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
