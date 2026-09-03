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

# Dijkstra's Algorithm

Shortest path from a source vertex to every other vertex in a **weighted graph with
non-negative edges**.

> **Mental model.** [BFS](graph-traversal.md) is the same loop with a different frontier.
> BFS comes out in ring order, everything one edge away before anything two edges away,
> which is only shortest when every edge costs the same. Swap the queue for a **min-heap
> keyed on distance** and the vertex that comes out next is the cheapest one found so far
> rather than the earliest one found. Nothing else in the loop changes, and now weights
> work.
>
> **Load-bearing:** a popped vertex is **final** only because weights cannot be negative.
> Any other route into it would have to run through a vertex that is already further away,
> and a longer prefix can never turn out shorter when every edge adds something. Allow one
> negative edge and that argument collapses, the first pop can be wrong, and you need
> Bellman-Ford instead.

## Relaxing an edge

The only real work in the loop is **relaxing** an edge: asking whether routing through the
vertex you just popped beats the best distance already known for its neighbour, which is
the test `dist[u] + w < dist[v]`. When it wins, write the shorter distance down and push
that neighbour so its own edges get relaxed later. Every distance starts at ∞ except the
source's, which starts at 0, so the first time anything is reached at all it counts as an
improvement.

The rows worth reading below are the ones where nothing happens. A vertex gets popped and
no distance improves, because a cheaper route there was already found.

```
graph on the left, edge weights on the connectors
`dist 1<-4` means dist[1] becomes 4; pops come out in heap order, nearest first

0 --4-- 1 --8-- 2        pop 0  (d=0)   dist 1<-4, 3<-8
|       |       |        pop 1  (d=4)   dist 2<-12, 4<-6
8       2       7        pop 4  (d=6)   3 stays 8 (6+7=13 is worse), 5<-15
|       |       |        pop 3  (d=8)   nothing improves
3 --7-- 4 --9-- 5        pop 2  (d=12)  5 stays 15 (12+7=19 is worse)
                         pop 5  (d=15)

result: [0, 4, 12, 8, 6, 15]
```

`heapq` has no decrease-key, so an improvement pushes a *new* entry and leaves the old one
behind. `if d > dist[u]: continue` discards those stale copies when they surface.

**Time:** O((V + E) log V) &nbsp; **Space:** O(V + E)

**Recipe**

1. `dist = [inf] * n`, `dist[src] = 0`, and a heap seeded with `(0, src)`.
   **Tuples go on the heap distance-first, because `heapq` compares tuples
   left to right and the distance has to be the sort key.**
2. Pop the smallest `(d, u)`.
3. **`if d > dist[u]: continue`.** The heap has no decrease-key operation, so a
   shorter route to `u` found after `u` was pushed leaves the older, longer entry
   sitting in the heap. This line discards those stale copies. Without it a
   vertex is processed several times, once per push.
4. Relax each edge: `dist[u] + w < dist[v]` means a better route, so update
   `dist[v]` and push `(dist[v], v)`.
5. **Push a new entry rather than trying to update the old one.** That is what
   makes the stale check in step 3 necessary, and it is the standard trade: a
   slightly larger heap in exchange for not needing an indexed priority queue.
6. Unreachable vertices are never pushed and keep `inf`.
7. **Why popping the minimum is safe to treat as final:** every edge weight is
   non-negative, so no route through an unprocessed vertex could come back
   cheaper. Negative weights break exactly this argument, which is why Dijkstra
   cannot handle them.

```python
import heapq
import math
from itertools import pairwise


def dijkstra(adj, src):
    """
    Shortest distances from src to every vertex.

    adj: adjacency list where adj[u] = [(v, weight), ...]
    Unreachable vertices keep a distance of math.inf.
    Time: O((V + E) log V)
    """
    n = len(adj)
    dist = [math.inf] * n
    dist[src] = 0
    heap = [(0, src)]  # (distance, vertex)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:  # stale entry left over from an earlier push
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    return dist


# weighted graph:
# 0 --4-- 1 --8-- 2
# |       |       |
# 8       2       7
# |       |       |
# 3 --7-- 4 --9-- 5
WEIGHTED = [
    [(1, 4), (3, 8)],          # 0
    [(0, 4), (2, 8), (4, 2)],  # 1
    [(1, 8), (5, 7)],          # 2
    [(0, 8), (4, 7)],          # 3
    [(1, 2), (3, 7), (5, 9)],  # 4
    [(2, 7), (4, 9)],          # 5
]


def test_dijkstra():
    assert dijkstra(WEIGHTED, 0) == [0, 4, 12, 8, 6, 15]
    # distance to self is always 0
    assert dijkstra(WEIGHTED, 3)[3] == 0
    # the greedy choice matters: 0 -> 4 goes via 1 (4 + 2 = 6),
    # not via the direct-looking 0 -> 3 -> 4 (8 + 7 = 15)
    assert dijkstra(WEIGHTED, 0)[4] == 6
    # unreachable vertices stay at infinity
    disconnected = [[(1, 1)], [(0, 1)], []]
    assert dijkstra(disconnected, 0) == [0, 1, math.inf]
    # single vertex
    assert dijkstra([[]], 0) == [0]


test_dijkstra()

print("Shortest distances from 0:", dijkstra(WEIGHTED, 0))
```

## Tracking the Path

Distances alone don't say *which* route achieved them. Record a `parent` at the moment a
distance improves - the edge that produced the best known cost - and those parents form
a shortest-path **tree** rooted at the source.

Walk `parent` backwards from the destination to the source, then reverse. `parent` is
`None` at the source, which is the loop's stopping condition, and an unreachable
destination is caught up front by its infinite distance.

**Time:** O((V + E) log V) &nbsp; **Space:** O(V)

**Recipe**

1. Identical to `dijkstra` plus a `parent` array of `None`.
2. Inside the relaxation, alongside `dist[v] = dist[u] + w`, record `parent[v] =
   u`. **One line. The predecessor is recorded at the moment a better route is
   found, so `parent` always reflects the current best path rather than the first
   one seen.**
3. Rebuild by walking `parent` back from `dst` until `None`, then reverse.
4. **Store the predecessor, not the whole path.** Copying a path per vertex would
   be O(V) per update; one back-pointer is O(1) and the path is reconstructed
   once at the end.
5. `dist[dst]` still `inf` means unreachable, so there is no path to rebuild.

```python
def dijkstra_path(adj, src, dst):
    """Shortest path from src to dst as a list of vertices, [] if unreachable."""
    n = len(adj)
    dist = [math.inf] * n
    parent = [None] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(heap, (dist[v], v))

    if dist[dst] == math.inf:
        return []
    path = []
    node = dst
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


def test_dijkstra_path():
    # 0 -> 4 costs 6 through vertex 1
    assert dijkstra_path(WEIGHTED, 0, 4) == [0, 1, 4]
    assert dijkstra_path(WEIGHTED, 0, 5) == [0, 1, 4, 5]
    assert dijkstra_path(WEIGHTED, 2, 2) == [2]
    assert dijkstra_path([[(1, 1)], [(0, 1)], []], 0, 2) == []
    # the returned path's total weight matches the computed distance
    path = dijkstra_path(WEIGHTED, 0, 5)
    weights = {(u, v): w for u in range(len(WEIGHTED)) for v, w in WEIGHTED[u]}
    total = sum(weights[edge] for edge in pairwise(path))
    assert total == dijkstra(WEIGHTED, 0)[5]


test_dijkstra_path()

print("Shortest path 0 -> 5:", dijkstra_path(WEIGHTED, 0, 5))
```
