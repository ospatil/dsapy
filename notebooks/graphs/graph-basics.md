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
- **Cycle:** Walk that returns to its starting vertex without reusing an edge. In a *simple*
  undirected graph that needs at least three distinct vertices, since stepping along one edge
  and straight back would reuse it - a self loop or a parallel pair is a cycle on fewer, and
  [cycle detection](cycle-detection.md) reports those too. In a directed graph two vertices
  are enough, because `u→v` and `v→u` are different edges.
- **DAG:** Directed Acyclic Graph
- **Weighted Graph:** Edges have weights assigned

## Graph Representations

The graph is given to you. What you choose is the *record* you keep of it, and
that choice is settled by one question: which query does the algorithm run in
its innermost loop? There are only four queries worth naming.

1. **"Who are u's neighbours?"** - every traversal, every shortest path, every
   cycle check. This one dominates.
2. **"Is u adjacent to v?"** - one yes/no about one pair, asked about pairs you
   did not arrive at by walking.
3. **"How many edges leave u?"** - degrees, and the in-degree counts that
   [topological sort](topological-sort.md) runs on.
4. **"Add or remove an edge, or a vertex."** - anything that mutates the graph
   while the algorithm runs.

Two structures answer all four, and each is slow at exactly what the other is
fast at. An **adjacency list** stores, for every vertex, the list of its
neighbours. An **adjacency matrix** stores a |V| × |V| grid of cells, one per
ordered pair, holding 1 when the edge exists.

| Query | Adjacency list | Adjacency matrix |
|---|---|---|
| Who are u's neighbours? | Θ(degree(u)) - the list is already built | Θ(V) - scan a whole row, mostly zeros |
| Is u adjacent to v? | O(degree(u)) - scan u's list | Θ(1) - one cell lookup |
| How many edges leave u? | Θ(1) - the list's length | Θ(V) - count the row |
| Add an edge | Θ(1) - append to u's list | Θ(1) - write one cell |
| Remove an edge | O(degree(u)) - find v in u's list first | Θ(1) - clear one cell |
| Add a vertex | Amortized Θ(1) - append an empty list | Θ(V) with resizable rows; Θ(V²) if the grid must be rebuilt |
| Space | Θ(V + E) | Θ(V²) |

Read the first row and the last row together and the default falls out. A
traversal asks query 1 once per vertex, and those calls sum to Θ(V + E) on a
list because each list is only as long as its vertex's degree. The matrix
answers the same sweep in Θ(V²) whatever the graph looks like, because it has
to walk V cells to find the few that are 1. On a sparse graph, E ≪ V², which is
most real graphs, that is the difference between linear and quadratic.

So: adjacency list by default, and every traversal notebook here uses one. Reach
for the matrix when query 2 is the inner loop *and* the graph is dense, so most
cells are non-zero and the Θ(V²) was unavoidable anyway.

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

`adj[u]` is the list of u's neighbours, so the whole structure costs Θ(V + E)
rather than the matrix's Θ(V²). Vertices are `0..n-1`, which lets a plain list of
lists stand in for a map.

`add_edge` appends **both** directions, because in an undirected graph the edge
u--v is the same object as v--u; forget one and half your traversals silently
miss edges. Storing each edge twice is also why the degrees sum to 2·|E|.

**Time:** O(1) per edge &nbsp; **Space:** Θ(V + E)

**Recipe**

1. Initialize `adj = [[] for _ in range(n)]`, one fresh list per vertex.
   **Not `[[]] * n`, which aliases a single list into every slot, so every
   vertex ends up sharing one neighbour list.**
2. Per edge `(u, v)`: `adj[u].append(v)` **and** `adj[v].append(u)`. **Drop the
   second append and the structure is still well-formed, just wrong** - nothing
   raises, the edge simply becomes one-way.
3. Return `adj`. For a directed graph, delete the second append; that is the
   only change.

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
    edges = [(0, 1), (0, 2), (0, 3), (1, 3)]
    adj = build_adj(4, edges)
    # the defining property: v is in u's list exactly when u is in v's
    assert all(
        (v in adj[u]) == (u in adj[v]) for u in range(4) for v in range(4)
    )
    # every stored neighbour comes from a real edge, and none is missing
    stored = {(u, v) for u in range(4) for v in adj[u]}
    assert stored == {pair for u, v in edges for pair in ((u, v), (v, u))}
    assert sum(len(neighbors) for neighbors in adj) == 2 * len(edges)
    assert len(adj[0]) == 3  # degree of vertex 0
    # neighbour order is not part of the contract, only a consequence of
    # append order - but it is deterministic, which is what makes the
    # traversal notebook's visit orders stable
    assert adj == [[1, 2, 3], [0, 3], [0], [0, 1]]
    assert build_adj(2, []) == [[], []]  # no edges
    assert build_adj(0, []) == []  # empty graph


test_build_adj()
```

## Building an Adjacency Matrix

`matrix[u][v] = 1` means "edge present", and the undirected case writes both
cells, so the matrix is symmetric about its diagonal.

The trade is a direct one: Θ(V²) space even for a graph with three edges, in
exchange for Θ(1) "are u and v adjacent?" - a question the adjacency list can
only answer by scanning u's neighbours. Dense graphs and repeated adjacency
queries favour the matrix; nearly everything else favours the list.

**Time:** Θ(V²) to build &nbsp; **Space:** Θ(V²)

**Recipe**

1. Initialize `matrix = [[0] * n for _ in range(n)]`. **The inner `[0] * n` is
   safe because integers are immutable and copied by value; the outer
   comprehension is still required, for the same aliasing reason as the list.**
2. Per edge `(u, v)`: set `matrix[u][v] = 1` **and** `matrix[v][u] = 1`, keeping
   it symmetric. A directed graph sets only the first.
3. Return `matrix`. **Adding one edge is O(1), but clearing or scanning the
   structure is Θ(V²)** however few edges it holds - which is why "who are u's
   neighbours?" costs a full row here.

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
    edges = [(0, 1), (0, 2), (0, 3), (1, 3)]
    matrix = build_matrix(4, edges)
    assert matrix == [
        [0, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 0],
        [1, 1, 0, 0],
    ]
    # symmetric for undirected graphs
    assert all(matrix[u][v] == matrix[v][u] for u in range(4) for v in range(4))
    # the two representations describe the same graph: a cell is 1 exactly when
    # the adjacency list holds that neighbour, whatever order it holds them in
    adj = build_adj(4, edges)
    assert all(
        bool(matrix[u][v]) == (v in adj[u])
        for u in range(4)
        for v in range(4)
    )
    assert all(matrix[u][u] == 0 for u in range(4))  # no self-loops here
    # adjacency check is O(1)
    assert matrix[1][3] == 1
    assert matrix[1][2] == 0
    assert build_matrix(2, []) == [[0, 0], [0, 0]]  # no edges


test_build_matrix()

print_graph(build_adj(4, [(0, 1), (0, 2), (0, 3), (1, 3)]))
```

## Python Built-in: Graph Representation

Python has no built-in graph type, but `defaultdict(list)` is the idiomatic way
to build adjacency lists.

This avoids pre-allocating a fixed-size list and lets you use any hashable type
as vertex (strings, tuples, etc.).

A `dict` of **sets** is the third useful shape: it keeps the list's Θ(V + E)
space while buying back the matrix's Θ(1) answer to "is u adjacent to v?", at
the cost of losing neighbour order and collapsing parallel edges. Reach for it
when an algorithm asks both query 1 and query 2 often.

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

# a dict of sets is handy when you need O(1) adjacency checks with duplicates
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
