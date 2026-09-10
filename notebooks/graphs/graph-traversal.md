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

# Graph Traversal

Reaching every vertex is the easy part. The real question is *which vertex to take
next* out of the ones you have found but not yet looked at. One thing decides it: the
container those waiting vertices sit in. That container is the **frontier**.

Change the container and a different algorithm falls out, with nothing else in the loop
touched:

| Frontier | What comes out next | Algorithm |
|---|---|---|
| queue (`deque`), first in first out | the vertex found earliest | **BFS**, ring by ring from the source |
| stack (or recursion), last in first out | the vertex found most recently | **DFS**, as deep as possible first |
| min-heap keyed by cost | the cheapest vertex found | [Dijkstra](dijkstra.md), shortest weighted path |

So BFS and DFS are not two algorithms to memorise. They are one algorithm making one
choice differently. Both visit every vertex and every edge once, so both are
**O(V + E)** on an adjacency list, with O(V) auxiliary space for the frontier and the
visited marks.

Two pieces of state run all of it:

- the **frontier**: vertices found but not yet expanded. Its container's discipline
  is the whole choice of algorithm.
- **`visited`**: the vertices that must never enter the frontier again.

`visited` is what makes the traversal finite and linear, and the invariant is worth
stating exactly: **a vertex enters the frontier at most once, so each edge is examined
a bounded number of times** - twice on an undirected adjacency list, once from each
end. Remove `visited` and a cycle sends the walk round forever; weaken it and the same
vertex is expanded repeatedly, which is how an O(V + E) loop quietly becomes worse.

See [Graph Basics](graph-basics.md) for representations.


![BFS vs DFS Traversal Order](images/bfs-vs-dfs.png)


## Does `visited` mean discovered, or processed?

One word, two different marks, and choosing the wrong one is the most common way these
loops break. The difference is *when* the mark goes down:

- **Discovered** - marked as it goes **into** the frontier. It means "claimed": some
  route to this vertex has been found, and no other route may claim it. Nothing has
  been done with it yet. **BFS uses this.**
- **Processed** - marked as it comes **out of** the frontier. It means "expanded": its
  neighbours have been looked at. **The iterative DFS below uses this**, and the
  recursive DFS marks on entry, which is the same instant as marking on push.

Marking time is not a stylistic choice. It decides three things:

1. **How many copies of a vertex the frontier can hold.** Discovered-marking admits
   each vertex once, so the frontier holds at most V entries. Processed-marking lets
   every incoming edge push its own copy, so the frontier can grow to O(E). BFS on the
   complete graph on 8 vertices enqueues 8 vertices when it marks on enqueue, and 29
   when it marks on dequeue.
2. **Whether a vertex can be emitted twice.** With processed-marking, the duplicates
   in the frontier are real, so the loop needs a second guard on the way out
   (`if visited[u]: continue`) or the same vertex is reported more than once.
3. **Whether BFS's distance guarantee survives at all.** This one is not repairable by
   a guard, and the next section is about why.


## Test graph helper

Each notebook is executed standalone by `make test`, so this rebuilds the adjacency
list locally rather than importing it from the basics notebook.

```python
from collections import deque


def build_adj(n, edges):
    """Adjacency list for an undirected graph on vertices 0..n-1."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def test_build_adj():
    assert build_adj(3, [(0, 1), (1, 2)]) == [[1], [0, 2], [1]]


test_build_adj()
```

## Checking a traversal without pinning one order

A traversal's visit order is not unique. It depends on the order neighbours happen to sit
in the adjacency list, which is an accident of the order the edges were added. Asserting
one exact list therefore tests two things at once and cannot tell them apart: the
algorithm being right, and the input happening to be in a particular order. Rewrite the
edge list in a different order and a correct implementation starts failing.

So the tests below check the **property each traversal actually promises**, and pin an
exact order only as a separate, clearly-labelled statement about `build_adj`'s append
order.

- BFS promises: every reachable vertex once, in non-decreasing distance from the source.
- DFS promises: every reachable vertex once, in an order some depth-first walk could
  produce - each new vertex hangs off the current path, never off an abandoned branch.
- A component sweep promises: every vertex exactly once, with each component in one
  unbroken run.

`distances` computes distance a layer at a time, from the definition, without a queue -
so it is independent of the thing it is used to check rather than a restatement of it.

```python
def distances(adj, s):
    """Distance from s to every reachable vertex, expanding whole layers."""
    dist = {s: 0}
    layer, d = {s}, 0
    while layer:
        d += 1
        nxt = set()
        for u in layer:
            for v in adj[u]:
                if v not in dist:
                    dist[v] = d
                    nxt.add(v)
        layer = nxt
    return dist


def is_bfs_order(adj, s, order):
    """Every reachable vertex once, in non-decreasing distance from s."""
    dist = distances(adj, s)
    if sorted(order) != sorted(dist):  # no repeats, nothing missed
        return False
    return all(dist[a] <= dist[b] for a, b in zip(order, order[1:]))


def is_dfs_order(adj, s, order):
    """Every reachable vertex once, in an order some DFS could produce.

    Replays the walk, keeping the path from s to where it stands. A new vertex
    is legal only if it is adjacent to some vertex still on that path, after
    backtracking off the vertices it does not touch. Jumping to a branch that
    was already left behind is what this rejects.
    """
    if not order or order[0] != s or sorted(order) != sorted(distances(adj, s)):
        return False
    path = [s]
    for w in order[1:]:
        while path and w not in adj[path[-1]]:
            path.pop()
        if not path:
            return False
        path.append(w)
    return True


def is_component_grouped(adj, order):
    """Every vertex once, each component in one unbroken run."""
    if sorted(order) != list(range(len(adj))):
        return False
    runs = []
    for u in order:
        comp = frozenset(distances(adj, u))
        if not runs or runs[-1] != comp:
            runs.append(comp)  # a run ended, a new component starts
    return len(runs) == len(set(runs))  # no component resumed later


def test_checkers():
    #   0 --- 1 --- 3
    #   |
    #   2
    adj = build_adj(4, [(0, 1), (0, 2), (1, 3)])
    assert distances(adj, 0) == {0: 0, 1: 1, 2: 1, 3: 2}
    assert is_bfs_order(adj, 0, [0, 1, 2, 3])
    assert is_bfs_order(adj, 0, [0, 2, 1, 3])  # either neighbour may go first
    assert not is_bfs_order(adj, 0, [0, 1, 3, 2])  # 3 is further out than 2
    assert not is_bfs_order(adj, 0, [0, 1, 2])  # 3 never reached
    assert not is_bfs_order(adj, 0, [0, 1, 2, 2, 3])  # 2 emitted twice
    assert is_dfs_order(adj, 0, [0, 1, 3, 2])  # dive down 1 before taking 2
    assert not is_dfs_order(adj, 0, [0, 1, 2, 3])  # 3 abandoned, then resumed
    assert is_component_grouped(adj, [0, 1, 3, 2])
    two = build_adj(4, [(0, 1), (2, 3)])
    assert is_component_grouped(two, [0, 1, 2, 3])
    assert not is_component_grouped(two, [0, 2, 1, 3])  # interleaved


test_checkers()
```

# Breadth-First Search (BFS)

> **Mental model.** The queue holds vertices you have found but not yet looked at, and
> because it is first in, first out, it stays sorted by distance from the source.
> Everything one edge away leaves the queue before anything two edges away. The order
> vertices come out *is* order of increasing distance, and that is the whole reason BFS
> gives shortest paths when every edge costs the same.
>
> **Load-bearing:** a vertex is marked visited when it is **enqueued**, not
> when it is dequeued. `visited` does not mean "already looked at", it means "already
> claimed". The diagram below shows what a late mark costs.

Why is it safe to claim a vertex the first time you see it and never look again? Because
the queue only ever holds vertices from one distance and the next, so the first route
that reaches a vertex is a shortest one. There is no better route still coming. Throwing
away every other way in loses nothing.

That whole argument rests on one thing: every edge costs the same. Give one edge a cost
of 10 and "fewest edges" stops meaning "cheapest", so the first arrival is no longer the
best one and the queue can no longer be trusted. Swapping the queue for a min-heap keyed
by total cost repairs exactly that, and the repair is [Dijkstra](dijkstra.md).

And the argument also rests on the mark going down at the right moment, because
"the queue holds only two distances at a time" is not a fact about queues, it is
something discovered-marking maintains. Mark on dequeue instead and a vertex gets
enqueued once per edge pointing at it, so copies of a distance-2 vertex sit behind
distance-1 vertices that have not yet been expanded. The layers smear together, the
vertex is emitted more than once, and the order is no longer sorted by distance. A
`visited` guard after the dequeue would suppress the duplicate emission, but it cannot
un-mix the layers, and the queue has already paid O(E) space to hold them.

![Mark on enqueue, not on dequeue](images/bfs-enqueue-marking.png)

## Applications
- Find shortest path in unweighted graph
- Web crawlers in search engines
- Peer-to-peer networks
- Social network search
- Garbage collection (Cheney's algorithm)
- Cycle detection
- Ford-Fulkerson algorithm
- Broadcasting in networking

**Time:** O(V + E) &nbsp; **Space:** O(V) for the queue and the visited list

**Recipe**

1. Initialize: `visited = [False] * len(adj)` only if the caller passed none, and
   `order = []`. **Never put `visited=[False] * n` in the signature** - Python
   evaluates a default once, at definition, so every call would share one list.
   Taking `visited` as an argument is what lets the component sweep below reuse
   this function instead of duplicating it.
2. Frontier: `q = deque([s])`, and `visited[s] = True` in the same breath.
   **Mark the source as you seed it** or its own neighbour enqueues it again.
3. Each step: `u = q.popleft()`, then `order.append(u)`. **`popleft` is O(1);
   `list.pop(0)` is O(n) and makes the traversal quadratic.**
4. Neighbour update: for every `v in adj[u]` with `not visited[v]`, set
   `visited[v] = True` **before** `q.append(v)`. **Marking on dequeue instead
   returns `[0, 1, 2, 2]` on the triangle `[[1, 2], [0, 2], [0, 1]]`**, and the
   layers stop being ordered by distance.
5. Return `order`, the dequeue sequence. `visited` is the second output, mutated
   in place - that is the channel the caller reads to continue across
   components.

```python
def bfs(adj, s, visited=None):
    """
    BFS from source vertex s. Returns vertices in visit order.

    Pass an existing `visited` list to continue a traversal across components.

        0
      /   \
    1      2
          / \
         3   4

    From 0: [0, 1, 2, 3, 4]
    """
    if visited is None:
        visited = [False] * len(adj)
    q = deque([s])
    visited[s] = True
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True  # mark on enqueue, not on dequeue
                q.append(v)
    return order


def test_bfs():
    adj = build_adj(4, [(0, 1), (0, 2), (1, 2), (1, 3)])
    # the promise: every reachable vertex once, distances non-decreasing
    assert is_bfs_order(adj, 0, bfs(adj, 0))
    assert is_bfs_order(adj, 3, bfs(adj, 3))
    # and with build_adj's append order, the exact order is this one
    assert bfs(adj, 0) == [0, 1, 2, 3]
    assert bfs(adj, 3) == [3, 1, 0, 2]
    # single vertex, no edges
    assert bfs([[]], 0) == [0]
    # only the source's component is reached
    adj = build_adj(5, [(0, 1), (2, 3)])
    assert bfs(adj, 0) == [0, 1]
    assert is_bfs_order(adj, 0, bfs(adj, 0))
    # visited is an output too: the caller can see what was claimed
    visited = [False] * 5
    bfs(adj, 0, visited)
    assert visited == [True, True, False, False, False]


test_bfs()
```

## What a late mark costs

Worth pinning this down rather than trusting it. `bfs_late_mark` below is the same loop
with `visited[v] = True` moved from the enqueue to the dequeue, and it fails in both of
the ways the marking discussion predicts: a vertex is emitted twice, and on a dense graph
the queue swells with copies of vertices already claimed. There is no recipe here: this is
the version not to write.

The queue is where it goes wrong on this four-vertex graph:
`build_adj(4, [(0, 1), (0, 2), (1, 3), (1, 2)])`:

```
front of the queue on the left; a vertex is marked only as it leaves the front

after 0 leaves:  queue [1, 2]     order [0]
after 1 leaves:  queue [2, 3, 2]  order [0, 1]        <- 1 enqueues 2 again
after 2 leaves:  queue [3, 2]     order [0, 1, 2]
after 3 leaves:  queue [2]        order [0, 1, 2, 3]
after 2 leaves:  queue []         order [0, 1, 2, 3, 2]
```

The second row is the whole defect: 0 left the queue having claimed only itself,
so when 1 scans its neighbours, 2 is still unmarked and goes in a second time.
Both symptoms fall out of that last line at once - 2 is emitted twice, and the
second copy is a **distance-1 vertex coming out behind distance-2 vertex 3**, so
the order no longer sorts by distance. The triangle below pins the duplicate
emission, and the complete graph on eight vertices pins the space cost.

```python
def bfs_late_mark(adj, s):
    """BFS marking on dequeue. Returns (order, number of enqueues)."""
    visited = [False] * len(adj)
    q = deque([s])
    order, enqueues = [], 1
    while q:
        u = q.popleft()
        visited[u] = True  # too late: copies of u may already be in the queue
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                q.append(v)
                enqueues += 1
    return order, enqueues


def bfs_enqueues(adj, s):
    """How many times bfs enqueues a vertex - once each, by construction."""
    visited = [False] * len(adj)
    q = deque([s])
    visited[s] = True
    enqueues = 1
    while q:
        for v in adj[q.popleft()]:
            if not visited[v]:
                visited[v] = True
                q.append(v)
                enqueues += 1
    return enqueues


def test_late_mark_costs():
    triangle = [[1, 2], [0, 2], [0, 1]]
    order, _ = bfs_late_mark(triangle, 0)
    assert order == [0, 1, 2, 2]  # both 0 and 1 enqueue 2
    assert not is_bfs_order(triangle, 0, order)
    assert bfs(triangle, 0) == [0, 1, 2]  # marking on enqueue
    # on a dense graph, one enqueue per vertex turns into nearly one per edge
    k8 = [[v for v in range(8) if v != u] for u in range(8)]
    assert bfs_enqueues(k8, 0) == 8  # V
    assert bfs_late_mark(k8, 0)[1] == 29  # heading for E = 28
    assert is_bfs_order(k8, 0, bfs(k8, 0))


test_late_mark_costs()
```

## Disconnected Graphs

One BFS only reaches what is reachable *from its source*. To touch every vertex, loop
over all of them and start a fresh BFS from each one not yet visited.

The restart is safe because of what `visited` means at the moment the outer loop looks at
it. `visited[u]` is still `False` only if no earlier traversal could reach `u`, which is
exactly the statement that `u` lies in no component seen so far. So each restart opens a
new component, and the count of restarts is the count of components.

Nothing is revisited because **`visited` is created once and threaded through the calls,
never reset**. That keeps the one-enqueue-per-vertex invariant across the whole sweep
rather than per call: a vertex `w` reached in component 3 is already `True` when the outer
loop reaches index `w`, so the loop skips it, and no inner traversal can cross into an
earlier component because every vertex there is already claimed. Total work is Θ(V) for
the sweep plus O(V + E) shared across all the traversals, so O(V + E) however many
components there are - the same bound as a single connected graph.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Initialize **one** `visited = [False] * len(adj)` and `order = []` *outside*
   the loop. **Create `visited` inside the loop and vertices repeat across
   components**, because each call starts blind.
2. Sweep `u` over `range(len(adj))`; on `not visited[u]`, run `bfs(adj, u,
   visited)` and `order +=` its result. The shared list is the only link between
   the calls.
3. Return `order`: every vertex exactly once, each component in one unbroken run,
   components ordered by their smallest vertex.

```python
def bfs_disconnected(adj):
    """BFS over every component. Returns all vertices in visit order."""
    visited = [False] * len(adj)
    order = []
    for u in range(len(adj)):
        if not visited[u]:
            order += bfs(adj, u, visited)
    return order


def test_bfs_disconnected():
    # two components: {0,1,2,3} and {4,5,6}
    adj = [[1, 2], [0, 3], [0, 3], [1, 2], [5, 6], [4, 6], [4, 5]]
    order = bfs_disconnected(adj)
    # the promise: every vertex once, no component interleaved with another
    assert is_component_grouped(adj, order)
    assert is_bfs_order(adj, 0, order[:4])  # each run is a BFS of its component
    assert is_bfs_order(adj, 4, order[4:])
    assert order == [0, 1, 2, 3, 4, 5, 6]  # with build order, exactly this
    # every vertex appears exactly once, even with no edges at all
    isolated = [[], [], []]
    assert sorted(bfs_disconnected(isolated)) == [0, 1, 2]
    assert bfs_disconnected([]) == []


test_bfs_disconnected()
```

## Counting Connected Components

Exactly the loop above with a counter. The insight is the restart argument stated once
more: the outer loop finds `visited[u]` still `False` only when no earlier traversal could
reach `u`, so each time it does, that is one component nobody has entered before.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Initialize the same single shared `visited = [False] * len(adj)`, plus
   `count = 0`.
2. Same sweep, but `count += 1` **inside the `if`, once per restart** - once per
   vertex counts vertices, not components.
3. Call `bfs(adj, u, visited)` for its side effect on `visited` and discard the
   returned order. Return `count`; the number of restarts is the whole answer.

```python
def count_components_bfs(adj):
    """Count connected components in an undirected graph using BFS."""
    visited = [False] * len(adj)
    count = 0
    for u in range(len(adj)):
        if not visited[u]:
            count += 1
            bfs(adj, u, visited)
    return count


def test_count_components_bfs():
    # components: {0,1,2}, {3,4}, {5,6,7}
    adj = [[1, 2], [0, 2], [0, 1], [4], [3], [6, 7], [5], [5]]
    # the promise, stated without walking the graph the same way: the number of
    # distinct reachable-sets is the number of components
    expected = len({frozenset(distances(adj, u)) for u in range(len(adj))})
    assert count_components_bfs(adj) == expected == 3
    # fully connected
    assert count_components_bfs(build_adj(3, [(0, 1), (1, 2)])) == 1
    # no edges - every vertex is its own component
    assert count_components_bfs([[], [], []]) == 3
    assert count_components_bfs([]) == 0


test_count_components_bfs()
```

# Depth-First Search (DFS)

> **Mental model.** The same loop as BFS with one substitution: the frontier is a stack,
> so the vertex that comes out next is the one found most recently. That single change
> makes the walk dive. It always carries on from where it just was, and backs up only
> when there is nowhere new to go. Recursion hides the stack rather than removing it -
> the call stack *is* the frontier, and `dfs_rec` never mentions a stack because Python
> is keeping it.
>
> **Load-bearing:** DFS says nothing about distance. The first route it finds to
> a vertex can be the longest one in the graph, because it commits to a branch before
> looking at the alternatives. Only BFS earns the shortest-path guarantee.

Nothing about depth-first order requires recursion. Recursion is just the cheapest way to
get a last-in-first-out frontier, since the language already maintains one. The diagram at
the top of the notebook shows the two orders side by side.

What DFS gives up in distance it gets back in structure. Because a vertex is entered and
then finished only after everything below it is finished, the traversal knows when a
branch is complete. That "finished" moment is what
[cycle detection](cycle-detection.md) and [topological sort](topological-sort.md) are
built on, and it is not something BFS can offer. Note that this needs a *second* mark:
`visited` says "entered", and "finished" is a different instant, recorded separately by
those algorithms. Marking on entry is what stops a cycle from re-entering a vertex already
sitting on the call stack.

## Applications
- Cycle detection
- Topological sorting
- Strongly connected components
- Solving maze puzzles
- Path finding

**Time:** O(V + E) &nbsp; **Space:** O(V) - the recursion can reach depth V on a path
graph

**Recipe**

1. Initialize in the wrapper: `visited = [False] * len(adj)`, `order = []`, then
   call the helper on `s`. The helper owns no state of its own.
2. On entry to `u`: `visited[u] = True`, then `order.append(u)`. **Marking on
   entry, before any recursion**, is the whole guard - a cycle would otherwise
   re-enter a vertex that is already on the call stack.
3. Neighbour update: for every `v in adj[u]`, recurse only `if not visited[v]`.
   The push and the pop are the call and the return; there is no container to
   manage. **There is no base case** - that guard is the only thing terminating
   this, because a graph has cycles and `adj[u]` is never a smaller subproblem.
4. Return nothing. `order` and `visited` are the outputs, mutated in place, which
   is why the caller must pass the same list rather than reassign it.

```python
def dfs_rec(adj, u, visited, order):
    """Recursive DFS helper - appends vertices to order as they are visited."""
    visited[u] = True
    order.append(u)
    for v in adj[u]:
        if not visited[v]:
            dfs_rec(adj, v, visited, order)


def dfs(adj, s):
    """
    DFS from source vertex s. Returns vertices in visit order.

         0
      /     \
      1      4
      |    /   \
      2   5  -  6
      |
      3

    From 0: [0, 1, 2, 3, 4, 5, 6]
    """
    visited = [False] * len(adj)
    order = []
    dfs_rec(adj, s, visited, order)
    return order


def test_dfs():
    adj = [[1, 4], [0, 2], [1, 3], [2], [0, 5, 6], [4, 6], [4, 5]]
    # the promise: every reachable vertex once, each one hanging off the path
    # the walk currently stands on
    assert is_dfs_order(adj, 0, dfs(adj, 0))
    assert is_dfs_order(adj, 5, dfs(adj, 5))
    assert dfs(adj, 0) == [0, 1, 2, 3, 4, 5, 6]  # with this append order
    # goes deep before wide - contrast with BFS on the same graph
    adj = build_adj(4, [(0, 1), (0, 2), (1, 3)])
    assert dfs(adj, 0) == [0, 1, 3, 2]
    assert bfs(adj, 0) == [0, 1, 2, 3]
    # and the orders are not interchangeable: each fails the other's property
    assert not is_bfs_order(adj, 0, dfs(adj, 0))
    assert not is_dfs_order(adj, 0, bfs(adj, 0))
    assert dfs([[]], 0) == [0]


test_dfs()
```

### DFS over components

The same outer loop as BFS, and the same reason it is safe: an unvisited vertex at the top
of the sweep is one no earlier walk could reach, so it opens a fresh component, and the
shared `visited` keeps the walks from crossing into ground already covered. The number of
components is a property of the graph, not of how you walk it, so BFS and DFS must agree
on the count - which the test asserts directly.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Initialize one shared `visited = [False] * len(adj)` outside the sweep, exactly
   as in the BFS pair, plus `order = []` or `count = 0`.
2. Sweep `u` over `range(len(adj))`; on `not visited[u]`, call `dfs_rec(adj, u,
   visited, order)`. **`dfs_rec` returns nothing**, so the collecting version must
   hand it the *same* `order` list every call - there is no result to concatenate.
3. `count_components_dfs` passes a throwaway `[]` for the order, since only the
   restart count carries information. Return `order` or `count`.

```python
def dfs_disconnected(adj):
    """DFS over every component. Returns all vertices in visit order."""
    visited = [False] * len(adj)
    order = []
    for u in range(len(adj)):
        if not visited[u]:
            dfs_rec(adj, u, visited, order)
    return order


def count_components_dfs(adj):
    """Count connected components in an undirected graph using DFS."""
    visited = [False] * len(adj)
    count = 0
    for u in range(len(adj)):
        if not visited[u]:
            count += 1
            dfs_rec(adj, u, visited, [])
    return count


def test_dfs_disconnected():
    # components: {0,1,2} and {3,4}
    adj = [[1, 2], [0, 2], [0, 1], [4], [3]]
    order = dfs_disconnected(adj)
    assert is_component_grouped(adj, order)
    assert is_dfs_order(adj, 0, order[:3])  # each run is a DFS of its component
    assert is_dfs_order(adj, 3, order[3:])
    assert order == [0, 1, 2, 3, 4]  # with this append order
    assert count_components_dfs(adj) == 2
    # BFS and DFS must agree on the number of components
    assert count_components_dfs(adj) == count_components_bfs(adj)
    assert count_components_dfs([[], [], []]) == 3
    assert count_components_dfs([]) == 0


test_dfs_disconnected()
```

## Iterative DFS

Taking the stack out of Python's hands changes nothing about the algorithm. It changes who
pays for it. Python allows only about 1000 nested calls, and recursive DFS needs one call
per vertex on the current path, so a long chain crashes it. The test walks a 2000-vertex
path graph for exactly that reason.

Making the stack explicit forces the marking decision into the open. Recursion marks on
entry, which is marking on push, so `visited` means discovered and no vertex is ever on
the stack twice. This version marks **on pop** instead, so `visited` means processed, and
that has one consequence you must handle: between a vertex being pushed and being popped,
every other neighbour that sees it pushes its own copy, so the stack holds duplicates.
Hence `if visited[u]: continue` immediately after the pop, without which a vertex is
emitted once per copy. Marking at push instead would make `visited` mean discovered again
and keep the stack duplicate-free, which is strictly cheaper in space; it is not done here
only because it changes the visit order, and the test compares this traversal against
`dfs_rec` directly. The `not visited[v]` test before pushing is pruning, not correctness -
it shrinks the stack, but the pop guard is what guarantees each vertex is emitted once.

Pushing `reversed(adj[u])` is the second cosmetic choice: it makes the first neighbour pop
first, matching recursion. Without it the result is a different but equally valid DFS,
which is exactly the kind of difference `is_dfs_order` accepts and an exact-list assert
would reject.

**Time:** O(V + E) &nbsp; **Space:** O(V) vertices but O(E) stack entries, since a
vertex can be pushed once per incoming edge

**Recipe**

1. Initialize `visited = [False] * len(adj)`, `stack = [s]`, `order = []`. **`s`
   is not marked here**, unlike BFS - this loop marks on the way out.
2. Each step: `u = stack.pop()`, then **`if visited[u]: continue`**. Skip this and
   duplicates already sitting on the stack are emitted: `[0, 1, 2, 3, 4, 5, 6, 6]`
   on this section's test graph.
3. Mark and emit: `visited[u] = True`, `order.append(u)`, in that order.
4. Neighbour update: `stack.append(v)` for every `v in reversed(adj[u])` with `not
   visited[v]`. The guard is pruning only; step 2 is what enforces uniqueness.
   **`reversed` matters only for matching `dfs_rec`** - drop it and the walk is a
   different, still valid DFS.
5. Return `order`.

```python
def dfs_iterative(adj, s):
    """DFS from s using an explicit stack. Returns vertices in visit order."""
    visited = [False] * len(adj)
    stack = [s]
    order = []
    while stack:
        u = stack.pop()
        if visited[u]:  # may have been queued twice before being popped
            continue
        visited[u] = True
        order.append(u)
        # reversed so the first neighbour is popped first, matching dfs_rec
        for v in reversed(adj[u]):
            if not visited[v]:
                stack.append(v)
    return order


def test_dfs_iterative():
    adj = [[1, 4], [0, 2], [1, 3], [2], [0, 5, 6], [4, 6], [4, 5]]
    # the promise, independent of which valid DFS this happens to be
    assert is_dfs_order(adj, 0, dfs_iterative(adj, 0))
    assert is_dfs_order(adj, 6, dfs_iterative(adj, 6))
    # reversed() is what makes it agree with the recursive walk exactly
    assert dfs_iterative(adj, 0) == dfs(adj, 0)
    adj = build_adj(4, [(0, 1), (0, 2), (1, 3)])
    assert dfs_iterative(adj, 0) == [0, 1, 3, 2]
    # deep path graph would blow the recursion limit at scale; iterative is fine
    path = build_adj(2000, [(i, i + 1) for i in range(1999)])
    assert dfs_iterative(path, 0) == list(range(2000))
    assert dfs_iterative([[]], 0) == [0]


test_dfs_iterative()
```

# Python Built-in: BFS on a `dict` Graph

There is no graph type in the standard library, but `deque` gives an O(1) `popleft` for
the BFS frontier and `defaultdict(list)` holds the adjacency list. Vertices can be any
hashable value.

The algorithm itself is unchanged apart from two substitutions: a `set` replaces the
boolean visited list (vertices are no longer indices `0..n-1`), and a missing key yields
`[]` instead of raising.

Worth knowing that the `defaultdict` convenience cuts both ways - reading
`graph[missing]` silently *creates* an empty entry, so the graph can grow just by being
traversed.

**Time:** O(V + E) &nbsp; **Space:** O(V)

**Recipe**

1. Initialize `visited = {start}` and `q = deque([start])`, `order = []`. Same
   discovered-marking as the list version, in a `set` because there are no
   indices to size an array from.
2. Each step: `node = q.popleft()`, `order.append(node)`.
3. Neighbour update: for `neighbor in graph[node]` not in `visited`,
   `visited.add(neighbor)` **then** `q.append(neighbor)`. **Use `graph.get(node,
   ())` if the graph must not grow** - `graph[node]` on a `defaultdict` inserts a
   key for every vertex it reads.
4. Return `order`.

```python
from collections import defaultdict


def bfs_dict(graph, start):
    """BFS over a dict-of-lists graph with arbitrary hashable vertices."""
    visited = {start}
    q = deque([start])
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                q.append(neighbor)
    return order


def test_bfs_dict():
    graph = defaultdict(list)
    for u, v in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]:
        graph[u].append(v)
        graph[v].append(u)  # undirected
    assert bfs_dict(graph, "A") == ["A", "B", "C", "D"]
    assert bfs_dict(graph, "D") == ["D", "B", "C", "A"]


test_bfs_dict()
```
