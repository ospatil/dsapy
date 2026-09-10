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

Three pieces of state, and only the third is unusual:

- `dist[v]` is **the cost of the cheapest route to `v` found so far**, not the answer yet.
  It starts at ∞ for every vertex except the source, which starts at 0, and it only ever
  falls. A vertex no route reaches is never written to and keeps its ∞.
- a heap entry `(d, v)` is a note saying "`v` can be reached for `d`". The distance sits
  first in the tuple because that is the key the heap has to order by.
- `d` is the cost that note carried **when it was pushed**, which need not still be
  `dist[v]` by the time it surfaces.

The only real work in the loop is **relaxing** an edge: asking whether routing through the
vertex you just popped beats the best route already known to its neighbour, which is the
test `dist[u] + w < dist[v]`. When it wins, write the shorter distance down and push that
neighbour so its own edges get relaxed later, from the lower cost. Since everything starts
at ∞, the first time a vertex is reached at all that test compares against ∞ and passes,
so discovering a vertex and improving it are the same event and there is no separate case
for either.

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

`heapq` has no decrease-key, so an improvement cannot edit the note already sitting on the
heap. It pushes a second one and leaves the first behind. That stale copy carries a `d`
bigger than the `dist[u]` that superseded it, which is exactly what `if d > dist[u]:
continue` tests when it surfaces.

Four vertices are enough to watch one stale note appear and be discarded:

```
directed graph: 0->1 (10), 0->2 (1), 2->1 (1), 1->3 (1)
heap notes are (distance, vertex), shown in pop order

pop (0, 0)   dist[1] inf->10, dist[2] inf->1  heap (1, 2) (10, 1)
pop (1, 2)   dist[1] 10->2                   heap (2, 1) (10, 1)
pop (2, 1)   dist[3] inf->3                  heap (3, 3) (10, 1)
pop (3, 3)   nothing improves                heap (10, 1)
pop (10, 1)  10 > dist[1] = 2, discard it
```

The route through 2 improves vertex 1 but cannot delete its old `(10, 1)` note.
When that note surfaces, its distance no longer matches the best known distance,
so the stale check prevents vertex 1 from being processed twice.

## Why the first pop is final

Popping is committing: the loop never revisits a vertex, so the distance it pops has to be
right the first time. It is, and the argument is short enough to rebuild on demand.

Say `(d, u)` comes off the heap and survives the stale test, so `d == dist[u]`. Take any
route from the source to `u`, however roundabout. Follow it forwards until it first reaches
a vertex that has not been popped before now, and call that vertex `y`; `u` itself qualifies,
so there is always one. The step into `y` came from a vertex that *was* already popped, and
popping a vertex relaxes every one of its edges, so `dist[y]` is already at most the cost of
this route's prefix ending at `y`.

Two more facts close it. `y` still has an entry on the heap carrying `dist[y]`, because it
has not been popped and every improvement pushes one. `u` came off the heap first and the
heap hands back its smallest key, so `dist[u] ≤ dist[y]`. And a prefix of a route costs no
more than the whole route, **because each remaining edge adds something that is not
negative**. Chain the three:

```
dist[u]  ≤  dist[y]  ≤  cost of the prefix up to y  ≤  cost of the whole route
```

That holds for *every* route to `u`, so nothing beats `dist[u]` and committing to it is safe.

Non-negativity is used in one link of that chain, `prefix ≤ whole route`, and nowhere else.
Removing that link is all it takes to break the algorithm, which is what the section after
the code does.

## The loop

That is the whole algorithm: pop the nearest vertex not yet finished, relax its edges,
discard notes that have been superseded, stop when the heap empties.

**Time:** O((V + E) log V) &nbsp; **Space:** O(V + E)

**Recipe**

1. `dist = [inf] * n`, `dist[src] = 0`, and a heap seeded with `(0, src)`.
   **Tuples go on the heap distance-first, because `heapq` compares tuples
   left to right and the distance has to be the sort key.**
2. Loop while the heap is non-empty, popping the smallest `(d, u)`.
3. **`if d > dist[u]: continue`.** Drop this line and a vertex is processed
   once per push rather than once in total.
4. Relax each `(v, w)` in `adj[u]`: `dist[u] + w < dist[v]` means a better
   route, so set `dist[v] = dist[u] + w` and push `(dist[v], v)`.
5. Return `dist` once the heap empties.

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

    class CountedEdges(list):
        def __init__(self, edges):
            super().__init__(edges)
            self.scans = 0

        def __iter__(self):
            self.scans += 1
            return super().__iter__()

    # Vertex 1 is first discovered at 10, then improved to 2 through vertex 2.
    # Its old (10, 1) heap entry must not scan vertex 1's edges a second time.
    edges_from_one = CountedEdges([(3, 1)])
    with_stale_entry = [
        [(1, 10), (2, 1)],
        edges_from_one,
        [(1, 1)],
        [],
    ]
    assert dijkstra(with_stale_entry, 0) == [0, 2, 1, 3]
    assert edges_from_one.scans == 1


test_dijkstra()

print("Shortest distances from 0:", dijkstra(WEIGHTED, 0))
```

## What one negative edge does to it

Break `prefix ≤ whole route` and a vertex can be popped while a cheaper route to it is
still unfound. Three edges are enough to do it:

```
directed edges, weight on the arrow; `dist 1<-2` means dist[1] becomes 2

0 --2--> 1      pop 0  (d=0)   dist 1<-2, 2<-5
0 --5--> 2      pop 1  (d=2)   dist 3<-3     <-- vertex 1 popped at 2, reachable for 1
1 --1--> 3      pop 3  (d=3)   nothing improves
2 -(-4)-> 1     pop 2  (d=5)   dist 1<-1     (5 + -4 = 1 beats 2)
                pop 1  (d=1)   dist 3<-2     (repairs the 3 that the bad pop produced)
                pop 3  (d=2)

true distances: [0, 1, 5, 2]
```

Vertex 1 is popped at 2, and 2 is not its shortest distance: `0 -> 2 -> 1` costs
`5 + -4 = 1`. The prefix `0 -> 2` costs 5, more than the 1 the whole route costs, which is
the broken link made concrete.

The answer still comes out right here, and that is worth being precise about. Because an
improvement pushes a fresh entry rather than skipping an already-popped vertex, the wrong
commitment gets overwritten and re-processed, and the damage it did downstream (vertex 3 at
3) gets repaired on the second pass. What is lost is the bound: vertices 1 and 3 are each
scanned twice below, and on a larger graph that re-processing compounds, up to exponentially.

The usual optimization is the one that turns this from slow into wrong. Track which
vertices are settled and skip them on arrival, `if done[u]: continue`, and there is no
second pass: vertex 3 keeps the 3 it computed from vertex 1's superseded 2, even though
`dist[1]` was later corrected to 1. The array ends up disagreeing with itself.

A negative *cycle* is worse than either. Each lap around it lowers every distance on it, so
there is no shortest route to converge on and the loop never ends. Bellman-Ford is the
algorithm for negative weights: it relaxes every edge V-1 times instead of trusting an
order of pops, and a V-th round that still improves something is how it reports the cycle
rather than spinning on it.

**Time:** exponential in the worst case, and non-terminating on a negative cycle &nbsp;
**Space:** O(V + E)

```python
def dijkstra_scans(adj, src):
    """dijkstra, plus how many times each vertex's edges were scanned."""
    n = len(adj)
    dist = [math.inf] * n
    scans = [0] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        scans[u] += 1
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    return dist, scans


def dijkstra_settled(adj, src):
    """Dijkstra with the usual 'a popped vertex is done' shortcut."""
    n = len(adj)
    dist = [math.inf] * n
    done = [False] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        d, u = heapq.heappop(heap)
        if done[u]:  # settled, so never looked at again
            continue
        done[u] = True
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    return dist


# 0 --2--> 1 --1--> 3, plus 0 --5--> 2 --(-4)--> 1
NEGATIVE = [
    [(1, 2), (2, 5)],  # 0
    [(3, 1)],          # 1
    [(1, -4)],         # 2
    [],                # 3
]


def test_negative_edge():
    # by hand: 0 -> 2 -> 1 costs 1, so 0 -> 2 -> 1 -> 3 costs 2
    truth = [0, 1, 5, 2]

    # non-negative weights: every vertex is final when popped, so one scan each
    dist, scans = dijkstra_scans(WEIGHTED, 0)
    assert dist == [0, 4, 12, 8, 6, 15]
    assert scans == [1, 1, 1, 1, 1, 1]

    # one negative edge: the re-push repairs the answer...
    dist, scans = dijkstra_scans(NEGATIVE, 0)
    assert dist == truth
    # ...by popping vertices 1 and 3 a second time, which is the lost bound
    assert scans == [1, 2, 1, 2]

    # skipping settled vertices removes the repair, so vertex 3 keeps a
    # distance built on vertex 1's superseded 2 while dist[1] itself is fixed
    assert dijkstra_settled(NEGATIVE, 0) == [0, 1, 5, 3] != truth
    # the same shortcut is correct, and normal, when no weight is negative
    assert dijkstra_settled(WEIGHTED, 0) == dijkstra(WEIGHTED, 0)


test_negative_edge()

print("negative edge, distances:", dijkstra_scans(NEGATIVE, 0)[0])
print("negative edge, scans per vertex:", dijkstra_scans(NEGATIVE, 0)[1])
print("negative edge, settling too early:", dijkstra_settled(NEGATIVE, 0))
```

## Tracking the Path

Distances alone don't say *which* route achieved them. `parent[v]` is **the vertex that
`v`'s current best distance came through**: written at the moment that distance improves,
overwritten if a better route turns up later. Every reachable vertex other than the source
has one, no parent is further from the source than its child is, and together they form a
shortest-path **tree** rooted at the source.

One back-pointer per vertex is what makes this free. Storing whole paths would copy up to V
vertices on every improvement; a predecessor is a single write, and the route is rebuilt
once, at the end, by walking backwards from the destination and reversing.

On the stale-note graph from [Relaxing an edge](#relaxing-an-edge),
`0->1 (10), 0->2 (1), 2->1 (1), 1->3 (1)`, vertex 1 first gets
distance 10 through 0, then distance 2 through 2. The same two improvements
write `parent[1]` as `0`, then replace it with `2`:

```
parent [None, 2, 0, 1]
follow parent from 3: [3, 1, 2, 0]   reverse: [0, 2, 1, 3]
```

The parent changes exactly when the distance changes, so it always describes the
route responsible for the current best distance.

`parent[src]` is never written, so it stays `None` and that is what stops the walk. An
unreachable destination is caught before the walk starts, by its infinite distance.

**Time:** O((V + E) log V) &nbsp; **Space:** O(V)

**Recipe**

1. Identical to `dijkstra` plus a `parent` array of `None`.
2. Inside the relaxation, alongside `dist[v] = dist[u] + w`, record
   `parent[v] = u`. **Inside the `if`, not beside it** - recording on every
   examined edge rather than every improving one corrupts the tree.
3. After the loop, `dist[dst] == inf` means unreachable: return `[]` before
   trying to walk anything.
4. Otherwise start at `node = dst`, append and follow `parent[node]` until it
   is `None`, then return the list reversed.

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
    # every reconstructed path starts at the source, ends at the destination,
    # uses only real edges, and costs exactly the distance computed for it
    weights = {(u, v): w for u in range(len(WEIGHTED)) for v, w in WEIGHTED[u]}
    dist = dijkstra(WEIGHTED, 0)
    for dst in range(len(WEIGHTED)):
        path = dijkstra_path(WEIGHTED, 0, dst)
        assert path[0] == 0 and path[-1] == dst
        assert sum(weights[edge] for edge in pairwise(path)) == dist[dst]


test_dijkstra_path()

print("Shortest path 0 -> 5:", dijkstra_path(WEIGHTED, 0, 5))
```
