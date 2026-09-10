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

<!-- #region -->
# Binary search tree

* For every node, **every** key in its whole left subtree is smaller and **every** key
  in its whole right subtree is greater - not just the two children.
* All data is distinct.
```sh
      50
     /  \
    30  70
   / \   / \
  10 40 60 80
```
* Time complexity of search in BST: `O(h)` where `h` is the height of tree.
* Inorder traversal of BST always results in sorted data.
* Smallest data is always leftmost leaf and largest the rightmost leaf.
* If keys are in sorted increasing order BST turns into a linked list. Ex: `5, 10, 20, 30` (right-skewed)<br>
* If keys are sorted in decreasing order the tree turns into left-skewed tree.

```sh
    5
     \
     10
      \
      20
       \
       40
```

Ideally, we want balanced BST that allow all operations in `O(log n)` time. Examples - AVL tree, Red-black tree. See the [AVL tree notebook](avl-tree.md) for a self-balancing BST with rotations.

> **Mental model.** Every key has exactly one legal place in the tree, and a single
> comparison tells you which way that place lies. So every function below is the same
> descent: compare with the node you are standing on, commit to one side, and throw the
> other side away forever. What they *do* with that descent is where they part company.
> Search and insert act only where it ends. Delete acts there too, then reattaches
> subtrees on the way back up. Floor and ceil are the ones to watch: they bank a
> candidate answer **while descending**, because a key that is merely allowed can still
> be beaten further down, and the last one banked is the answer.
>
> **Load-bearing:** the ordering rule covers whole subtrees, not just a node's two
> children - that is what the word *invariant* is doing here. Weaken it to "the left
> child is smaller" and discarding a side stops being safe, because the key you want
> could be sitting anywhere in the half you just dropped. The invariant also sets the
> price: the work is one root-to-leaf path, so a skewed tree costs O(n) and every
> operation degrades together.
<!-- #endregion -->

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def create_test_bst():
        """
              10
             /  \
            5   30
           /    / \
          2    25 40
        """
        root = Node(10)
        root.left = Node(5)
        root.left.left = Node(2)
        root.right = Node(30)
        root.right.left = Node(25)
        root.right.right = Node(40)

        return root
```

## Inorder traversal

Identical to the plain binary tree version, but on a BST it stops being one way of
listing the keys and becomes a proof. Inorder emits the whole left subtree, then
the node, then the whole right subtree, so a sorted output asserts the ordering
rule at every node at once: everything to my left is below me, everything to my
right is above me. The check is therefore **complete**, not merely suggestive - a
tree whose inorder is strictly increasing is a BST, and any violation surfaces as
one adjacent pair in the wrong order.

The visit has to sit *between* the two calls. Move `acc.append(root.data)` above
the left call and you get preorder: `[10, 5, 2, 30, 25, 40]` instead of
`[2, 5, 10, 25, 30, 40]`. The same six keys either way, so only an order-sensitive
assert notices.

**Time:** Θ(n) &nbsp; **Space:** Θ(h)

```python
def inorder(root, acc):
    if root:
        inorder(root.left, acc)
        acc.append(root.data)
        inorder(root.right, acc)

def test_inorder():
        root = create_test_bst()
        res = []
        inorder(root, res)
        assert res == [2, 5, 10, 25, 30, 40]
        empty = []
        inorder(None, empty)
        assert empty == []

test_inorder()

```

## Search

The whole point of a BST: one comparison discards an entire subtree, unexamined.
Node bigger than the target → the answer can only be to the left; smaller → only to
the right.

Dropping that side is the irreversible move, and it is safe only because the
invariant covers whole subtrees. If the node holds 50 and you want 30, nothing
anywhere under its right child is below 50 - not one level down, not ten - so 30
cannot be hiding there. A rule about immediate children would not license that.

Binary search with pointers instead of indices, so the cost is the length of one
root-to-leaf path rather than the node count.

**Time:** O(h) - O(log n) balanced, O(n) if the tree has degenerated into a list
&nbsp; **Space:** O(h)

**Recipe**

1. Two base cases: `root is None` returns `False`, a match returns `True`.
   Everything else is one comparison and one call whose value is returned
   directly - no work on the way back up, which is what the next section exploits.
2. **One recursive call, not two.** The binary tree's `search` needed
   `search(left) or search(right)`, and writing that here returns *the same answer
   on every input* - it just quietly costs O(n) instead of O(h), so no assert can
   tell the two apart.

```python
def search(root, data):
    """
    Time complexity: O(h) where h is height of BST
    Aux space: O(h)
    """
    if root is None:
        return False
    if root.data == data:
        return True
    if root.data > data:
        return search(root.left, data)
    return search(root.right, data)

def test_search():
    root = create_test_bst()
    assert search(root, 30)
    assert not (search(root, 50))
    assert not search(None, 1)  # empty tree, the recursive base case

test_search()
```

## Search, iteratively

The recursion is tail-recursive - nothing happens after the recursive call - so it
collapses into a `while` loop that reassigns `root`. From here on, `root` stops
meaning "the tree's root" and starts meaning "wherever the walk currently
stands", overwritten one step at a time. Identical comparisons and identical
path, but O(1) space instead of a frame per level.

This is the form to prefer in practice; the recursive one just reads better as an
explanation.

**Time:** O(h) &nbsp; **Space:** O(1)

**Recipe**

1. Reassign `root` itself as the cursor - no second variable. A failed search has
   nothing to attach and nothing to unlink, so it never needs to know what it
   stood on one step back.
2. **Return `False` after the loop, not from inside it.** Falling out of the bottom
   is the only thing that means "absent"; an `else: return False` in the loop body
   answers after a single comparison.

```python
def search_iter(root, data):
    """
    Time complexity: O(h) where h is height of BST
    Aux space: O(1)
    """
    while root is not None:
        if root.data == data:
            return True
        elif root.data > data:
            root = root.left
        else:
            root = root.right
    return False

def test_search_iter():
    root = create_test_bst()
    assert search_iter(root, 25)
    assert not (search_iter(root, 50))
    assert not search_iter(None, 1)  # loop never runs

test_search_iter()
```

## Insert

Walk exactly as `search` would. Where the search *would have failed* is precisely
where the key belongs - that empty slot is the only place consistent with every
comparison above it - so an insert always adds a **leaf** and never rearranges an
existing node.

That slot is `None`, and `None` cannot be written to: it has no fields and no
address. So the new node cannot be attached from below. Each call hands its own
subtree root back to its caller instead, and the caller stores it in the slot it
owns. Only one store in the whole descent is a real relink; at every node above
the insertion point the child stores itself back, so nothing moves.

An equal key returns the existing node untouched, so the tree behaves as a set.

**Time:** O(h) &nbsp; **Space:** O(h)

**Recipe**

1. Empty subtree: **return `Node(data)`**. That return value is the only thing
   carrying the new node up to whoever owns the slot.
2. Duplicate: `return root` before recursing.
3. Otherwise recurse into the correct side and **assign the result back**:
   `root.left = insert(root.left, data)`.
4. **The trap: calling `insert(root.left, data)` and dropping the assignment.** It
   builds the node, walks to the correct slot, links nothing, and raises no
   exception - the tree comes back exactly as it was.
5. `return root` at the end, so the caller one level up has something to store.

```python
def insert(root, data):
    """
    Time complexity: O(h) where h is height of BST
    Aux space: O(h)
    Insertion always happens at leaf level for non-empty BST.
    """
    if root is None:
        return Node(data)
    if root.data == data:
        return root
    if root.data > data:
        root.left = insert(root.left, data)
    else:
        root.right = insert(root.right, data)
    return root

def test_insert():
    root = insert(None, 40)
    root = insert(root, 20)
    root = insert(root, 30)
    root = insert(root, 100)
    root = insert(root, 70)
    root = insert(root, 60)
    root = insert(root, 200)
    res = []
    inorder(root, res)
    assert res == [20, 30, 40, 60, 70, 100, 200]
    # duplicate is a no-op: same tree, and the existing node comes back
    assert insert(root, 30) is root
    res = []
    inorder(root, res)
    assert res == [20, 30, 40, 60, 70, 100, 200]

test_insert()
```

## Insert, iteratively

Every node in a BST splits its subtree into two ranges: everything smaller
goes left, everything larger goes right. Placing a new value means walking
down through those splits until it lands in the one gap consistent with every
split above it, then attaching it there.

That gap is `None`, and `None` cannot hold its own address. So the loop
tracks two pointers: `curr`, where the descent currently stands, and
`parent`, the last real node it stood on, one step behind. `parent` is
updated before `curr` moves, since it's the only real node left to remember
which slot it owns once `curr` walks into `None`.

`parent is None` after the loop means the loop never ran - the tree was
empty. No node owns a slot to attach to, so the new node becomes the root
itself.

**Time:** O(h) &nbsp; **Space:** O(1)

**Recipe**

1. Build the node first. Then walk down, setting `parent = curr` **before** `curr`
   advances into `.left` or `.right`. **Set it after the move and `parent` is only
   another name for `curr`**: it is `None` when the loop exits, so step 3 fires
   every time and each call returns its own node alone - feeding in 40, 20, 30
   leaves a one-node tree holding 30.
2. Duplicate: `return root` from inside the loop.
3. The loop ends with `curr` on `None`, which owns no slot. **`parent is None`
   means the loop never ran**, so return `new` as the whole tree.
4. Otherwise compare `data` against `parent.data` once more to pick `.left` or
   `.right`, and attach `new` there. It has to go through `parent`: `curr` is
   `None` here and has no field to set.
5. Return `root`, never `new`. Step 3 is the only case where the root changes.

```python
def insert_iter(root, data):
    """
    Time complexity: O(h) where h is height of BST
    Aux space: O(1)
    """
    new = Node(data)
    parent, curr = None, root
    # traverse to find the parent for the new node
    while curr is not None:
        parent = curr
        if curr.data == data:
            return root
        elif curr.data > data:
            curr = curr.left
        else:
            curr = curr.right
    if parent is None:
        return new
    if parent.data > data:
        parent.left = new
    else:
        parent.right = new
    return root

def test_insert_iter():
    root = insert_iter(None, 40)
    root = insert_iter(root, 20)
    root = insert_iter(root, 30)
    root = insert_iter(root, 100)
    root = insert_iter(root, 70)
    root = insert_iter(root, 60)
    root = insert_iter(root, 200)
    res = []
    inorder(root, res)
    assert res == [20, 30, 40, 60, 70, 100, 200]
    assert insert_iter(root, 30) is root  # duplicate exits inside the loop
    res = []
    inorder(root, res)
    assert res == [20, 30, 40, 60, 70, 100, 200]

test_insert_iter()
```

![BST Delete - 3 Cases](images/bst-delete.png)


## Delete

The one BST operation that has to restructure. Removing a node leaves a hole, and the
real question is not "how do I unlink this node" but "which key is allowed to stand
here instead". How hard that is depends only on how many children the node has - the
three cases in the diagram above:

1. **No child** - `root.left is None`, so `return root.right` hands the parent
   `None`, and the parent's pointer drops it.
2. **One child** - the same line, `return root.right` (or its mirror,
   `return root.left`), but now the surviving child comes back instead of
   `None`. Its whole subtree is already on the correct side of the parent, so
   it moves up unchanged.
3. **Two children** - neither line fires, so both subtrees stay and the hole
   still needs a separator between them. Walk down the right subtree to its
   leftmost node - call it `succ`, the **inorder successor** (the next key in
   sorted order) - copy its value into the hole, then delete `succ` from the
   right subtree.

Only two keys can legally sit in that slot: the biggest one on the left, or the smallest
one on the right. Any other key has something on the wrong side of it. Case 3 takes the
smallest on the right.

That choice also caps the extra work. The leftmost node of a subtree has no left child,
by definition, so removing it lands in case 1 or case 2 - the recursion cannot hit
another two-child deletion.

**The trap:** case 3 never removes the node the caller searched for. It writes
`succ.data` over `root.data` and unlinks `succ`'s node instead. Delete 10 from the
tree built by `create_test_bst` and the object that held 10 is still there, still
the root, now reporting 25 - so a reference a caller was already holding silently
means a different key than the one they looked up.

**Time:** O(h) &nbsp; **Space:** O(h)

**Recipe**

1. Empty subtree: return `None`. This is also the absent-key case - the search
   walks off the bottom and every caller assigns back what it already had.
2. Target below this node: `root.left = delete(root.left, data)`. Above it:
   the same on the right. Every call returns the new root of the subtree it
   was given, and the caller assigns it back - **that assignment is the only
   thing that unlinks a node**, nothing else touches pointers.
3. Found it, and no left child: return `root.right`. No right child: return
   `root.left`. The leaf case falls out of these two, since both are `None`.
4. Two children: walk `root.right` left as far as it goes. That is `succ`.
5. Copy `succ.data` into `root.data`, then `root.right = delete(root.right,
   succ.data)`. **Recurse into `root.right`, not `root`** - `root` now *holds*
   `succ.data`, so a search starting there matches at once, finds the same
   successor, and recurses until `RecursionError`. That call cannot re-enter step
   4, since a leftmost node has no left child.
6. Return `root`, because the caller in step 2 is waiting to assign it.

```python
def delete(root, data):
    """
    Time complexity: O(h) where h is height of BST
    Aux space: O(h)

    Three cases:
    1. Leaf node - simply remove
    2. One child - replace node with its child
    3. Two children - replace with inorder successor
       (leftmost node in right subtree), then delete successor
    """
    if root is None:
        return None
    if root.data > data:
        root.left = delete(root.left, data)
    elif root.data < data:
        root.right = delete(root.right, data)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        # find inorder successor (leftmost in right subtree)
        succ = root.right
        while succ.left is not None:
            succ = succ.left
        root.data = succ.data
        root.right = delete(root.right, succ.data)
    return root

def test_delete():
    """
           20
          /  \\
        10     30
        / \\    / \\
       5  15  25 40
    """
    root = Node(20)
    root.left = Node(10)
    root.left.left = Node(5)
    root.left.right = Node(15)
    root.right = Node(30)
    root.right.left = Node(25)
    root.right.right = Node(40)

    # delete leaf node (5)
    root = delete(root, 5)
    res = []
    inorder(root, res)
    assert res == [10, 15, 20, 25, 30, 40]

    # delete node with one child (10)
    root = delete(root, 10)
    res = []
    inorder(root, res)
    assert res == [15, 20, 25, 30, 40]

    # delete node with two children (20). Case 3 rewrites the key at this very
    # node object instead of unlinking it - see the trap above.
    held = root
    root = delete(root, 20)
    res = []
    inorder(root, res)
    assert res == [15, 25, 30, 40]
    assert held is root and held.data == 25

    # absent key walks off the bottom and changes nothing
    root = delete(root, 99)
    res = []
    inorder(root, res)
    assert res == [15, 25, 30, 40]

    assert delete(None, 5) is None  # empty tree
    assert delete(Node(7), 7) is None  # last node standing

test_delete()
```

## Floor

Largest key ≤ `val`. Read it as **the closest key that does not go above `val`**.
Two tests hide in that phrase - is this key allowed at all, and could something
still beat it - and every node the walk stands on is judged on exactly those two.
The three comparison cases are the three answers.

`root.data == val`: allowed, and nothing can be closer. Return this node.

`root.data > val`: above `val`, so not allowed, and neither is anything in its
right subtree, which holds keys larger still. Only the left subtree can hold an
allowed key. Go left, and record nothing, because nothing here was allowed.

`root.data < val`: allowed. Possibly not the closest, since the right subtree holds
keys larger than this node and any of those still ≤ `val` would beat it. Possibly
the closest, since every one of them might overshoot instead. Neither can be ruled
out from here, and that is exactly what the extra variable is for: **`res` is the
answer if the search to the right turns up nothing better.** Bank this node in
`res`, then go right and try to beat it.

Going right throws the left subtree away, and it is safe for a different reason
than in `search`: those keys are all smaller than the node just banked, so they are
allowed but strictly worse. Nothing is lost. Each later bank happens inside the
previous bank's right subtree, so `res` only ever improves - `floor(26)` banks 10,
then 25.

`res` is still `None` at the end only when the walk never stepped right, meaning
every node it stood on was above `val`. Each of those steps discarded only keys
larger still, so nothing anywhere in the tree was ≤ `val` and `val` sits below the
minimum. An empty tree also returns `None`, having never entered the loop.

Too large, go left. Small enough, save it and go right.

**Time:** O(h) &nbsp; **Space:** O(1)

**Recipe**

1. `res = None`, and `res` holds a **node**, not a key - callers read `.data` off
   the return value.
2. `root` is the walking pointer, as in `search_iter`. Loop while
   `root is not None`.
3. `root.data == val`: `return root`, straight out of the loop.
4. `root.data > val`: `root = root.left`, **and no write to `res` on this branch.**
   Writing on both leaves `res` holding the last node visited, which is above `val`
   whenever the walk's final step was a left step - not only when the answer is
   `None`. On the test tree `floor(24)` returns 25 instead of 10, and `floor(1)`
   returns 2 instead of `None`.
5. `root.data < val`: `res = root` **before** `root = root.right`. `root` is the
   only handle on that node, and the step overwrites it.
6. `return res` after the loop.

```python
def floor(root, val):
    """
    Find the largest value in tree that is <= val.
    Time complexity: O(h)
    Aux space: O(1)
    """
    res = None
    while root is not None:
        if root.data == val:
            return root
        elif root.data > val:
            root = root.left
        else:
            res = root
            root = root.right
    return res

def test_floor():
    root = create_test_bst()
    assert floor(root, 6).data == 5
    assert floor(root, 10).data == 10
    assert floor(root, 26).data == 25  # banks 10, then improves to 25
    assert floor(root, 24).data == 10  # 25 is too big; the bank from 10 stands
    assert floor(root, 41).data == 40  # above every key
    assert floor(root, 1) is None  # walk never steps right
    assert floor(None, 5) is None

test_floor()
```

## Ceil

Smallest key ≥ `val`: the closest key that does not go *below* `val`. Same two
tests, with "allowed" flipped. A node is allowed when `root.data > val`, and what
could still beat it lies to its left, among keys smaller than it but possibly still
≥ `val` - so bank it and go left. A node below `val` is not allowed, and neither is
its left subtree, holding keys smaller still, so go right and record nothing.

Both functions obey one rule, which is easier to hold than two sets of comparisons:
**record on the side where the node itself is an allowed answer, then step toward
`val`.** Floor banks when the node is below `val` and steps up; ceil banks when it
is above and steps down.

Floor and ceil together answer "nearest neighbours of a key that may not be in the
tree" - the BST counterpart of `bisect_right(a, x) - 1` and `bisect_left(a, x)`.

Too small, go right. Big enough, save it and go left.

**Time:** O(h) &nbsp; **Space:** O(1)

**Recipe**

1. Same skeleton as `floor`: `res = None` holding a node, `root` as the walking
   pointer, exact match returns the node, `return res` after the loop.
2. `root.data < val`: `root = root.right`, recording nothing. Otherwise `res = root`
   **before** `root = root.left`.
3. **Bank on the `<` branch instead and the answer comes back below `val`**, which
   still reads as plausible: `ceil(26)` returns 25, and `ceil(1)` returns `None`
   even though 2 is sitting in the tree.

```python
def ceil(root, val):
    """
    Find the smallest value in tree that is >= val.
    Time complexity: O(h)
    Aux space: O(1)
    """
    res = None
    while root is not None:
        if root.data == val:
            return root
        elif root.data < val:
            root = root.right
        else:
            res = root
            root = root.left
    return res

def test_ceil():
    root = create_test_bst()
    assert ceil(root, 10).data == 10
    assert ceil(root, 26).data == 30  # not 25: banking on `<` returns 25
    assert ceil(root, 1).data == 2  # below every key
    assert ceil(root, 50) is None  # walk never steps left
    assert ceil(None, 5) is None

test_ceil()
```

## Python Built-in Note

Python has **no built-in BST**. For sorted-container operations on a list, use the `bisect` module:

| BST Operation | `bisect` Equivalent | Time |
|---------------|--------------------|----- |
| Search | `bisect_left` + index check | O(log n) search, O(1) check |
| Insert (sorted) | `insort` | O(log n) search + O(n) shift |
| Floor | `bisect_right(a, x) - 1` | O(log n) |
| Ceil | `bisect_left(a, x)` | O(log n) |

The trade-off: `bisect` gives O(log n) search on a sorted list but O(n) insertion (due to array shifting). A BST gives O(h) for both. For a truly balanced BST with O(log n) everything, the third-party `sortedcontainers.SortedList` is the go-to.

See the binary-search notebook for `bisect` usage examples.
