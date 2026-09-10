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

# Binary Heap

A heap is a tree that is **only half sorted, on purpose**. It promises one thing: the
smallest value is at the root. It promises nothing else. The second smallest could be
under either child, and two values in different subtrees have no relationship at all.

That weak promise is the whole point. A fully sorted array hands you the minimum for
free too, but inserting into it costs O(n), because everything after the new value
has to shift up one slot. The heap keeps only the one fact you actually asked for, and
that is why inserting costs O(log n) instead.

Two flavours, mirror images of each other:

1. **Min heap** - the smallest value is at the root, so "highest priority" means lowest value
2. **Max heap** - the largest value is at the root

| Operation | Time |
|---|---|
| Find the min | O(1) - it is the root |
| Insert | O(log n) |
| Extract min | O(log n) |
| Decrease key | O(log n) |
| Delete | O(log n) |
| Build from an unordered array | O(n) |

**Space:** O(n), with no pointer overhead at all - a heap is a plain array.

Reach for one when you need the smallest item over and over while new items keep
arriving: a priority queue, the next-closest vertex in Dijkstra, heapsort, the k
smallest values of a stream.

Two separate rules define a heap, and keeping them apart is what makes the code
below obvious:

- **Shape.** Every level is full except the last, and the last one fills left to
  right, leaving no gaps. A tree like that is called *complete*.
- **Order.** Every node is smaller than both of its children, in a min heap. Siblings
  and cousins are not compared, ever.

The shape rule is what buys the array representation: with no gaps, a node's index
alone says where its family is, so no node needs to store a pointer.

- Left child of node at index i: `left(i) = 2i + 1`
- Right child of node at index i: `right(i) = 2i + 2`  
- Parent of node at index i: `parent(i) = floor((i - 1)/2)`

An array is also contiguous, which means random access and cache-friendly reads, and
a complete tree is the shortest a binary tree can be, so the height is log n.

> **Mental model.** Half sorted, deliberately. The root is the minimum, everything
> else is a mess, and that trade is what makes insert and extract cheap. Every
> operation is then the same two steps: put the value in the one slot the **shape**
> allows, which is always the end of the array, then let it walk until the **order**
> allows it as well - up towards the root, or down towards the leaves.
>
> **Load-bearing:** completeness. Index arithmetic is the only thing linking a node to
> its parent and children, and it is only correct while the tree has no gaps. Break
> that and there are no pointers to fall back on. It is also why nothing is ever
> pulled out of the middle: extract min overwrites the root with the last element and
> pops the end, and delete first sifts its victim up to the root, because the end is
> the only slot that can be given up without tearing a hole in the shape.


![Heap Array to Tree Mapping](images/heap-array-tree.png)


## Which way a value walks

There are only two movements in this entire notebook - a value walking up towards the root, or
down towards the leaves - and every operation is one of them. So it is worth settling once how to
tell which, because the answer is never a judgement call.

The order rule is a statement about **pairs**: every parent is smaller than each of its two
children. A node at index `i` therefore takes part in exactly two kinds of pair - one with its
parent above, and one with each child below. When an operation writes a single value into slot
`i`, ask which of those two can now be false. **Exactly one can**, every time, and that names the
direction:

| Operation | What it does to one slot | Which pair can be broken | Walk |
|---|---|---|---|
| Build (`heapify` on `i`) | leaves `i` above two subtrees that are already finished heaps | its children | **down** |
| Insert | appends at the end, index `n-1` | its parent | **up** |
| Extract min | overwrites the root from the end; both subtrees untouched | its children | **down** |
| Decrease key | makes `arr[i]` smaller | its parent | **up** |
| Increase key | makes `arr[i]` larger | its children | **down** |

Each row is forced, not observed:

- **Insert.** The appended slot is `n-1`, and its children would be at `2n-1` and `2n`, which are
  off the end of the array. It has no children to be wrong about.
- **Extract min.** Index 0 has no parent - `parent(0)` is not a node. And the two subtrees were
  never touched, so every pair *inside* them still holds; only the two pairs involving the root
  can have broken.
- **Decrease key.** The new value is smaller than the old one, and the children were already
  larger than the old one, so they are larger than the new one too. The pair below is safe for
  free. Increase key is the mirror: the parent was already smaller than the old value, so the
  pair above is the safe one.
- **Build.** Both of `i`'s subtrees are finished, so all the pairs inside them hold. The pair
  between `i` and *its* parent is allowed to be broken here - fixing it is the job of the next
  iteration, which is precisely why the sweep runs upwards.

The two walks are also asymmetric in cost, and for a reason worth keeping. Going up, a node has
one parent, so there is nothing to choose: compare, swap, repeat. Going down there are two
children, so every step first has to pick which one - and it must be the smaller, since promoting
the larger would make it the parent of the smaller and break the rule being repaired.


## Building the heap (constructor)

You have a pile of unordered values and want a heap out of them. Sorting works, since
a sorted array obeys the order rule, but it costs O(n log n) and buys ordering you
were never going to use.

The reframe: a heap is made of smaller heaps. One value on its own is already a valid
heap, so every leaf is finished before you start. Work upwards from there. Every time
you step to a lower index you land on a node whose two subtrees are already finished
heaps, so a single sift down settles that node and finishes its subtree too.

The direction is the algorithm. Working upwards is what guarantees `heapify` is only
ever handed one bad node sitting on top of two good heaps, which is the only situation
it can repair.

Top down does not work, and it fails on four elements. Sifting the root first tells you
nothing, because the subtrees you are comparing it against are still unordered - the value
you promote is only the smallest of *three*, not of the subtree, so it can be left sitting
above something smaller that has not moved yet. Sweep `[2, 3, 4, 1]` top down and you get
`[2, 1, 4, 3]`, where the root is larger than its own left child. Bottom up on the same
input reaches `1` first, at index 1, and lifts it before the root is ever considered.

The other half of the saving is that **half the array is already done**. A node at index
`i` is a leaf exactly when `2i + 1 >= n`, and those indices are a contiguous block at the
end - the first leaf is always `(n - 2) // 2 + 1`, one past where the sweep starts. In a
1023-element heap that is 512 nodes, 50%, that `heapify` is never called on at all.

The whole build is O(n), not the O(n log n) you would expect from n sift downs. Why
that is true is worked out at the end of the notebook.

**Time:** O(n) &nbsp; **Space:** O(1) plus the recursion in `heapify`

**Recipe**

1. A heap is an **array**, not a linked structure. Index arithmetic replaces
   pointers: `parent(i) = (i - 1) // 2`, `lchild(i) = 2*i + 1`, `rchild(i) =
   2*i + 2`.
2. Those three come from numbering a complete tree level by level, left to right.
   **Derive them from a small drawing rather than memorising them; the `- 1` and
   `+ 1` are easy to misplace and the errors are silent.**
3. Store the list itself, and **default `ls` to `None`, not to `[]`**. A mutable
   default is evaluated once at definition time, so `def __init__(self, ls=[])`
   makes every heap built with no argument share one list.
4. To build from an existing list: start at the **last non-leaf node** and
   `heapify` every index down to and including `0`, in reverse.
5. The last non-leaf is the parent of the last element, `((n - 1) - 1) // 2`,
   which the code folds to `(n - 2) // 2`. **Start any later and you only
   heapify leaves; start any earlier and real non-leaves never get heapified.**
6. **The empty and single-element cases need no guard.** `(n - 2) // 2` is `-1`
   for both `n = 0` and `n = 1` - Python floors, so `-2 // 2` and `-1 // 2` are
   both `-1` - and a `while i >= 0` loop simply never runs.

```python
import math


class MinHeap:
    def __init__(self, ls=None):
        """Build a heap out of ls in place, bottom-up. Time: O(n)."""
        self.arr = [] if ls is None else ls
        i = (len(self.arr) - 2) // 2
        while i >= 0:
            self.heapify(i)
            i -= 1

    def parent(self, i):
        return (i - 1) // 2

    def lchild(self, i):
        return (2 * i) + 1

    def rchild(self, i):
        return (2 * i) + 2


def is_min_heap(arr):
    """True if every node is <= both of its children."""
    n = len(arr)
    return all(
        arr[i] <= arr[child]
        for i in range(n)
        for child in (2 * i + 1, 2 * i + 2)
        if child < n
    )


def test_is_min_heap():
    assert is_min_heap([2, 4, 8, 5, 10, 20]) is True
    assert is_min_heap([]) is True
    assert is_min_heap([1]) is True
    assert is_min_heap([10, 5, 20]) is False  # root larger than its child


test_is_min_heap()
```

## Heapify (sift down)

One node may be too big for the spot it is in. Both of its subtrees are already valid
heaps. Where does that node belong?

Of the three values in play - the node and its two children - only the smallest is
allowed on top. If that is already the node, nothing below it can be wrong either and
the work is finished. If it is a child, swap the two, and the node now faces the same
question one level lower, against a smaller subtree. It sinks until both of its
children are larger, or until it has no children left.

Swapping with the *smaller* child is not a detail. On `[5, 3, 4]`, both children
beat the parent, but only 3 belongs on top. Choosing it gives `[3, 5, 4]`.
Compare each child only with the original 5, and the right child 4 wins by accident,
giving `[4, 3, 5]`, which still has 3 below a larger parent.

**Time:** O(log n) - one comparison pair per level of descent &nbsp;
**Space:** O(log n) recursion depth

**Recipe**

1. Precondition: both children already head valid heaps, and only `i` may be out
   of place. **Nothing here repairs a scrambled array.** Every caller is
   arranged to hand `heapify` exactly this situation.
2. Read `n = len(arr)` once, and compute `lt = 2*i + 1`, `rt = 2*i + 2`.
3. `smallest = i`, so "the node is already in the right place" is the default
   answer, and the swap at the end can be guarded by a single comparison.
4. Left child: `if lt < n and arr[lt] < arr[smallest]: smallest = lt`. **The
   bounds test comes first**, and `and` short-circuits, so a leaf never reads past
   the end. Reversed, `arr[lt]` raises `IndexError` on every leaf.
5. Right child: the same test, but **against `arr[smallest]`, not `arr[i]`**,
   so `smallest` remains the smallest of every value inspected so far.
6. `smallest == i` means the node is where it belongs and everything under it was
   already valid, so stop - this is the base case, and there is no separate
   `if i >= n` guard anywhere.
7. Otherwise swap `arr[i]` and `arr[smallest]`, then **recurse on `smallest`, the
   slot the node just moved into** - not on `i`, which now holds the child's old
   value and is already settled.

```python
def heapify(self, i):
    """Sift arr[i] down until both children are larger. Time: O(log n)."""
    arr = self.arr
    lt = self.lchild(i)
    rt = self.rchild(i)
    smallest = i
    n = len(arr)
    if lt < n and arr[lt] < arr[smallest]:
        smallest = lt
    if rt < n and arr[rt] < arr[smallest]:
        smallest = rt
    if smallest != i:
        arr[smallest], arr[i] = arr[i], arr[smallest]
        self.heapify(smallest)


MinHeap.heapify = heapify


def test_create_heap():
    heap = MinHeap([10, 5, 20, 2, 4, 8])
    assert heap.arr == [2, 4, 8, 5, 10, 20]
    assert is_min_heap(heap.arr)
    # build heap only reorders - it never adds or drops elements
    assert sorted(heap.arr) == [2, 4, 5, 8, 10, 20]

    # empty and single-element heaps
    assert MinHeap().arr == []
    assert MinHeap([7]).arr == [7]

    # a default argument must not leak between instances
    assert MinHeap().arr is not MinHeap().arr

    # already a heap - unchanged
    assert MinHeap([1, 2, 3]).arr == [1, 2, 3]

    # reverse sorted is the worst case for build heap
    heap = MinHeap([9, 7, 5, 3, 1])
    assert is_min_heap(heap.arr)
    assert heap.arr[0] == 1

    # the direction is load-bearing: a top-down sweep over the same four values
    # leaves the root larger than its own child. Four elements shows it.
    top_down = MinHeap()
    top_down.arr = [2, 3, 4, 1]
    for i in range(4):
        top_down.heapify(i)
    assert top_down.arr == [2, 1, 4, 3]
    assert not is_min_heap(top_down.arr)
    assert MinHeap([2, 3, 4, 1]).arr == [1, 2, 4, 3]  # bottom-up gets it right


test_create_heap()
```

## Insert (sift up)

The shape rule picks the slot before you even look at the value. The only position
that keeps the tree complete is the next free one at the end, and appending to the end
of an array is O(1). The shape is now right and the order may well be wrong.

Which leaves one way to repair it: walk the value upwards. While it is smaller than
its parent, swap the two. It stops as soon as its parent is smaller, and reaches the
root only when it is the new minimum.

Sifting up compares with the parent and nothing else, and it does not need more. A
value that is smaller than its new parent is smaller than everything that parent
already sat above, including the child it just displaced.

**Time:** O(log n) &nbsp; **Space:** O(1)

**Recipe**

1. `arr.append(x)`, then start the walk at `i = len(arr) - 1`, the slot it
   landed in. Read the index **after** appending, or you sift the wrong slot.
2. Sift up: `while i > 0 and arr[parent(i)] > arr[i]`, with
   `parent(i) = (i - 1) // 2`.
3. Inside the loop, save `p = parent(i)` **once**, swap
   `arr[i], arr[p] = arr[p], arr[i]`, then `i = p`. Recomputing `parent(i)` after
   the swap would be reading the parent of the old index for a value that has
   already moved.
4. **`i > 0` has to be tested first.** At the root `parent(0)` is `(0-1)//2 = -1`,
   and Python reads `arr[-1]` without error, so a missing guard silently compares
   the root against the *last element of the array* instead of raising - and on a
   large heap that comparison is usually false, so the loop exits and the bug
   hides.
5. Strict `>` in the comparison, not `>=`. Equal values already satisfy the rule,
   so `>=` still terminates - the `i > 0` guard stops it - but it climbs to the
   root swapping equal values on the way, turning the O(1) best case into
   O(log n). In an array of identical values, `>` does zero swaps per insert and
   `>=` does one per level.
6. A `while` loop, not recursion: sifting up is a tail call with nothing to do on
   the way back, so the O(1) space is free.

```python
def insert(self, x):
    """Append x, sift up while smaller than its parent. Time: O(log n)."""
    arr = self.arr
    arr.append(x)
    i = len(arr) - 1
    while i > 0 and arr[self.parent(i)] > arr[i]:
        p = self.parent(i)
        arr[i], arr[p] = arr[p], arr[i]
        i = p


MinHeap.insert = insert


def test_insert():
    heap = MinHeap([2, 4, 8, 5, 10, 20])

    # new minimum bubbles all the way to the root
    heap.insert(1)
    assert heap.arr == [1, 4, 2, 5, 10, 20, 8]
    assert is_min_heap(heap.arr)

    # a large value stays at the bottom
    heap.insert(100)
    assert heap.arr[-1] == 100
    assert is_min_heap(heap.arr)

    # inserting into an empty heap
    heap = MinHeap()
    heap.insert(5)
    assert heap.arr == [5]

    # inserting in increasing order never swaps
    heap = MinHeap()
    for x in [1, 2, 3, 4, 5]:
        heap.insert(x)
    assert heap.arr == [1, 2, 3, 4, 5]

    # inserting in decreasing order swaps every time
    heap = MinHeap()
    for x in [5, 4, 3, 2, 1]:
        heap.insert(x)
    assert heap.arr[0] == 1
    assert is_min_heap(heap.arr)


test_insert()
```

## Extract min

The value you want is at index 0, and index 0 is the worst place to delete from in an
array: every remaining element shifts down a slot, O(n), which would throw away the
only reason the heap exists.

So do not remove index 0. Remove the *end*, because the end is the only slot the shape
can spare and popping it is free. Save the root value to hand back, then move the last
element into the root's slot. The shape is untouched and exactly one node is now in the
wrong place, standing on two heaps that were never disturbed. That is precisely what
`heapify` repairs, so sift it down.

The value promoted to the root came from the bottom row, so it is usually one of the
largest in the heap and normally sinks most of the way back down. In a 1023-element heap
of random values - root at height 9, leaves at height 0 - it sinks 8.7 levels on average,
and 8 or more levels 97% of the time. The saving is not in the sift; it is in never
shifting the array.

An empty heap returns `math.inf` as a sentinel rather than raising.

**Time:** O(log n) &nbsp; **Space:** O(log n)

**Recipe**

1. Empty heap, return `math.inf`, the value that loses every min comparison.
2. Save `res = arr[0]` **before anything overwrites it**; that saved value is the
   return.
3. `arr[0] = arr[-1]`, then `arr.pop()`, **in that order**. Popping first loses the
   value you were about to copy, and on a one-element heap it would leave `arr[0]`
   pointing past the end.
4. `heapify(0)`, then `return res`.
5. **A one-element heap needs no special case.** `arr[0] = arr[-1]` is a
   self-assignment, `pop()` empties the list, and `heapify(0)` reads
   `n = len(arr) == 0` so both bounds tests fail immediately.
6. **Steps 3 and 4 are a pattern, not a one-off: overwrite from the end, shrink,
   sift down.** `delete` and `heap_sort` are both built out of it - `heap_sort`
   swaps instead of overwriting, because it wants to keep the value it removes.

```python
def extract_min(self):
    """Move the last element to the root, pop, then sift the root down.

    Time: O(log n).
    """
    arr = self.arr
    if len(arr) == 0:
        return math.inf
    res = arr[0]
    arr[0] = arr[-1]
    arr.pop()
    self.heapify(0)
    return res


MinHeap.extract_min = extract_min


def test_extract_min():
    heap = MinHeap([10, 5, 20, 2, 4, 8])  # -> [2, 4, 8, 5, 10, 20]
    assert heap.extract_min() == 2
    assert heap.arr == [4, 5, 8, 20, 10]
    assert is_min_heap(heap.arr)

    # repeated extraction yields sorted order - this is heap sort
    heap = MinHeap([10, 5, 20, 2, 4, 8])
    assert [heap.extract_min() for _ in range(6)] == [2, 4, 5, 8, 10, 20]
    assert heap.arr == []

    # extracting from an empty heap returns infinity as a sentinel
    assert MinHeap().extract_min() == math.inf

    # single element
    heap = MinHeap([7])
    assert heap.extract_min() == 7
    assert heap.arr == []


test_extract_min()
```

## Decrease key

Making a value *smaller* can only break the rule in one direction: against its parent.
Its children were already larger than the old value, so they are larger than the new
one as well. So write the value in and reuse the sift-up walk from `insert`; the
children never need looking at.

This is the operation a priority queue needs when an item already in the queue turns
out to have a better priority. Python's `heapq` has no equivalent, which is why the
Dijkstra notebook pushes a duplicate entry and skips stale pops instead.

**Time:** O(log n) &nbsp; **Space:** O(1)

**Recipe**

1. Overwrite `arr[i] = x`, then sift up with the identical loop from `insert`:
   save `p = parent(i)`, swap, `i = p`, guarded by `i != 0`.
2. **Increasing a key would need `heapify` instead**, per the direction table
   above - a larger value can only be wrong against its children. Calling this
   with a larger `x` silently corrupts the heap and nothing here checks: on
   `[2, 4, 8, 5, 10, 20]`, `decrease_key(1, 99)` leaves `[2, 99, 8, 5, 10, 20]`,
   where `99` sits above `5`. Writing `arr[1] = 99` and calling `heapify(1)`
   instead gives `[2, 5, 8, 99, 10, 20]`, which is a heap.
3. **A negative `i` is not caught either.** `arr[-1] = x` writes the last slot and
   `parent(-1)` is `-1`, so the loop's `i != 0` guard is true and it compares the
   slot with itself. That is why `delete` below guards only the upper bound and
   still must not be handed a negative index.
4. `insert` is really `append` plus this loop, which is why the two bodies match
   line for line. The only difference is the guard spelling - `i != 0` here,
   `i > 0` there - and they behave identically for non-negative `i`.

```python
def decrease_key(self, i, x):
    """Overwrite arr[i] with x, then sift up. Time: O(log n)."""
    arr = self.arr
    arr[i] = x
    while i != 0 and arr[self.parent(i)] > arr[i]:
        p = self.parent(i)
        arr[p], arr[i] = arr[i], arr[p]
        i = p


MinHeap.decrease_key = decrease_key


def test_decrease_key():
    heap = MinHeap([2, 4, 8, 5, 10, 20])

    # 10 at index 4 becomes 1 and rises to the root
    heap.decrease_key(4, 1)
    assert heap.arr == [1, 2, 8, 5, 4, 20]
    assert is_min_heap(heap.arr)

    # decreasing a value that still exceeds its parent stays put
    heap = MinHeap([2, 4, 8, 5, 10, 20])
    heap.decrease_key(5, 9)  # 20 -> 9, parent is 8
    assert heap.arr == [2, 4, 8, 5, 10, 9]
    assert is_min_heap(heap.arr)

    # decreasing the root is a no-op structurally
    heap = MinHeap([2, 4, 8])
    heap.decrease_key(0, 0)
    assert heap.arr == [0, 4, 8]


test_decrease_key()
```

## Delete

Pulling a value out of the middle of the array is the one thing the shape forbids. But
there is a position you already know how to remove from: the root.

So move the victim there. Set it to `-inf` and it is now smaller than everything, which
means `decrease_key` walks it to the root by definition, not by luck. Then
`extract_min` throws that root away. No new machinery, just the two operations already
written, with `-inf` as the hinge between them.

Two O(log n) passes instead of one, in exchange for no extra code.

**Time:** O(log n) &nbsp; **Space:** O(log n)

**Recipe**

1. Guard `if i >= len(arr): return`; nothing else validates the index. **This
   checks the upper bound only** - a negative `i` walks off into the far end of the
   array, as the `decrease_key` recipe notes.
2. `decrease_key(i, -math.inf)`, then `extract_min()`, **in that order**. The
   first is what makes the second remove the right element.
3. `-math.inf` rather than "something small enough": it is smaller than every
   float and every int, so the walk to the root is guaranteed rather than
   dependent on the data.
4. **Discard what `extract_min` returns here.** It is the `-inf` this function
   just wrote, not the key that was deleted, so putting a `return` in front of
   it hands the caller a value that was never in the heap. To return the deleted
   key, read `arr[i]` *before* step 2.
5. Deleting the last index still costs two passes. `decrease_key` walks it up to
   the root and `extract_min` walks the replacement back down, where popping it
   directly would have done. Two O(log n) passes instead of one is the price of
   writing no new code.

```python
def delete(self, i):
    """Decrease arr[i] to -inf so it rises to the root, then extract it.

    Time: O(log n).
    """
    if i >= len(self.arr):
        return
    self.decrease_key(i, -math.inf)
    self.extract_min()


MinHeap.delete = delete


def test_delete():
    heap = MinHeap([2, 4, 8, 5, 10, 20])
    heap.delete(2)  # remove the 8
    assert sorted(heap.arr) == [2, 4, 5, 10, 20]
    assert is_min_heap(heap.arr)

    # deleting the root removes the minimum
    heap = MinHeap([2, 4, 8, 5, 10, 20])
    heap.delete(0)
    assert 2 not in heap.arr
    assert heap.arr[0] == 4
    assert is_min_heap(heap.arr)

    # deleting the last element
    heap = MinHeap([2, 4, 8])
    heap.delete(2)
    assert heap.arr == [2, 4]

    # out of range index is ignored
    heap = MinHeap([2, 4, 8])
    heap.delete(10)
    assert heap.arr == [2, 4, 8]

    # deleting every element one by one
    heap = MinHeap([5, 3, 9, 1])
    for _ in range(4):
        heap.delete(0)
    assert heap.arr == []


test_delete()
```

## Time complexity of build heap operation

n nodes, each sifted down at O(log n), so build heap should be O(n log n). It is O(n).
The error is in what a sift down actually costs.

`heapify` does not cost the height of the tree. It costs the height *below the node it
was called on*, since that is as far as the value can possibly sink. And a complete tree
is heavily bottom weighted: about half of all nodes are leaves, which cost nothing at
all, a quarter sit one level up and can sink one level, and so on upwards. Only the root
can sink log n levels, and there is one root.

So the total is not n copies of log n. It is, for each height, the number of nodes at
that height multiplied by that height - and the counts halve faster than the heights
grow.

### Height convention in this section: leaves at 0

**This section counts edges, not nodes: a leaf has height $h = 0$ and the root has height
$h = \lfloor \log_2 n \rfloor$.** That is the opposite of the convention used in the
[binary tree](binary-tree.md) and [AVL](avl-tree.md) notebooks, where a leaf has height 1 and an
empty tree has height 0. Every $h$ below is one *smaller* than the same node's height there.

The switch is not a matter of taste, it is what makes the sum work. The argument turns on leaves
being **free**, and $h$ is used directly as the cost of a `heapify` call, so leaves have to
evaluate to zero. Count nodes instead and every leaf is charged 1 - which alone adds $n/2$ to the
total, and worse, `heapify` on a leaf does no comparisons at all, so the charge would be fiction.

The diagram below is drawn in this convention: read the labels bottom-up, `h = 0` on the leaf row
up to `h = 3` at the root of a 15-node heap, and note that $\lfloor \log_2 15 \rfloor = 3$.

![Min heap](images/min-heap.png)

Maximum nodes at height $h$ can be computed using the following formula:
$n_h = \bigg\lceil \frac {n}{2^{h+1}} \bigg\rceil$

It is an upper bound rather than an identity - the bottom two rows of a heap are only partly
filled in general - and an upper bound is all the argument needs. For the 15-node tree in the
diagram it happens to be exact, giving 8, 4, 2, 1 nodes at heights 0 to 3, which is what the
picture shows.

The time required by `heapify` when called on a node with height $h$ is $O(h)$.
Letting $c$ be the constant implicit in asymptotic notation, the total cost can be expressed in the following:
$$= \sum_{h=0}^{\log{n}} \bigg\lceil \frac {n}{2^{h+1}} \bigg\rceil ch$$
Dropping the ceiling gives an upper bound:
$$\leqslant \sum_{h=0}^{\log{n}} \frac {n}{2^{h+1}} \cdot ch$$
Factor out $cn$:
$$= cn \sum_{h=0}^{\log{n}} \frac {h}{2^{h+1}}$$
Rewrite $2^{h+1} = 2 \cdot 2^h$:
$$= cn \sum_{h=0}^{\log{n}} \frac {h}{2 \cdot 2^{h}} = \frac{cn}{2} \sum_{h=0}^{\log{n}} \frac {h}{2^{h}}$$
Since $\frac{1}{2}$ is a constant, this simplifies to:
$$= O\!\left(cn \sum_{h=0}^{\log{n}} \frac {h}{2^{h}}\right)$$
Upperbounding to `∞`, the above can be rewritten as:
$$\leqslant cn \sum_{h=0}^{\infty} \frac {h}{2^{h}}$$
Now it's clear it's an arithmetico-geometric series (derivable by differentiating the geometric series $\sum x^k = \frac{1}{1-x}$ with respect to $x$) with $x = 1/2$, $\sum_{k=0}^{\infty} kx^k = \frac {x}{(1 - x)^2}$
Using the above formula:
$$\leqslant cn * \frac {1/2}{(1 - 1/2)^2} \\\\ = O(n)$$

The series settles on 2 - a fixed number that does not grow with n - so the whole build
is a constant multiple of n. The log factor never appears, because the nodes that could
have paid it are outnumbered.

The constant is small enough to see directly. Counting the swaps the bottom-up build performs on
a reverse-sorted array, the worst case for a min heap, gives 8 swaps at `n = 10`, 96 at `n = 100`,
992 at `n = 1000` and 99,990 at `n = 100000` - converging on `n` from below, not on the
~1.7 million that $n \log_2 n$ would predict at that last size.

>
> *Sources*
> Introduction to algorithms 4ed (Cormen et all) - section 6.3
> <https://stackoverflow.com/questions/9755721/how-can-building-a-heap-be-on-time-complexity/62177336#62177336>


## Heap Sort

Heap sort is selection sort with the slow part swapped out.

Selection sort finds the largest remaining value with a linear scan and moves it to the
end, over and over. The scan is the entire cost: n scans of O(n) each is O(n^2). But
"give me the largest, repeatedly" is exactly what a heap is for, so hold the remaining
values in a max heap instead. The maximum is at the root, so finding it costs nothing,
and repairing the heap once it is removed costs O(log n) instead of another O(n) scan.

A **max** heap, not a min heap, and that is what lets it sort in place with no second
array. The largest remaining value sits at index 0 and its final home is the last
unsorted slot, so a single swap puts it there for good and drops the displaced value
onto the root, where one sift down settles it.

### The heap boundary is not the array length

One array, two regions, and the whole correctness of the sort rests on keeping them apart:

- `arr[0:size]` is **the heap** - unordered apart from the heap rule, shrinking by one
  each round.
- `arr[size:]` is **the sorted tail** - final, correct, and never to be read or written
  again.

`len(arr)` describes the *array* and never changes. `size` describes the *heap* and is the
only boundary that matters, and after the first swap the two are no longer the same number.
Nothing in Python enforces the split - the tail is not a separate list, and indices past
`size` are perfectly valid - so `size` has to be passed in by hand. That is exactly what the
extra `n` argument to `max_heapify` is for, and it is the one difference from `heapify` in the
`MinHeap` class, which could read `len(self.arr)` because for it the two were always equal.

Watch the boundary move on `[10, 5, 20, 2, 4, 8]`, after `build_heap` has made it
`[20, 5, 10, 2, 4, 8]`. The array stays six long throughout:

```
heap size   the heap (arr[0:size])   the sorted tail (arr[size:])
    5       [10, 5, 8, 2, 4]         [20]
    4       [8, 5, 4, 2]             [10, 20]
    3       [5, 2, 4]                [8, 10, 20]
    2       [4, 2]                   [5, 8, 10, 20]
    1       [2]                      [4, 5, 8, 10, 20]
```

Each row's tail is already the correct suffix of the sorted output; nothing later touches it.
Pass `len(arr)` where `size` belongs and `max_heapify` sees the placed maxima as ordinary heap
elements and drags them back to the front: the same six values come out as
`[8, 20, 4, 5, 10, 2]`, and the sort silently returns garbage rather than failing.

**Time complexity:** O(n log n)  
**Aux space:** O(1) (or O(log n) if we use recursion)

### Notes:

- It's not stable
- Heapsort is 2-3 times slower than quicksort because quicksort has better locality of reference than heapsort
- Used in hybrid sorting algorithms like IntroSort

**Recipe**

Max-heap versions of the same code, plus the sort they enable.

1. `max_heapify(arr, n, i)` is `heapify` with both comparisons flipped to `>` and
   one new argument: **`n`, how much of the array is still the heap.** Both bounds
   tests read `< n`, never `< len(arr)`.
2. `build_heap(arr)` runs `max_heapify(arr, n, i)` for `i` in
   `range((n - 2) // 2, -1, -1)` with `n = len(arr)` - the same bottom-up sweep as
   the constructor, and the one place where the heap really is the whole array.
3. `heap_sort`: `n = len(arr)`, `build_heap(arr)`, then for `i` in
   `range(n - 1, 0, -1)`: swap `arr[i], arr[0] = arr[0], arr[i]`, then call
   `max_heapify(arr, i, 0)`.
4. **Pass `i`, not `n`, to `max_heapify` after the swap.** `i` is the new, shorter
   heap length and it excludes the slot just filled, because the loop counts down
   from `n - 1` and the element was placed *at* `i`. Pass `n` and sifting pulls
   already-placed elements back into the heap.
5. **Swap, do not overwrite.** `extract_min` could overwrite the root from the end
   because the extracted value was returned to the caller; here the removed
   maximum has to survive in the array, at index `i`, so the two values trade
   places.
6. Stop at `i = 1`, so the range's exclusive bound is `0`. A heap of one is already
   sorted and `arr[0]` is the minimum, which is where it belongs.
7. Ascending output from a **max** heap, which is the part that reads backwards.
   A min heap would place the smallest at the end and sort descending.

```python
def build_heap(arr):
    """Turn arr into a max heap in place. Time: O(n)"""
    n = len(arr)
    for i in range((n - 2) // 2, -1, -1):
        max_heapify(arr, n, i)


def max_heapify(arr, n, i):
    """Sift arr[i] down within the first n elements of arr. Time: O(log n)"""
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        max_heapify(arr, n, largest)


def heap_sort(arr):
    """Sort arr in place, ascending. Time: O(n log n), aux space: O(log n)"""
    n = len(arr)
    build_heap(arr)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # largest goes to its final position
        max_heapify(arr, i, 0)  # restore the heap over the shrinking prefix


def is_max_heap(arr, n=None):
    """True if the first n elements of arr satisfy the max heap property."""
    n = len(arr) if n is None else n
    return all(
        arr[i] >= arr[child]
        for i in range(n)
        for child in (2 * i + 1, 2 * i + 2)
        if child < n
    )


def test_build_heap():
    arr = [10, 5, 20, 2, 4, 8]
    build_heap(arr)
    assert is_max_heap(arr)
    assert arr[0] == 20  # the maximum ends up at the root
    assert sorted(arr) == [2, 4, 5, 8, 10, 20]


def test_heap_sort():
    arr = [10, 5, 20, 2, 4, 8]
    heap_sort(arr)
    assert arr == [2, 4, 5, 8, 10, 20]

    # duplicates, already sorted, reverse sorted
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    heap_sort(arr)
    assert arr == [1, 1, 2, 3, 4, 5, 5, 6, 9]

    arr = [1, 2, 3, 4]
    heap_sort(arr)
    assert arr == [1, 2, 3, 4]

    arr = [4, 3, 2, 1]
    heap_sort(arr)
    assert arr == [1, 2, 3, 4]

    # edge cases
    arr = []
    heap_sort(arr)
    assert arr == []

    arr = [1]
    heap_sort(arr)
    assert arr == [1]

    # matches sorted() on random input
    import random

    data = [random.randint(0, 100) for _ in range(50)]
    arr = list(data)
    heap_sort(arr)
    assert arr == sorted(data)


def test_heap_sort_boundary():
    # The heap shrinks while the array does not. Step the sort by hand and check
    # both regions every round: arr[0:i] is a heap, arr[i:] is already final.
    data = [10, 5, 20, 2, 4, 8]
    arr = list(data)
    n = len(arr)
    build_heap(arr)
    assert arr == [20, 5, 10, 2, 4, 8]
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        max_heapify(arr, i, 0)  # i, the heap size - not n, the array length
        assert len(arr) == n  # the array itself never shrinks
        assert is_max_heap(arr, i)  # the front i slots are still a heap
        assert arr[i:] == sorted(data)[i:]  # the tail is already the answer
    assert arr == sorted(data)


def test_heap_sort_wrong_boundary_corrupts():
    # Passing len(arr) where the heap size belongs lets max_heapify reach back
    # into the sorted tail. It does not raise; it just returns the wrong answer.
    data = [10, 5, 20, 2, 4, 8]
    arr = list(data)
    n = len(arr)
    build_heap(arr)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        max_heapify(arr, n, 0)  # the bug: n instead of i
    assert arr == [8, 20, 4, 5, 10, 2]
    assert arr != sorted(data)


test_build_heap()
test_heap_sort()
test_heap_sort_boundary()
test_heap_sort_wrong_boundary_corrupts()
```

## Python Built-in: `heapq` module

Python's `heapq` implements a **min-heap** on a regular `list`.

| Operation | Function | Time |
|-----------|----------|------|
| Push | `heapq.heappush(h, x)` | O(log n) |
| Pop min | `heapq.heappop(h)` | O(log n) |
| Peek min | `h[0]` | O(1) |
| Build heap | `heapq.heapify(h)` | O(n) |
| Push + pop | `heapq.heappushpop(h, x)` | O(log n) |
| N smallest | `heapq.nsmallest(k, iterable)` | O(n log k) |

**No built-in max-heap** - use the negation trick.

```python
import heapq

# min-heap operations
h = [10, 5, 20, 2, 4, 8]
heapq.heapify(h)           # O(n) - [2, 4, 8, 5, 10, 20]
print(h)

heapq.heappush(h, 1)       # O(log n)
print(heapq.heappop(h))    # 1 - smallest element
print(h[0])                # 2 - peek without removing

# max-heap via negation trick
nums = [3, 1, 4, 1, 5]
max_h = [-x for x in nums]
heapq.heapify(max_h)
print(-heapq.heappop(max_h))  # 5 - largest element

# k smallest / k largest
data = [10, 5, 20, 2, 4, 8]
print(heapq.nsmallest(3, data))  # [2, 4, 5]
print(heapq.nlargest(3, data))   # [20, 10, 8]
```
