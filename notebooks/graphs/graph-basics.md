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

# Graph Basics

Trees don't allow cycles, graphs do.

```
v1 ---- v3
|        | \
|        | v5
|        | /
v2 ---- v4
```

Graph is a pair of sets G = {V, E}
- **Vertices:** V = {v1, v2, v3, v4, v5}
- **Edges:** E = {(v1, v2), (v1, v3), (v2, v4), (v3, v4), (v3, v5), (v4, v5)}

## Types of Graphs

### Undirected Graph
- Can traverse edges in both directions
- Edge (v1, v2) same as (v2, v1)
- **Example:** Social network
- **Degree of vertex:** Number of edges passing through it
- **Sum of degrees = 2 × |E|**
- **Max edges = |V| × (|V| - 1) / 2**

### Directed Graph
- Edges are ordered pairs
- (v1, v2) ≠ (v2, v1)
- **Example:** Web pages with links
- **In-degree:** Number of incoming edges
- **Out-degree:** Number of outgoing edges
- **Sum of in-degrees = Sum of out-degrees = |E|**
- **Max edges = |V| × (|V| - 1)**

## Common Terms

- **Walk:** Sequence of vertices following edges (repetition allowed)
- **Path:** Walk with no vertex repetition
- **Cyclic:** Walk that begins and ends with same vertex
- **DAG:** Directed Acyclic Graph
- **Weighted Graph:** Edges have weights assigned

## Graph Representations

### 1. Adjacency Matrix
- |V| × |V| matrix
- **Space:** Θ(V²)
- **Check adjacency:** Θ(1)
- **Find all adjacent:** Θ(V)
- **Add/remove edge:** Θ(1)
- **Add/remove vertex:** Θ(V²)

### 2. Adjacency List
- Array of lists
- **Space:** Θ(V + E)
- **Check adjacency:** O(V)
- **Find all adjacent:** Θ(degree(u))
- **Add/remove edge:** Θ(1)
- **Find degree:** Θ(1)

Adjacency list is the default choice for sparse graphs (E ≪ V²), which is
most graphs in practice. The traversal notebooks all use it.

> **Mental model.** A graph is a record of what is next to what. The vertices and edges are
> handed to you; the only real decision you make is how to store that record. An adjacency
> list answers "who are u's neighbours?" cheaply, because it hands you the list already
> built. An adjacency matrix answers "is there an edge from u to v?" cheaply, because that
> is one lookup. Every graph algorithm sits on top of one of those two answers.
>
> **Load-bearing:** the question your algorithm asks most often is what picks the
> representation. Traversals walk neighbours, so they want the list - that is why
> [Graph Traversal](graph-traversal.md) and everything built on it use one. And the matrix
> costs V² cells whether the graph is dense or nearly empty, so a graph with a million
> vertices and three edges still pays for a million-by-million grid.


## Building an Adjacency List

`adj[u]` is the list of u's neighbours, so the whole structure costs Θ(V + E) rather than
the matrix's Θ(V²). Vertices are `0..n-1`, which lets a plain list of lists stand in for
a map.

`add_edge` appends **both** directions, because in an undirected graph the edge u--v is
the same object as v--u; forget one and half your traversals silently miss edges. Storing
each edge twice is also why the degrees sum to 2·|E|, which the test checks.

**Time:** O(1) per edge &nbsp; **Space:** Θ(V + E)

```python
def add_edge(adj, u, v):
    """Add an undirected edge u--v to adjacency list adj."""
    adj[u].append(v)
    adj[v].append(u)


def build_adj(n, edges):
    """Build an adjacency list for an undirected graph on vertices 0..n-1."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        add_edge(adj, u, v)
    return adj


def test_build_adj():
    #   0 --- 1
    #   | \   |
    #   |  \  |
    #   2    3
    adj = build_adj(4, [(0, 1), (0, 2), (0, 3), (1, 3)])
    assert adj == [[1, 2, 3], [0, 3], [0], [0, 1]]
    assert len(adj[0]) == 3  # degree of vertex 0
    # sum of degrees = 2 * |E|
    assert sum(len(neighbors) for neighbors in adj) == 2 * 4


test_build_adj()
```

## Building an Adjacency Matrix

`matrix[u][v] = 1` means "edge present", and the undirected case writes both cells, so
the matrix is symmetric about its diagonal.

The trade is a direct one: Θ(V²) space even for a graph with three edges, in exchange for
Θ(1) "are u and v adjacent?" - a question the adjacency list can only answer by scanning
u's neighbours. Dense graphs and repeated adjacency queries favour the matrix; nearly
everything else favours the list.

**Time:** Θ(V²) to build &nbsp; **Space:** Θ(V²)

```python
def build_matrix(n, edges):
    """Build an |V| x |V| adjacency matrix for an undirected graph."""
    matrix = [[0] * n for _ in range(n)]
    for u, v in edges:
        matrix[u][v] = 1
        matrix[v][u] = 1  # undirected - symmetric matrix
    return matrix


def print_graph(adj):
    """Print an adjacency list, one vertex per line."""
    for u, neighbors in enumerate(adj):
        print(u, "->", neighbors)


def test_build_matrix():
    matrix = build_matrix(4, [(0, 1), (0, 2), (0, 3), (1, 3)])
    assert matrix == [
        [0, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 0],
        [1, 1, 0, 0],
    ]
    # symmetric for undirected graphs
    assert all(matrix[u][v] == matrix[v][u] for u in range(4) for v in range(4))
    # adjacency check is O(1)
    assert matrix[1][3] == 1
    assert matrix[1][2] == 0


test_build_matrix()

print_graph(build_adj(4, [(0, 1), (0, 2), (0, 3), (1, 3)]))
```

# Python Built-in: Graph Representation

Python has no built-in graph type, but `defaultdict(list)` is the idiomatic way
to build adjacency lists.

This avoids pre-allocating a fixed-size list and lets you use any hashable type
as vertex (strings, tuples, etc.).

```python
from collections import defaultdict

# adjacency list using defaultdict - no need to pre-allocate
graph = defaultdict(list)

# works with string vertices (not just integers)
edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)  # undirected

print(dict(graph))
# {'A': ['B', 'C'], 'B': ['A', 'D'], 'C': ['A', 'D'], 'D': ['B', 'C']}

# a set of sets is handy when you need O(1) adjacency checks with duplicates
# collapsed
neighbors = {u: set(vs) for u, vs in graph.items()}
print("B" in neighbors["A"])  # True
print("D" in neighbors["A"])  # False
```

## Next

- [Graph Traversal](graph-traversal.md) - BFS, DFS, connected components
- [Cycle Detection](cycle-detection.md)
- [Topological Sort](topological-sort.md)
- [Dijkstra's Algorithm](dijkstra.md)
- [Union-Find](union-find.md)
