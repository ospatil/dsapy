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
# Binary Trees

Consider the following binary tree

```bash
        10
       /  \
     20    30
    /  \     \
  40    50    60
       /  \
     70    80
```

## Traversals

A list has one obvious order: front to back. A tree has none. Every node offers two
ways down, so "visit all the nodes" has to be given an order, and the traversals are
the four answers.

1. **Depth-first** - one recursive walk. The name says where the *root* falls
   among the three.
   1. **Preorder** - root, left, right - `10 20 40 50 70 80 30 60`
   2. **Inorder** - left, root, right - `40 20 70 50 80 10 30 60`
   3. **Postorder** - left, right, root - `40 70 80 50 20 60 30 10`
2. **Breadth-first** i.e Level order - `10 20 30 40 50 60 70 80`. The odd one out. It
   reads 40 then 50 then 60, and 40 lives under 20 while 60 lives under 30, so it has
   to jump between subtrees. A depth-first walk cannot jump - it finishes the left
   subtree entirely before touching the right. That is why level order needs a queue
   and the other three need nothing but the call stack.

## Variations of tree and uses:

* Binary search tree
* Binary heap: Mainly used to represent priority queues.
* B and B+ tree: Database indexes
* Spanning and shortest path trees: Used in computer networks
    * bridges use spanning tree to forward the packets
    * routers use shortest path trees to to route data
* Parse tree, expression tree: in compilers
* Trie: Used to represent dictionary, supports operations like prefix search
* Suffix tree: used for fast searches in string, if you have pattern and text \
    We can preprocess text, build suffix tree and search patterns in this tree \
    Time is proportional to length of pattern and not of the string.
* Binary index tree: Used for range query searches. Faster for limited set of operations.
* Segment tree: Used for range query searches. More powerful.

## Notes

* Degree of a node in a tree is the number of its children. Degree of a tree is the maximum degree of any node.
* Binary trees are most common type of tree.
* Binary tree can have 0, 1 or 2 children.
* Binary tree can also be represented as array.

> **Mental model.** Almost everything in this notebook is one recursive shape: do the
> left subtree, do the right subtree, combine. Traversals combine by appending to a
> list, `size` combines with `+`, `get_max` with `max`, `search` with `or`. Preorder,
> inorder and postorder are not three algorithms, they are that one walk with the
> "record this node" line in three different places. Level order is the exception,
> because it has to cross from one subtree to another and the walk never crosses.
>
> **Load-bearing:** the recursion copies the shape of the tree, so the deepest the call
> stack ever gets is the height of the tree. That is where every `Θ(h)` below comes
> from - about `log n` frames when the tree is bushy, but `n` frames when it is a single
> long chain. Shape, not node count, is what costs you, and a skewed tree makes every
> operation worse at the same time.
<!-- #endregion -->

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def create_test_tree():
        # tree
        #     10
        #  20    30
        #      40  50
        root = Node(10)
        root.left = Node(20)
        root.right = Node(30)
        root.right.left = Node(40)
        root.right.right = Node(50)
        return root
```

## Inorder traversal (left → root → right)

Start from the output you have to produce. Inorder wants every node to land between
the two halves of its own subtree: everything on its left side, then it, then
everything on its right side. Write that down as the contract for a single call -
**`inorder(node, ls)` appends the whole subtree at `node`, in that order, onto the end
of `ls`, and returns nothing** - and the body has one shape left. Trust the contract
for the left child, append this node, trust it for the right child. Nothing in the
code decides an order; the required output already did.

The contract is the only thing the three depth-first traversals disagree about, and
what they disagree about is where the node is recorded relative to its two subtrees:

```
def walk(node):
    record node        <- put it here and it is preorder
    walk(node.left)
    record node        <- here and it is inorder
    walk(node.right)
    record node        <- here and it is postorder
```

Same nodes, each visited once, three different orders:

```
tree       10          preorder    10 20 30 40 50
         20  30        inorder     20 10 40 30 50
            40 50      postorder   20 40 50 30 10
```

Inorder's split is the useful one: at every node the output divides into "everything
left of me" and "everything right of me". On a BST those two halves are exactly the
smaller and the larger keys, so inorder comes out sorted - which is why inorder is the
one you reach for most often.

The `if root:` line is the base case, and it is doing real work: a missing child is
just an empty tree, whose contribution to the output is nothing at all. That is why a
leaf needs no case of its own, and neither does a node with one child.

**Time:** Θ(n) &nbsp; **Space:** Θ(h) - one call-stack frame per level

**Recipe**

1. `if root:` and nothing else - no `else`, no explicit `return`.
2. `inorder(root.left, ls)`, then `ls.append(root.data)`, then
   `inorder(root.right, ls)`.
3. **`ls` is mutated in place and the call returns `None`.** There is nothing to
   combine on the way back up, and `res = inorder(root, [])` binds `None`; build
   the list first, pass it in, read it afterwards.

```python
def inorder(root, ls):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) where h is height since at any time there will be h function calls on call stack
    """
    if root:
        inorder(root.left, ls)
        ls.append(root.data)
        inorder(root.right, ls)


def test_inorder():
    root = create_test_tree()
    res = []
    inorder(root, res)
    assert res == [20, 10, 40, 30, 50]

    empty = []
    inorder(None, empty)
    assert empty == []  # empty tree contributes nothing

    single = []
    inorder(Node(7), single)
    assert single == [7]

test_inorder()
```

## Preorder traversal (root → left → right)

Ask for an output you can rebuild the tree from and the append position is forced the
other way. Rebuilding top down means creating each node as it arrives and attaching it
to a parent that already exists, so every node must be written down before anything
beneath it - which means recording it before descending at all. The contract per call
is inorder's with one clause moved: **`preorder(node, ls)` appends `node`, then its
left subtree, then its right subtree**. Parents always precede their children.

That is what makes preorder the traversal for copying or serializing a tree. Inorder
cannot do the job: its output starts with `20`, a leaf, so nothing in the sequence
tells you which node was the root. On a BST, replaying a preorder sequence through
`insert` rebuilds the identical tree.

**Time:** Θ(n) &nbsp; **Space:** Θ(h)

```python
def preorder(root, ls):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) where h is height since at any time there will be h function calls on call stack
    """
    if root:
        ls.append(root.data)
        preorder(root.left, ls)
        preorder(root.right, ls)


def test_preorder():
    root = create_test_tree()
    res = []
    preorder(root, res)
    assert res == [10, 20, 30, 40, 50]

    single = []
    preorder(Node(7), single)
    assert single == [7]

test_preorder()
```

## Postorder traversal (left → right → root)

The third position falls out of a different requirement: what if a node cannot be
handled until both of its children have been? Then it must be recorded last, after
both calls - **`postorder(node, ls)` appends both subtrees, then `node`** - so
children always precede parents, the exact reverse of preorder's guarantee.

That requirement is common. Freeing a tree needs the children gone first, or you lose
the pointers to them. Height and subtree sums need the children's numbers before they
can produce their own. `size`, `get_max` and `height` below are all this same walk,
with the child's report arriving as a returned value instead of an append.

It is also the only one of the three that is not tail-recursive - there is still work
to do after the last recursive call returns.

**Time:** Θ(n) &nbsp; **Space:** Θ(h)

```python
def postorder(root, ls):
    """
    Time complexity: 𝛳(n)
    Aux Space:  𝛳(h) where h is height since at any time there will be h function calls on call stack
                postorder is not tail-recursive, while other two are.
    """
    if root:
        postorder(root.left, ls)
        postorder(root.right, ls)
        ls.append(root.data)


def test_postorder():
    root = create_test_tree()
    res = []
    postorder(root, res)
    assert res == [20, 40, 50, 30, 10]
    assert res[-1] == root.data  # the root is last, always

    single = []
    postorder(Node(7), single)
    assert single == [7]

test_postorder()
```

## Size

Every "reduce a tree to one number" function starts by naming what a call gives back.
Here: **`size(node)` returns the number of nodes in the subtree rooted at `node`**, so
the call on the root is the answer for the whole tree and no other bookkeeping is
needed. With the return named, the body is arithmetic - take each child's count and
add your own 1: `1 + size(root.left) + size(root.right)`.

The empty tree returns 0, and that is not an arbitrary choice. Adding 0 changes nothing,
so a missing child costs the answer nothing, which is why a leaf and a one-child node
need no case of their own. The value that leaves a combiner unchanged is called its
*identity*, and every function of this shape needs the right one.

**Time:** Θ(n) - every node must be visited &nbsp; **Space:** Θ(h)

**Recipe**

1. `if root is None: return 0`.
2. Otherwise `return 1 + size(root.left) + size(root.right)`.

```python
def size(root):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) where h is height since at any time there will be (h+1) function calls on call stack
    """
    # no of nodes in the binary tree
    if root is None:
        return 0
    return 1 + size(root.left) + size(root.right)

def test_size():
    root = create_test_tree()
    assert size(root) == 5
    assert size(Node(7)) == 1
    root = None
    assert size(root) == 0

test_size()
```

## Maximum element

**`get_max(node)` returns the largest value in the subtree rooted at `node`.** Same
shape as `size` with a different combiner - `max` instead of `+` - so the identity has
to change with it. The empty tree returns `-inf`, because `-inf` loses every comparison
and therefore leaves the answer alone, the same job 0 was doing for `+`. Return 0
instead and a tree of negative numbers gives the wrong answer.

Every one of the n nodes gets checked, and that is forced: a plain binary tree carries no
ordering, so the largest value could be anywhere and skipping a subtree is never safe.
Add the ordering rule and you can skip - in a BST the maximum is simply the rightmost
node, O(h).

**Time:** Θ(n) &nbsp; **Space:** Θ(h)

**Recipe**

1. `if root is None: return -math.inf`.
2. Otherwise `return max(root.data, get_max(root.left), get_max(root.right))`.
3. **Not `0`, and not `None`.** `0` silently returns the wrong answer on an
   all-negative tree; `None` raises inside `max`.

```python
import math

def get_max(root):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) where h is height since at any time there will be (h+1) function calls on call stack
    """
    # maximum element in the binary tree, return -infinity for none
    if root is None:
        return -math.inf
    return max(root.data, get_max(root.left), get_max(root.right))

def test_get_max():
    root = create_test_tree()
    assert get_max(root) == 50
    assert get_max(Node(7)) == 7

    neg = Node(-5)
    neg.left = Node(-9)
    neg.right = Node(-7)
    assert get_max(neg) == -5  # would come out 0 if the identity were 0

    root = None
    assert get_max(root) == -math.inf

test_get_max()
```

## Search

**`search(node, data)` returns whether the subtree rooted at `node` contains `data`** -
whether, not where, which is why a bool is enough to combine. The combiner is `or`: this
node is a hit, or the left subtree has one, or the right subtree does. `False` is its
identity, so the empty tree returns `False`. `or` also stops early, since Python stops
evaluating as soon as something is true - a hit in the left subtree means the right
subtree is never touched.

That helps in luck, not in the worst case. With no ordering to exploit there is nothing
smarter than looking everywhere, so a miss costs all n nodes. This is the exact problem a
BST solves: give the keys an order and one comparison throws half the tree away. See the
[binary search tree notebook](binary-search-tree.md).

**Time:** O(n) &nbsp; **Space:** Θ(h)

**Recipe**

1. `if root is None: return False`, then `if root.data == data: return True`.
2. Otherwise `return search(root.left, data) or search(root.right, data)`.
3. **Return the `or`, do not just evaluate it.** A bare recursive call whose
   result is dropped makes every deep hit read as a miss.

```python
def search(root, data):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) where h is height since at any time there will be (h+1) function calls on call stack
    """
    # search for key in the binary tree
    if root is None:
        return False
    if root.data == data:
        return True
    return search(root.left, data) or search(root.right, data)

def test_search():
    root = create_test_tree()
    assert search(root, 50)
    assert search(root, 10)          # the root itself
    assert not (search(root, 60))
    assert search(Node(7), 7)
    assert not (search(None, 7))     # empty tree, no hit

test_search()
```

## Height

**`height(node)` returns the number of nodes on the longest path from `node` down to a
leaf**, so a node's answer is 1 plus the taller of its two children's, and the whole
tree's height is the root's answer. The combiner is `max`, and 0 is its identity here
because an empty subtree must not lengthen a path.

This is the number every other `Θ(h)` in the notebook is measured in, so it is worth
knowing what makes it big. Height is set by the tree's shape, not by how many nodes it
holds. Five nodes in a chain have height 5; five nodes packed tight have height 3. Since
the recursion follows the shape, the deepest the call stack ever gets is that height -
`log n` frames when the tree is bushy, n frames when it is a chain. That single number
is why a skewed tree hurts search, insert and every traversal at once, and why the
self-balancing trees exist: see the [AVL tree notebook](avl-tree.md).

Two conventions exist - count *nodes* on the longest root-to-leaf path (single node = 1,
empty = 0) or count *edges* (single node = 0, empty = -1). This notebook counts nodes, so
the three-level test tree has height 3 and an empty tree has height 0.

**Time:** Θ(n) &nbsp; **Space:** Θ(h)

**Recipe**

1. `if root is None: return 0`, matching this notebook's node-counting convention.
   **Mixing the node and edge conventions is where the off-by-one bugs in AVL
   balance factors come from**, so commit to one before writing a line.
2. Otherwise `return 1 + max(height(root.left), height(root.right))`.
3. **`max`, not `+`.** Height is the longest single path, not a total - `+` would
   compute the size instead, and the two agree on a chain, so a skewed test case
   will not catch it.

```python
def height(root):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) where h is height since at any time there will be (h+1) function calls on call stack

    There are two conventions for height of a tree:
    1. Maximum number of nodes on longest (root to leaf) path
        height of single node tree is 1
        height of empty tree is 0
    2. Maximum number of edges on longest path
        height of single node tree is 0
        height of empty tree is -1
    We'll use 1.
    """
    # height of the binary tree
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))

def test_height():
    root = create_test_tree()
    assert height(root) == 3
    assert height(Node(7)) == 1  # single node = 1 under the node convention
    root = None
    assert height(root) == 0

test_height()
```

## Iterative inorder

Removing the recursion means taking over the job the call stack was doing, so the whole
design question is what that stack held. It held the nodes walked past but not
finished: a node sits there for exactly as long as its left subtree is still in
progress, deepest on top. That is what `roots` is, and naming it fixes the meaning of
both operations on it. Pushing means "started, cannot be emitted yet". Popping means
"my left subtree is done", which by inorder's contract is the moment the node may be
emitted - and what remains unfinished for it is its right subtree.

Walking left as far as possible, pushing as you go, stacks up one such chain - a
*spine* - and leaves the leftmost node on top, which is the node inorder wants first
because it has nothing to its left. A popped node's right subtree then enters `roots`
the same way, as a spine of its own.

The stack's shape is the point, so it is worth watching:

```
roots drawn bottom to top, top on the right
"emit" means append the value to result

push spine from 10     roots [10, 20]
pop 20, emit 20        roots [10]        right is None, nothing to push
pop 10, emit 10        roots [30, 40]    right is 30, so push the spine 30, 40
pop 40, emit 40        roots [30]        right is None
pop 30, emit 30        roots [50]        right is 50, so push the spine 50
pop 50, emit 50        roots []          right is None, the loop ends

result   20 10 40 30 50
```

Only one spine is ever on the stack, and a spine cannot be longer than the tree is tall.
That is why this costs the same memory as the recursion it replaces.

**Time:** Θ(n) &nbsp; **Space:** Θ(h) - `roots` holds at most one spine

**Recipe**

1. `if root is None: return []`.
2. From `curr = root`, loop `roots.append(curr)` then `curr = curr.left` while
   `curr is not None`. **Emit nothing on the way down.**
3. While `roots`: `curr = roots.pop()`, `result.append(curr.data)`, then
   `curr = curr.right`.
4. Still inside that same iteration, run step 2's loop again from `curr`. **The
   push-all-the-way-left loop has to be written out twice.** Step to `curr.right`
   and pop straight away and the right child is emitted ahead of its own left
   subtree.
5. `return result` after the loop, not inside it.

```python
def inorder_iter(root):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) - roots holds one spine, no longer than the tree is tall
    """
    # roots holds the nodes walked past but not finished: each one is waiting for its
    # left subtree. Popping means that subtree is done, so the node can be emitted, and
    # its right subtree then goes on as a spine of its own.
    if root is None:
        return []

    roots = []
    result = []  # will hold result of the traversal
    curr = root
    while curr is not None:
        roots.append(curr)
        curr = curr.left
    # we are at the leftmost leaf, time to pop the stack
    while roots:
        curr = roots.pop()
        result.append(curr.data)
        curr = curr.right  # now go to the right subtree
        while curr is not None:
            roots.append(curr)
            curr = curr.left
    return result

def test_inorder_iter():
    root = create_test_tree()
    assert inorder_iter(root) == [20, 10, 40, 30, 50]
    assert inorder_iter(Node(7)) == [7]
    assert inorder_iter(None) == []

    # matches the recursive version on a right-leaning chain, where the second
    # push-left loop is what keeps the order right
    chain = Node(1)
    chain.right = Node(2)
    chain.right.left = Node(3)
    assert inorder_iter(chain) == [1, 3, 2]

test_inorder_iter()
```

## Iterative preorder

Preorder's contract lets a node be emitted the instant it is reached, so nothing is
ever left half-finished and `roots` does not have to remember ancestors at all. Here
it is a to-do list: nodes that have been discovered but not yet emitted. Popping
therefore means "take the next thing owed", not "a subtree has finished", and the
whole loop is pop, emit, push both children.

The one trap is push order. A stack hands back what went in last, so pushing left then
right would pop the right child first and the entire right subtree would come out
ahead of the left. Push **right first**.

Pushing two children per pop looks like it should cost more memory than the spine did,
and it does not. `roots` holds the next node to emit, plus the right siblings deferred
along the path that led to it. A complete seven-node tree shows the shape; the stack
top is on the right:

```
        1
      /   \
     2     3
    / \   / \
   4   5 6   7

after emitting 1   roots [3, 2]
after emitting 2   roots [3, 5, 4]   peak: next 4, with pending siblings 5 and 3
after emitting 4   roots [3, 5]
after emitting 5   roots [3]
after emitting 3   roots [7, 6]      level 3 has four nodes; at most two wait here
```

The stack grows with depth, not with the number of nodes on a level, so it stays
Θ(h). Width is paid for by level order below, not here.

**Time:** Θ(n) &nbsp; **Space:** Θ(h) - next node plus pending siblings on one path

**Recipe**

1. `if root is None: return []`, then `roots = [root]`.
2. While `roots`: `curr = roots.pop()`, `result.append(curr.data)`.
3. `roots.append(curr.right)`, then `roots.append(curr.left)`, each guarded by its
   own `is not None` check. **There is no base case here to absorb an empty
   child**, so an unguarded push crashes on the next pop.
4. **Right before left.** Swap those two lines and you get a valid preorder of the
   *mirrored* tree - the kind of bug a symmetric test case passes; the test tree
   below is lopsided on purpose.
5. `return result` after the loop.

```python
def preorder_iter(root):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) - next node plus deferred siblings along one path
    """
    if root is None:
        return []
    roots = [root]  # to-do list: discovered but not yet emitted
    result = []
    # Push right first so left is popped first.
    while roots:
        curr = roots.pop()
        result.append(curr.data)
        if curr.right is not None:
            roots.append(curr.right)
        if curr.left is not None:
            roots.append(curr.left)
    return result

def test_preorder_iter():
    root = create_test_tree()
    # lopsided on purpose: swapping the two pushes gives [10, 30, 50, 40, 20]
    assert preorder_iter(root) == [10, 20, 30, 40, 50]
    assert preorder_iter(Node(7)) == [7]
    assert preorder_iter(None) == []

test_preorder_iter()
```

## Level order (BFS)

This is the traversal the recursive walk cannot do. Reading a tree row by row means
leaving a subtree half-done to go and read the node beside it in the other subtree, and
the walk has no way to leave: entering the left child means finishing everything under it
before the right child is even looked at. The call stack enforces that, because the only
thing you can return to is where you came from.

So change what waits. `q` holds exactly what `roots` held in iterative preorder -
nodes discovered but not yet emitted - and only the discipline over it changes. A stack
hands back the newest thing, which keeps pulling you deeper. A queue hands back the
oldest, so a node's children line up *behind* every node already waiting. Everything
at depth k was queued before anything at depth k+1, so depth k comes out first, all of
it. Order in equals order out, which is what *FIFO* means.

The cost follows the same swap. The stack held one path down the tree, so it cost the
tree's height; the queue holds a whole row, so it costs the tree's width - and that is
the one place in this notebook where width, not height, is what you pay.

This is plain BFS on a graph that happens to be a tree - no `visited` set is needed,
because a tree has no cycles and no shared nodes. See the
[graph traversal notebook](../graphs/graph-traversal.md).

**Time:** Θ(n) &nbsp; **Space:** O(w) where w is the widest level - up to n/2 for a
complete tree

**Recipe**

1. `if root is None: return []`, then `q = deque()` holding just `root`.
2. While `q`: `curr = q.popleft()`, `result.append(curr.data)`, then append
   `curr.left` and `curr.right` when each is not `None`.
3. **`popleft`, not `pop`** - the one call that separates this from
   `preorder_iter`, and `pop` fails quietly by producing a depth-first order.
4. **`collections.deque`, not a list.** `list.pop(0)` is O(n) because every
   remaining element shifts down, turning the traversal quadratic with no visible
   symptom on small trees.
5. Left then right, with no reversal trick: a queue comes out in the order it went
   in. `return result` after the loop.

```python
from collections import deque

def levelorder(root):
    """
    Time complexity: 𝛳(n)
    Aux Space:  O(w) - q holds at most one level, i.e. the width of the binary tree
    """
    if root is None:
        return []
    # q holds discovered-but-not-emitted nodes, oldest first
    q = deque()
    result = []
    q.append(root)
    while q:
        curr = q.popleft()
        result.append(curr.data)
        if curr.left is not None:
            q.append(curr.left)
        if curr.right is not None:
            q.append(curr.right)
    return result

def test_levelorder():
    root = create_test_tree()
    assert levelorder(root) == [10, 20, 30, 40, 50]
    assert levelorder(Node(7)) == [7]
    assert levelorder(None) == []

    # a shape where level order and preorder disagree, so a stack instead of a
    # queue could not pass: the last row crosses from one subtree to the other
    #     1
    #   2   3
    #  4     5
    cross = Node(1)
    cross.left = Node(2)
    cross.right = Node(3)
    cross.left.left = Node(4)
    cross.right.right = Node(5)
    assert levelorder(cross) == [1, 2, 3, 4, 5]
    assert preorder_iter(cross) == [1, 2, 4, 3, 5]

test_levelorder()
```
