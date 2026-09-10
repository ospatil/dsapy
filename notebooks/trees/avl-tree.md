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

# AVL Tree (Self-Balancing BST)

A plain [binary search tree](../trees/binary-search-tree.md) gives `O(h)` operations, but `h` can degrade to `O(n)` when keys arrive in sorted order - the tree becomes a linked list. An **AVL tree** (Adelson-Velsky and Landis, 1962) is a BST that **rebalances itself after every insert and delete** so that `h` stays `O(log n)`.

## The balance invariant

For **every** node, the heights of its left and right subtrees differ by at most 1:

```
balance_factor(node) = height(left subtree) - height(right subtree)
```

A node is *balanced* when its balance factor is `-1`, `0`, or `+1`. If an insert or delete pushes any node's balance factor to `+2` or `-2`, we restore the invariant with **rotations**.

### Why "differ by at most 1" forces `O(log n)`

The rule is local - it talks about one node at a time - so it is not obvious that it says
anything about the height of the whole tree. Turn the question around: instead of asking how
tall a tree with `n` nodes can be, ask **how few nodes a tree of height `h` can have.** If even
the skinniest legal tree needs a lot of nodes, then a tree with `n` nodes cannot be tall.

Call that minimum `N(h)`. To make a tree of height `h` as sparse as possible, give the root the
shortest legal pair of subtrees: one of height `h-1` (something has to reach the full height)
and one of height `h-2` (the smallest the rule permits alongside it). Each of those is itself as
sparse as possible, so

```
N(h) = 1 + N(h-1) + N(h-2)          N(1) = 1, N(2) = 2
```

which is the Fibonacci recurrence wearing a different hat - in fact `N(h) = F(h+2) - 1`:

| h | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|----|
| N(h) | 1 | 2 | 4 | 7 | 12 | 20 | 33 | 54 | 88 | 143 |

The point is the *rate*: each row is roughly 1.6 times the one before it, because Fibonacci
numbers grow like $\varphi^h$ where $\varphi \approx 1.618$. So the minimum node count grows
exponentially in the height, and reading that backwards, the height can only grow
logarithmically in the node count:

$$h \leqslant \log_{\varphi}(n+1) \approx 1.44 \log_2 (n+1)$$

An AVL tree is therefore never worse than about 44% taller than a perfectly balanced one. That
is the whole promise: `O(h)` becomes `O(log n)` not by keeping the tree perfect, but by making
lopsidedness expensive in nodes.

**What the "1" is load-bearing for.** Allow a difference of 2 and the recurrence becomes
`N(h) = 1 + N(h-1) + N(h-3)`, which grows more slowly, so the same node count permits a taller
tree - still logarithmic, but with a worse constant. Allow *any* difference and there is no
recurrence left: `N(h) = h` is legal, a chain, and the height is `O(n)`. The bound comes from
the number being finite, and the constant comes from it being small.

| Operation | Time | Aux space |
|-----------|------|-----------|
| Search | `O(log n)` | `O(log n)` recursion / `O(1)` iterative |
| Insert | `O(log n)` | `O(log n)` |
| Delete | `O(log n)` | `O(log n)` |

Search is identical to a normal BST (the ordering invariant is unchanged), so this notebook focuses on **height tracking, rotations, and rebalancing**.

> **Mental model.** A BST's `O(h)` is only useful while `h` stays small, and nothing in a plain
> BST enforces that. AVL adds exactly one rule - no node's two sides may differ in height by
> more than 1 - and rotations are how that rule is restored after an insert or delete.
> Everything else behaves like an ordinary BST, because a rotation never changes the ordering.
>
> **Load-bearing:** heights are *cached* on the node, so any change of shape must recompute
> them from the bottom up. Skip that and every balance factor above the change is reading a
> stale number. And **on an insert** - only on an insert - fixing the *lowest* unbalanced
> node is enough: that rotation gives the subtree back the height it had before, so nothing
> further up ever sees a difference. Delete gets no such guarantee. Its rotation can leave
> the subtree a level shorter, and a shorter child is exactly what unbalances a parent, so a
> delete may have to rebalance again at every level up to the root.

That last clause is the single place insert and delete part company, and it is the one thing
here worth chasing down rather than taking on trust:
[Why delete is not just insert with a different first half](#why-delete-is-not-just-insert-with-a-different-first-half)
works through which fixes shorten a subtree and which do not.


### Height bookkeeping

Every node **stores** its height rather than computing it on demand. That is what keeps
rebalancing cheap: a balance factor is then two O(1) lookups instead of two subtree walks,
which would make every check O(n).

The cost of caching is that the cache must be maintained - `update_height` has to be called
after *any* structural change, and always bottom-up, since a parent's height is defined in
terms of its children's.

Conventions used here, all three fixed once and relied on everywhere below:

- **Heights count nodes, not edges.** `height(None) = 0` and a leaf has height 1, matching
  `height` in the [binary tree notebook](binary-tree.md). The other convention in circulation
  counts edges, putting a leaf at 0 and an empty tree at -1; every stored number here is one
  larger than its edge-counting twin. The [heap notebook](heap.md) uses that other one, and says
  so, because its cost analysis needs leaves to cost nothing.
- `balance_factor = height(left) - height(right)`, so **positive means left-heavy**.
- `balance_factor(None) = 0` - a missing subtree is perfectly balanced, which keeps the
  callers free of null checks.

Which convention you pick does not affect a single rotation decision, because a balance factor
is a *difference* of two heights and the `+1` cancels. It does affect every number you can
assert on: with nodes counted, three nodes balanced give `root.height == 2`, and the tests below
are written against that.

**Time:** O(1) for all three helpers

**Recipe**

1. A `Node` is the BST node plus a stored **`height`**, starting at `1` for a new
   leaf.
2. `height(node)` is a free function returning `0` for `None`. **Wrap it; never
   read `node.height` directly**, since half the calls are on children that may
   not exist.
3. `update_height(node)` is `1 + max(height(left), height(right))`, read from the
   children's stored values rather than recomputing them.
4. `balance_factor(node)` is `height(left) - height(right)`, and `0` for `None`.
   **Fix that direction once and never flip it** - one reversed subtraction sends
   every rotation case to the opposite fix.

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1  # height of a new leaf is 1

def height(node):
    """Height of None is 0; height is stored on the node and kept up to date."""
    return node.height if node else 0

def update_height(node):
    """Recompute a node's height from its children. Call after any structural change."""
    node.height = 1 + max(height(node.left), height(node.right))

def balance_factor(node):
    """left height - right height. Positive => left heavy, negative => right heavy."""
    if node is None:
        return 0
    return height(node.left) - height(node.right)
```

## Rotations

Rotations are usually presented as a pair of pointer recipes to memorise. They are not: the
two constraints already on the table leave exactly one legal move, so the recipe can be
*derived* on the spot, which is the only way to still have it months later.

**Constraint one: the inorder sequence may not change.** A BST is exactly a tree whose inorder
walk is sorted, so whatever we do to the shape, reading the subtree left to right must produce
the same list afterwards. That single sentence is the whole ordering invariant, in the form
that is useful here.

**Constraint two: something has to come up.** A node `y` is left-heavy by 2, so its left side
must lose a level and its right side must gain one. The only way to shorten the left side is to
promote a node out of it.

Now ask which node can be promoted. Write the subtree's inorder sequence, naming `y`'s left
child `x` and the three subtrees hanging off the pair:

```
T1  x  T2  y  T3
```

The node that ends up on top is the root of the subtree, so everything before it in the
sequence goes in its left subtree and everything after it goes in its right.

There are only two nodes to choose from. A rotation is `O(1)`, so it may not reach inside a
subtree and reshuffle it - `T1`, `T2` and `T3` move as sealed blocks, and the only nodes it can
actually reposition are the two it names, `x` and `y`. `y` is where we started. **So `x` goes on
top**, and once it does the rest is forced by the sequence, with no choices left to get wrong:

- everything after `x` in the list - `T2`, `y`, `T3` - must be in `x`'s right subtree, so `y`
  goes there;
- inside that, `T2` comes before `y`, so `T2` becomes `y`'s **left** child;
- `T1` and `T3` never move, because nothing about their position in the list changed.

So `T2` is the only subtree that changes parent, and that is not a fact to remember but the
only remaining option. Reading `T1 < x < T2 < y < T3` off the result confirms it: the sequence
is identical, so the tree is still a BST. The near-miss arrangements all fail that same test -
hang `T2` off `x` instead and `T2` ends up before `x` in the list; put `y` on the *left* of `x`
and `y` ends up before `T2`. Neither is sorted any more.

And it does fix the balance, which is the other thing to check: `x`'s left side kept `T1` while
its right side gained everything else, so the level the left side was too tall by is exactly the
level that moved across.

That is one rotation. It is `O(1)` - three pointer writes and two height updates, no matter how
big the subtree - and there are exactly two of them, left and right, because "left-heavy" and
"right-heavy" are mirror images and so are their fixes.

### Right rotation (fixes a left-heavy node)

![Right rotation](images/avl-rotations-single.png)

`x` moves up, `y` becomes its right child, and `x`'s old right subtree `T2` is reattached as `y`'s left child. `T2` is the only subtree that changes parent, and that is the whole operation. Ordering is preserved: `T1 < x < T2 < y < T3` before and after.

### Left rotation (fixes a right-heavy node)

```
    x                  y
   / \                / \
  T1  y     --->     x   T3
     / \            / \
    T2  T3         T1  T2
```

The exact mirror. After either rotation we recompute the heights of the two nodes that moved, **bottom-up** (the lower node first).

**Recipe**

1. `rotate_right(y)`: read both temporaries **first** - `x = y.left`, then
   `t2 = x.right`. **`x.right` is about to be overwritten**, so a rewire before
   the read loses `T2` and silently drops a whole subtree.
2. Rewire, two writes: `x.right = y`, then `y.left = t2`. Order between these two
   does not matter now that `t2` is saved; the reads in step 1 are what had to
   come first.
3. **Update heights `y` first, then `x`.** `y` is now the lower node and `x`'s new
   height is `1 + max(height(x.left), height(y))`, so updating `x` first reads a
   stale `y` and leaves `x` one too tall - a wrong number that no assert on
   ordering can see.
4. Return `x`, the new subtree root. `y` is no longer the top of anything, so
   returning it, or returning nothing, detaches the rotated subtree from its
   parent.
5. `rotate_left` is the mirror image: swap every `left` for `right`, so `y = x.right`,
   `t2 = y.left`, `y.left = x`, `x.right = t2`, update `x` then `y`, return `y`.
   Write one and flip it rather than deriving both.

```python
def rotate_right(y):
    """
    Right-rotate around y. Returns the new subtree root (x).
    Time: O(1). Used to fix a left-heavy node.
    """
    x = y.left
    t2 = x.right
    # rotate
    x.right = y
    y.left = t2
    # update heights bottom-up: y first (now lower), then x
    update_height(y)
    update_height(x)
    return x

def rotate_left(x):
    """
    Left-rotate around x. Returns the new subtree root (y).
    Time: O(1). Used to fix a right-heavy node.
    """
    y = x.right
    t2 = y.left
    # rotate
    y.left = x
    x.right = t2
    # update heights bottom-up: x first (now lower), then y
    update_height(x)
    update_height(y)
    return y
```

## The four imbalance cases

When a node becomes unbalanced (`|balance_factor| > 1`), exactly one of four cases applies.

The two letters are **two readings of the tree, taken at the unbalanced node**: the first letter
is the side that is too tall, and the second is the way that child leans. That is literally what
the code does - one balance factor at the node, one at the heavy child - and it is the definition
to keep, because it is the only one that is true for both insert and delete.

| Case | Condition | Fix |
|------|-----------|-----|
| **Left-Left (LL)** | node is left-heavy, left child is left-heavy/balanced | `rotate_right(node)` |
| **Left-Right (LR)** | node is left-heavy, left child is right-heavy | `rotate_left(left)` then `rotate_right(node)` |
| **Right-Right (RR)** | node is right-heavy, right child is right-heavy/balanced | `rotate_left(node)` |
| **Right-Left (RL)** | node is right-heavy, right child is left-heavy | `rotate_right(right)` then `rotate_left(node)` |

### Where the names come from, and why delete keeps them

The names are usually introduced the other way round, as **the first two steps of the path from
the unbalanced node down to the newly-inserted node** - go left, then left again, and you have
LL. For insert that reading is exact and it is worth having, because it explains why there are
four and only four cases: the new node arrived in one of four grandchild positions.

It does not survive delete, and the mismatch is not cosmetic. **A delete has no newly-inserted
node to path towards, and the imbalance is usually not even on the side that changed** - deleting
from the right subtree makes a node left-heavy, so the path the name would describe leads away
from the deletion, into a subtree that nothing touched. Read the letters as "heavy side, then the
child's lean" and both operations are covered by one table; read them as a path to a new node and
half the table's uses have no such node to point at.

The `/balanced` arm in the LL and RR rows is where the difference shows up in the code:

- **After an insert, the heavy child is never balanced.** Its own balance factor is `+1` or `-1`,
  never `0`, so LL and RR are entered strictly on `+1` (and RR on `-1`). A subtree whose two
  sides are equal did not just grow, so it cannot be the one that pushed its parent to `±2`.
- **After a delete, the heavy child can be balanced**, because the imbalance was created by the
  *other* side shrinking rather than by this side growing. Nothing about this side changed at all.
  Both single rotations are legal here; the code takes the LL/RR branch because its `if` tests
  for the *opposite* lean.

So the "/balanced" is not defensive coding, and it is not reachable from `insert`. It is the
delete-only third possibility, and dropping it sends a perfectly ordinary delete into a double
rotation that then leaves the node unbalanced the other way.

### What a fix does to the subtree's height

Worth separating from the ordering argument, because this is what decides whether the work is
finished. Compare the rotated subtree against the height it had **before** the operation that
disturbed it:

| Situation | Height after the fix | Consequence |
|---|---|---|
| Insert, any case | same as before the insert | no ancestor sees a change, so one fix per insert is always enough |
| Delete, heavy child balanced (`bf == 0`) | same as before the delete | the unwind can stop caring; no ancestor is affected |
| Delete, heavy child leans either way (`bf == ±1`) | **one less** than before the delete | the parent now has a shorter child and may itself go to `±2` |

That last row is the whole reason delete is not just insert with a different first half. Its cost
is spelled out in the [Delete](#delete) section.

### Double rotations

The LR and RL cases are "double rotations": a first rotation on the child reduces them to the LL/RR case, which the second rotation then fixes.

![Left-Right double rotation](images/avl-rotations-double.png)

Why one rotation cannot do it: the node that has to end up on top is `y`, the *grandchild*, and a single rotation around `z` can only lift `z`'s own child. Rotating `z` alone would move the imbalance to the other side rather than remove it. The first rotation exists purely to make `y` a child of `z`, and then the familiar single rotation applies.

`T1 < T2 < T3 < T4` left to right in all three states, which is why neither step can break the search order.

**Recipe**

1. `update_height(node)` first, then read `bf = balance_factor(node)`. **Height
   before balance factor, or the factor is computed from stale numbers.**
2. `bf > 1` is left-heavy. Read **the left child's** balance factor: `< 0` means the
   child leans right, so this is Left-Right. **Test `< 0`, not `<= 0`** - a
   balanced child belongs in the LL branch, and on delete it is a live case.
3. Left-Right: `node.left = rotate_left(node.left)`, which turns it into
   Left-Left, then `return rotate_right(node)`. **The inner rotation must be
   assigned back into `node.left`**; it returns a new child root and dropping it
   leaves `node.left` pointing at a node that is now one level down.
4. `bf < -1` mirrors it exactly: read the right child, `> 0` means Right-Left, so
   `node.right = rotate_right(node.right)`, then `return rotate_left(node)`.
5. **Two `if`s, not four branches.** The inner rotation folds LR into LL and RL
   into RR, so each outer `if` ends with the single rotation it now shares.
6. Otherwise return `node` untouched - and return it, rather than falling off the
   end, because every caller assigns the result back and `None` would delete the
   subtree.
7. **A balance factor never exceeds 2 in magnitude here**, because the tree was
   valid before the single insert or delete that disturbed it. If you ever see
   `±3`, the bug is a missing `update_height` or a dropped return, not a missing
   case.

```python
def rebalance(node):
    """
    Restore the AVL invariant at `node` after a child changed.
    Updates height, then applies the LL / LR / RR / RL fix if needed.
    Returns the (possibly new) subtree root. Time: O(1).
    """
    update_height(node)
    bf = balance_factor(node)

    # Left heavy (bf == +2). The left child's bf is +1 after an insert, and may
    # additionally be 0 after a delete; both take the single rotation.
    if bf > 1:
        if balance_factor(node.left) < 0:     # Left-Right: reduce to Left-Left
            node.left = rotate_left(node.left)
        return rotate_right(node)             # Left-Left

    # Right heavy (bf == -2), the mirror image.
    if bf < -1:
        if balance_factor(node.right) > 0:    # Right-Left: reduce to Right-Right
            node.right = rotate_right(node.right)
        return rotate_left(node)              # Right-Right

    return node  # already balanced
```

## Insert

Identical to BST insertion, with one addition: as the recursion **unwinds**, every ancestor
of the inserted node calls `rebalance`.

That ordering is the whole trick. The recursive call returns before `rebalance(root)` runs,
so nodes are checked bottom-up - heights below are already correct by the time a node looks
at its own balance factor. A single insert can unbalance several ancestors, but fixing the
lowest one restores the subtree's original height, which leaves everything above it balanced
too. One rotation (single or double) per insert is always enough.

```
insert 10, 20, 30 into an empty tree

after 10        10                    balanced
after 20        10                    bf(10) = 0 - 1 = -1, still fine
                  \
                   20
after 30        10                    bf(10) = 0 - 2 = -2 → right heavy,
                  \                   right child is right heavy → RR case
                   20
                     \                rotate_left(10):
                      30
                                          20
                                         /  \
                                       10    30      height 2, balanced
```

### The plumbing: return the root, assign it back

Everything in this notebook that can change a subtree's shape - `rotate_left`, `rotate_right`,
`rebalance`, `insert`, `delete` - **takes a subtree root and returns the subtree root**, which
may or may not be the same node. That one convention is what lets the whole family work without
parent pointers. A rotation replaces the top node of a subtree, and the only thing holding a
pointer to that top node is its parent, one frame up the recursion. So the parent has to be the
one to write it:

```
root.left = insert(root.left, data)     # not: insert(root.left, data)
```

Three ways this goes wrong, and none of them raise:

- **Dropping the assignment on the recursive call.** The child subtree is still updated in place
  for an ordinary insert, so tests keep passing - until a rotation happens at that child and its
  new root is thrown away, leaving `root.left` pointing at a node that is now one level down.
- **Dropping the assignment on the inner rotation of a double.** Same shape, one level lower:
  `node.left = rotate_left(node.left)` inside `rebalance`.
- **Returning `root` instead of `rebalance(root)`.** Heights stop being updated too, since
  `update_height` lives inside `rebalance`, so every balance factor above the change reads stale
  numbers and the tree quietly stops being AVL.

The caller at the very top is subject to the same rule - `root = insert(root, v)` - because the
root itself is what a rotation at the root replaces.

**Time:** O(log n) &nbsp; **Space:** O(log n) recursion stack

**Recipe**

1. An ordinary BST insert: `None` returns `Node(data)`, an equal key returns
   `root` unchanged, otherwise recurse into one side and **assign the result
   back**: `root.left = insert(root.left, data)`.
2. Then `return rebalance(root)` in place of `return root`. That single
   substitution is the entire diff from the BST version.
3. **The duplicate branch returns early, before `rebalance`.** Nothing changed, so
   there is nothing to fix - and no new node was created, which is why an insert
   of an existing key cannot rotate.

```python
def insert(root, data):
    """
    Insert into the AVL tree, rebalancing on the way up.
    Time: O(log n). Aux space: O(log n) recursion stack.
    """
    # 1. standard BST insert
    if root is None:
        return Node(data)
    if data < root.data:
        root.left = insert(root.left, data)
    elif data > root.data:
        root.right = insert(root.right, data)
    else:
        return root  # duplicates not allowed

    # 2. rebalance this ancestor
    return rebalance(root)

def inorder(root, acc):
    if root:
        inorder(root.left, acc)
        acc.append(root.data)
        inorder(root.right, acc)
```

```python
def test_rotation_ll():
    # 30, 20, 10 arrive sorted-descending -> would skew left.
    # A single right rotation at the root fixes it.
    root = None
    for v in [30, 20, 10]:
        root = insert(root, v)
    assert root.data == 20
    assert root.left.data == 10
    assert root.right.data == 30
    assert root.height == 2

test_rotation_ll()
```

```python
def test_rotation_rr():
    # 10, 20, 30 ascending -> right-skewed -> single left rotation.
    root = None
    for v in [10, 20, 30]:
        root = insert(root, v)
    assert root.data == 20
    assert root.left.data == 10
    assert root.right.data == 30

test_rotation_rr()
```

```python
def test_rotation_lr():
    # 30, 10, 20 -> Left-Right: rotate_left(left) then rotate_right(root).
    root = None
    for v in [30, 10, 20]:
        root = insert(root, v)
    assert root.data == 20
    assert root.left.data == 10
    assert root.right.data == 30

test_rotation_lr()
```

```python
def test_rotation_rl():
    # 10, 30, 20 -> Right-Left: rotate_right(right) then rotate_left(root).
    root = None
    for v in [10, 30, 20]:
        root = insert(root, v)
    assert root.data == 20
    assert root.left.data == 10
    assert root.right.data == 30

test_rotation_rl()
```

## Checking the invariant

Two helpers, because the two things that can silently go wrong are different. `is_avl_balanced`
recursively verifies every node satisfies `|balance_factor| <= 1`. `heights_consistent`
recomputes every stored height from its children and compares - that is the check for the failure
mode the notebook keeps warning about, since a stale cached height produces a tree that is
*genuinely* balanced and still reports the wrong balance factors, and no ordering or balance
assert can see it.

**Recipe**

1. Empty subtree is balanced, and vacuously consistent.
2. `is_avl_balanced`: if `abs(balance_factor(node)) > 1`, return `False`;
   otherwise recurse into both children and require both.
3. `heights_consistent`: require `node.height == 1 + max(height(left),
   height(right))`, then recurse into both children. **Recompute from the
   children's stored values, not by re-walking the subtree** - re-walking would
   pass even when every stored number is wrong.
4. **Check every node, not just the root.** A root with equal-height subtrees can
   sit above a badly skewed one, so a root-only check passes trees that are not
   AVL.
5. Pair both with the inorder-is-sorted check. The three cover ordering, balance
   and the cache, and a given rotation bug usually breaks exactly one of them:
   a swapped rewire breaks ordering, a wrong case choice breaks balance, and an
   `update_height` in the wrong order breaks only the cache.

```python
def is_avl_balanced(node):
    """True if every node in the subtree has balance factor in {-1, 0, 1}."""
    if node is None:
        return True
    if abs(balance_factor(node)) > 1:
        return False
    return is_avl_balanced(node.left) and is_avl_balanced(node.right)

def heights_consistent(node):
    """True if every stored height agrees with its children's stored heights."""
    if node is None:
        return True
    if node.height != 1 + max(height(node.left), height(node.right)):
        return False
    return heights_consistent(node.left) and heights_consistent(node.right)

def test_stays_balanced():
    root = None
    for v in [10, 20, 30, 40, 50, 25]:
        root = insert(root, v)
    res = []
    inorder(root, res)
    assert res == [10, 20, 25, 30, 40, 50]  # still a valid BST
    assert is_avl_balanced(root)
    assert heights_consistent(root)
    assert root.height == 3  # 6 nodes balanced; a plain BST here would be height 5

test_stays_balanced()
```

```python
def test_sequential_inserts_stay_log_height():
    # The pathological case for a plain BST: 1..63 in ascending order
    # would build a height-63 linked list. AVL keeps it logarithmic.
    root = None
    for v in range(1, 64):
        root = insert(root, v)
    assert is_avl_balanced(root)
    assert heights_consistent(root)  # no stale cached heights on the way up
    assert root.height == 6  # 63 nodes -> perfectly balanced height
    res = []
    inorder(root, res)
    assert res == list(range(1, 64))

test_sequential_inserts_stay_log_height()
```

## Delete

Like BST delete (three cases: leaf, one child, two children - replacing with the inorder
successor), but every ancestor calls `rebalance` as the recursion unwinds.

### Why delete is not just insert with a different first half

Insert's argument for stopping after one fix was that the rotation gives the subtree back the
height it had before, so no ancestor ever notices. **Delete breaks that premise.** Two of the
three fix situations in the [height table](#what-a-fix-does-to-the-subtrees-height) leave the
subtree one level shorter than it was, and a shorter subtree is exactly what unbalances a parent.
So the fix can be needed again one level up, and again above that.

The result is the same asymptotics by a different route: insert does at most **one** rotation and
`O(log n)` height updates; delete does up to **`O(log n)`** rotations, each `O(1)`, on the same
unwind. Nothing in the code says which - `delete` calls `rebalance` at every level exactly as
`insert` does, and the difference is entirely in how often `rebalance` finds something to do.

It takes a surprisingly large tree to see it. Rotating at two levels needs two nodes on the path
that are *both* one delete away from `±2`, and the smallest AVL tree with room for that has **12
nodes** - `N(5)` from the table at the top of this notebook, the sparsest legal tree of height 5.
Below 12 nodes, every single delete rotates at most once. The test below builds that 12-node tree
and pins the two-level case, because a smaller example cannot exist.

### The deletion cases, in the vocabulary of the case table

The four-case table applies unchanged, and this is where reading its letters as "heavy side, then
the child's lean" pays off: on delete the heavy side is the side that **did not** change. Delete a
key from the right subtree and the *left* subtree becomes the tall one, so an LL or LR fix is what
a right-side deletion calls for. Naming the cases after a path towards the changed node would
point in the wrong direction here.

The two-children case does not delete the node at all - it **overwrites `root.data` with the
successor's** and then deletes the successor from the right subtree. So the structural deletion
always happens at a node with at most one child, always down in the right subtree, and the
`rebalance` calls on the way back up from *that* recursion are what keep the right subtree legal
before this node's own `rebalance` ever runs.

**Time:** O(log n) &nbsp; **Space:** O(log n) recursion stack

**Recipe**

1. `min_node` walks `left` to the end and returns the node. A `while`, not
   recursion - there is no unwinding to do.
2. `delete` is the BST delete verbatim, with the same **assign the result back**
   protocol as `insert`: `root.left = delete(root.left, data)`.
3. Empty subtree returns `None`, which is both the not-found answer and the
   correct new child for a parent that just lost a leaf.
4. Zero or one child: `return root.right` if there is no left, else
   `return root.left` if there is no right. One test covers the leaf case too,
   since both sides are `None` and returning either returns `None`.
5. Two children: `succ = min_node(root.right)`, copy `root.data = succ.data`,
   then `root.right = delete(root.right, succ.data)`. **Recurse on
   `root.right`, not on the whole tree**, and **delete `succ.data`, not the
   original key** - the original key no longer exists anywhere by this point.
6. Then `return rebalance(root)` in place of `return root`, exactly as `insert`
   did.
7. **The early `return root.right` and `return root.left` deliberately skip
   `rebalance`.** They return a *child*, not this node, and that child was already
   a valid AVL subtree; the parent's own `rebalance` on the way up absorbs the
   height change.
8. **Do not stop after the first fix.** The unwind has to run all the way to the
   root, because delete's rotations can shorten a subtree and cascade. A `break`
   or an early return here is the classic delete bug, and it survives every test
   built on fewer than 12 nodes.

```python
def min_node(node):
    """Leftmost (smallest) node in a subtree."""
    while node.left is not None:
        node = node.left
    return node

def delete(root, data):
    """
    Delete from the AVL tree, rebalancing on the way up.
    Time: O(log n). Aux space: O(log n).
    """
    if root is None:
        return None

    # 1. standard BST delete
    if data < root.data:
        root.left = delete(root.left, data)
    elif data > root.data:
        root.right = delete(root.right, data)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        # two children: replace with inorder successor, then delete it
        succ = min_node(root.right)
        root.data = succ.data
        root.right = delete(root.right, succ.data)

    # 2. rebalance this ancestor
    return rebalance(root)

def test_delete_rebalances():
    # Insertion leaves 3 balanced; deleting 4 makes it left-heavy and forces
    # a right rotation. Checking the shape proves delete actually rebalanced.
    rotating = None
    for v in [3, 2, 4, 1]:
        rotating = insert(rotating, v)
    assert rotating.data == 3

    rotating = delete(rotating, 4)
    assert rotating.data == 2
    assert rotating.left.data == 1
    assert rotating.right.data == 3
    assert rotating.height == 2
    assert is_avl_balanced(rotating)
    assert heights_consistent(rotating)

    root = None
    for v in [10, 20, 30, 40, 50, 25]:
        root = insert(root, v)
    root = delete(root, 10)
    res = []
    inorder(root, res)
    assert res == [20, 25, 30, 40, 50]
    assert is_avl_balanced(root)
    assert heights_consistent(root)

    root = delete(root, 40)
    res = []
    inorder(root, res)
    assert res == [20, 25, 30, 50]
    assert is_avl_balanced(root)
    assert heights_consistent(root)

test_delete_rebalances()
```

The height table above claims delete's two situations behave differently, and the difference is
observable in a five-node tree, so it is worth pinning rather than asserting in prose. Both trees
below are height 3 and both go left-heavy when `75` is deleted; only the lean of the left child
differs.

```python
def test_delete_height_depends_on_the_childs_lean():
    # Left child BALANCED (bf == 0) - reachable only from delete.
    # The single rotation gives the subtree back its pre-delete height,
    # so an ancestor would see no change and the unwind could stop.
    root = None
    for v in [50, 25, 75, 10, 30]:
        root = insert(root, v)
    assert root.height == 3
    assert balance_factor(root.left) == 0
    root = delete(root, 75)
    assert root.data == 25          # rotated
    assert root.height == 3         # ...but no shorter than before
    assert is_avl_balanced(root) and heights_consistent(root)

    # Left child LEANS LEFT (bf == +1) - the insert-style LL shape.
    # The same single rotation leaves the subtree one level SHORTER,
    # which is what lets a delete cascade into an ancestor.
    root = None
    for v in [50, 25, 75, 10]:
        root = insert(root, v)
    assert root.height == 3
    assert balance_factor(root.left) == 1
    root = delete(root, 75)
    assert root.data == 25
    assert root.height == 2         # one shorter than before the delete
    assert is_avl_balanced(root) and heights_consistent(root)

test_delete_height_depends_on_the_childs_lean()
```

And the cascade itself. Twelve nodes is the smallest tree in which one delete rotates at two
levels, so this is the minimum-size witness rather than a large arbitrary example. Inserting in
level order reproduces the sparsest legal tree of height 5 exactly, with no rotations along the
way.

```python
def test_delete_cascades_at_two_levels():
    # N(5) = 12 nodes: the sparsest AVL tree of height 5.
    root = None
    for v in [8, 5, 11, 3, 7, 9, 12, 2, 4, 6, 10, 1]:
        root = insert(root, v)
    assert root.data == 8
    assert root.height == 5
    assert height(root.left) == 4 and height(root.right) == 3

    root = delete(root, 12)

    # Two separate rotations, both visible in the shape:
    # the lower one replaced 11 with 10 as that subtree's root...
    assert root.right.right.data == 10
    assert root.right.right.left.data == 9
    assert root.right.right.right.data == 11
    # ...and shortening that side pushed the root itself over, so 8 moved down.
    assert root.data == 5
    assert root.right.data == 8
    assert root.height == 4

    res = []
    inorder(root, res)
    assert res == list(range(1, 12))
    assert is_avl_balanced(root)
    assert heights_consistent(root)

test_delete_cascades_at_two_levels()
```

## Python Built-in Note

Python has **no built-in balanced BST**. The standard-library `bisect` module keeps a plain list sorted with `O(log n)` *search* but `O(n)` *insert/delete* (array shifting) - see the [binary-search](../searching/binary-search.md) and [BST](../trees/binary-search-tree.md) notebooks.

For true `O(log n)` ordered operations, the de-facto choice is the third-party **`sortedcontainers.SortedList`** (pure Python, but uses a list-of-lists with large fan-out that beats a textbook AVL in practice due to cache locality):

| Operation | `SortedList` |
|-----------|--------------|
| `add(x)` | `O(log n)` amortized |
| `remove(x)` | `O(log n)` amortized |
| `sl[i]` (index) | `O(log n)` |
| `bisect_left/right` | `O(log n)` |

**Why implement AVL by hand then?** To understand *how* a self-balancing tree maintains its invariant - rotations and balance factors are the foundation for red-black trees (used inside many language runtimes' ordered maps), B-trees (databases and filesystems), and interval trees.
