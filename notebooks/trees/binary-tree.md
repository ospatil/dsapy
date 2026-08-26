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

Three of them are one walk. Go down into the left child, come back, go down into the
right child, come back. That walk is fixed. The only choice left is *when* you write
the node down: before both trips, between them, or after both. Three choices, three
names, one algorithm.

1. **Depth-first** - the walk above, named by where the node is recorded.
   1. **Preorder** - record before both trips - `10 20 40 50 70 80 30 60`
   2. **Inorder** - record between them - `40 20 70 50 80 10 30 60`
   3. **Postorder** - record after both - `40 70 80 50 20 60 30 10`
2. **Breadth-first** i.e Level order - `10 20 30 40 50 60 70 80`. The odd one out. It
   reads 40 then 50 then 60, and 40 lives under 20 while 60 lives under 30, so it has
   to jump between subtrees. The walk above can't jump - it finishes the left subtree
   entirely before touching the right. That is why level order needs a queue and the
   other three need nothing but the call stack.

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

### Inorder traversal (left → root → right)

The walk is the same in all three depth-first traversals, and it is short: go left,
come back, go right. The only thing that changes is where the "write this node down"
line sits.

```
def walk(node):
    record node        <- put it here and it is preorder
    walk(node.left)
    record node        <- here and it is inorder
    walk(node.right)
    record node        <- here and it is postorder
```

So the same five nodes come out in three different orders, and none of the three
changes which nodes are visited or how many times:

```
tree       10          preorder    10 20 30 40 50
         20  30        inorder     20 10 40 30 50
            40 50      postorder   20 40 50 30 10
```

Inorder appends between the two calls, so a node is written down once its entire left
subtree is finished and before any of its right subtree starts. That is the useful
part: it splits the output at every node into "everything left of me" and "everything
right of me". On a BST those two halves are exactly the smaller and the larger keys, so
inorder comes out sorted - which is why inorder is the one you reach for most often.

The `if root:` line is the base case, and it is doing real work: a missing child is
just an empty tree, so a leaf needs no special handling and neither does a node with
one child.

**Time:** Θ(n) &nbsp; **Space:** Θ(h) - one call-stack frame per level

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

test_inorder()
```

### Preorder traversal (root → left → right)

The append moves above both calls, so a node is written down before anything beneath
it. Parents always come out before their children.

That is what makes preorder the traversal for copying or serializing a tree. The first
thing you get is the root, and every node arrives before its descendants, so you can
rebuild top down: create each node as it comes out, and its parent already exists to
attach it to. On a BST that is literally replaying the values through `insert` and getting
the identical tree back. Inorder cannot do this - its output starts with `20`, a leaf, so
nothing in the sequence tells you which node was the root.

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

test_preorder()
```

### Postorder traversal (left → right → root)

The append moves below both calls, so a node is written down only when everything under
it is already done. Children before parents, the exact reverse of preorder's guarantee.

Reach for it whenever a node's answer depends on its children's answers. Freeing a tree
needs the children gone first, or you lose the pointers to them. Height and subtree sums
need the children's numbers before they can produce their own. `size`, `get_max` and
`height` below are all postorder wearing a different combiner.

It is also the only one of the three that is not tail-recursive - there is still
work to do after the last recursive call returns.

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

test_postorder()
```

### Size

Postorder with `+` as the combiner, and it is the template for nearly every "reduce a
tree to one number" function: ask both subtrees for their answers, then combine them
with this node's own contribution. `1 + size(left) + size(right)` - the 1 is this node.

The empty tree returns 0, and that is not an arbitrary choice. Adding 0 changes nothing,
so a missing child costs the answer nothing, which is why a leaf and a one-child node
need no case of their own. The value that leaves a combiner unchanged is called its
*identity*, and every function of this shape needs the right one.

**Time:** Θ(n) - every node must be visited &nbsp; **Space:** Θ(h)

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
    root = None
    assert size(root) == 0

test_size()
```

### Maximum element

Same shape as `size`, different combiner: `max` instead of `+`. So the identity has to
change with it. The empty tree returns `-inf`, because `-inf` loses every comparison and
therefore leaves the answer alone, the same job 0 was doing for `+`. Return 0 instead and
a tree of negative numbers gives the wrong answer.

Every one of the n nodes gets checked, and that is forced: a plain binary tree carries no
ordering, so the largest value could be anywhere and skipping a subtree is never safe.
Add the ordering rule and you can skip - in a BST the maximum is simply the rightmost
node, O(h).

**Time:** Θ(n) &nbsp; **Space:** Θ(h)

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
    root = None
    assert get_max(root) == -math.inf

test_get_max()
```

### Search

The same recursion once more, combined with `or`: this node is a hit, or the left subtree
has one, or the right subtree does. `or` is also the combiner that can stop early, since
Python stops evaluating as soon as something is true - so a hit in the left subtree means
the right subtree is never touched.

That helps in luck, not in the worst case. With no ordering to exploit there is nothing
smarter than looking everywhere, so a miss costs all n nodes. This is the exact problem a
BST solves: give the keys an order and one comparison throws half the tree away. See the
[binary search tree notebook](binary-search-tree.md).

**Time:** O(n) &nbsp; **Space:** Θ(h)

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
    assert not (search(root, 60))

test_search()
```

### Height

Postorder again: a node's height is 1 plus the taller of its two children. The whole
tree's height is just the root's.

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
    root = None
    assert height(root) == 0

test_height()
```

### Iterative inorder

To remove the recursion you have to take over the job the call stack was doing, so the
first question is what it was holding. It was holding the nodes you had walked past but
not finished: a node sits on the stack for exactly as long as its left subtree is still
in progress, deepest on top. Name that and the code follows.

Walking left as far as you can, pushing as you go, stacks up one such chain - a *spine* -
and leaves the leftmost node on top. That node has nothing to its left, so it is the
first thing inorder wants. Popping a node means its left subtree is done, so it may be
recorded now. What is still unfinished is its right subtree, and that enters the stack
the same way, as a spine of its own.

The stack's shape is the point, so it is worth watching:

```
stack shown bottom to top, top on the right
"emit" means append the value to the output list

push spine        stack [10, 20]
pop 20  -> emit   stack [10]        no right child
pop 10  -> emit   stack []          right = 30 -> push spine [30, 40]
pop 40  -> emit   stack [30]
pop 30  -> emit   stack []          right = 50 -> push [50]
pop 50  -> emit   stack []          done
```

Only one spine is ever on the stack, and a spine cannot be longer than the tree is tall.
That is why this costs the same memory as the recursion it replaces.

**Time:** Θ(n) &nbsp; **Space:** Θ(h) - the stack holds at most one spine

```python
def inorder_iter(root):
    """
    Time complexity: 𝛳(n)
    Aux Space: 𝛳(h) at any points there will be "height" no. of nodes in the stack
    """
    # we traverse to leftmost leaf by pushing nodes in a stack,
    # once there, we print its data. When that happens, it's left subtree will have been processed completely
    # we then continue with the right subtree and process its left subtrees
    if root is None:
        return

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

test_inorder_iter()
```

### Iterative preorder

Preorder needs no spine trick, because it records a node the moment it arrives at it.
Nothing is left half-finished, so the stack does not have to remember ancestors - it only
has to remember work not started yet. Pop a node, record it, push its children.

The one trap is push order. A stack hands back what went in last, so pushing left then
right would pop the right child first and the right subtree would come out ahead of the
left. Push **right first**.

The cost changes too. Both children go on the stack, so the stack can hold a whole level
at once rather than a single path.

**Time:** Θ(n) &nbsp; **Space:** O(n) - both children are pushed, so the stack can
hold an entire level

```python
def preorder_iter(root):
    """
    Time complexity: 𝛳(n)
    Aux Space: O(n) as we are pushing both right and left nodes in stack
    """
    if root is None:
        return
    roots = [root]
    result = []
    # consider a simple tree
    #   10
    # 20  30
    # We need to print 10, then 20 and then 30
    # we are using stack which is LIFO, therefore, in the code below,
    # we push 30 i.e right first and then 20 i.e left so that left
    # is popped first.
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
    assert preorder_iter(root) == [10, 20, 30, 40, 50]

test_preorder_iter()
```

### Level order (BFS)

This is the traversal the recursive walk cannot do. Reading a tree row by row means
leaving a subtree half-done to go and read the node beside it in the other subtree, and
the walk has no way to leave: entering the left child means finishing everything under it
before the right child is even looked at. The call stack enforces that, because the only
thing you can return to is where you came from.

So change what waits. One line differs from iterative preorder - take from the front of a
queue instead of the top of a stack. A stack hands back the newest thing, which keeps
pulling you deeper. A queue hands back the oldest, so a node's children line up *behind*
every node already waiting. Everything at depth k was queued before anything at depth
k+1, so depth k comes out first, all of it. Order in equals order out, which is what
*FIFO* means.

The cost follows the same swap. A stack held one path, so it cost the tree's height; a
queue holds a whole row, so it costs the tree's width.

This is plain BFS on a graph that happens to be a tree - no `visited` set is needed,
because a tree has no cycles and no shared nodes. See the
[graph traversal notebook](../graphs/graph-traversal.md).

**Time:** Θ(n) &nbsp; **Space:** O(w) where w is the widest level - up to n/2 for a
complete tree

```python
from collections import deque

def levelorder(root):
    """
    Time complexity: 𝛳(n)
    Aux Space:  O(n) as we are pushing a level in the queue i.e. width of the binary tree
    """
    if root is None:
        return
    # use queue to store nodes
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

test_levelorder()
```
