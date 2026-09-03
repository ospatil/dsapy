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

# Doubly Linked List

Each node holds a value plus `prev` and `next` pointers. The extra link costs
memory but buys backward traversal and O(1) deletion when you already hold a
reference to the node - no need to walk the list to find its predecessor.

| Operation | Singly | Doubly |
|---|---|---|
| Insert / delete at front | O(1) | O(1) |
| Delete a node you hold a reference to | O(n) - find predecessor first | O(1) |
| Traverse backwards | not possible | O(n) |
| Pointers per node | 1 | 2 |

**Space:** O(n), with two extra pointers of overhead per node.
> **Mental model.** A [singly linked list](singly-linked-list.md) can only look forwards.
> Every change there needs the node *before* the target, and finding it costs a walk -
> that one limit is where its whole cost model comes from. The `prev` pointer buys exactly
> one thing back: hand it a node and it can unlink that node without knowing what came
> before. So deleting a node you already hold drops from O(n) to O(1), and the reversal
> that needed a temporary variable no longer needs one, because the rest of the list stays
> reachable from the node just moved. The price is one more pointer per node than a singly
> linked list carries.
>
> **Load-bearing:** every operation now has to fix *two* directions, and it has to fix
> them as a pair. Repair only the `next` links and the list still walks correctly
> forwards. It lies only when walked backwards - so half the tests keep passing, which is
> the worst kind of bug to be handed.

```python
class ListNode:
     def __init__(self, val=0):
         self.val = val
         self.prev, self.next = None, None

def to_list(head):
    ls = []
    curr = head.next
    while curr:
        ls.append(curr.val)
        curr = curr.next
    return ls
```

We'll use a dummy head for all functions.


### Insert at front

The forward half is the singly linked list's splice, unchanged: the new node adopts the
rest of the list, then the dummy lets go of it. The order trap is unchanged too - read
`head.next` into the new node before overwriting it, or the rest of the list is lost.

The backward half is what's new, and it is two pointers, not one. The new node points back
at the dummy, *and* the node that used to be first has to point back at the new node.
Forgetting the second one costs nothing that a forward walk can see. An empty list has no
old first node, which is the only thing the `if new.next` guard is for.

**Time:** O(1) &nbsp; **Space:** O(1)

**Recipe**

Four pointers touch this splice, and the singly-linked version only had two.

1. `new.next = head.next`, then `head.next = new`, same order and same reason as
   the singly linked list.
2. `new.prev = head`. The dummy is a real node here, so the first node's `prev`
   points at it rather than being `None`.
3. `if new.next: new.next.prev = new`. **The guard is the empty-list case: there
   is no old first node whose `prev` needs repairing.**
4. Forgetting step 3 leaves a list that reads correctly forwards and is broken
   backwards, which no forward traversal will ever catch.

```python
def insert_front(head, val):
    new = ListNode(val)
    new.next = head.next
    head.next = new
    new.prev = head
    if new.next:  # empty list has no old first node to repair
        new.next.prev = new


def test_insert_front():
    head = ListNode(-1)
    insert_front(head, 1)
    insert_front(head, 2)
    insert_front(head, 3)
    assert to_list(head) == [3, 2, 1]
    # prev pointers run the other way: 3.prev is dummy, 2.prev is 3, 1.prev is 2
    assert head.next.prev is head
    assert head.next.next.prev is head.next


test_insert_front()
```

### Insert at end

Still O(n), and the reason is worth naming. A `prev` pointer lets you move backwards from
a node you are already holding. It never helps you *find* a node. Nothing in this list
points at the back, so the last node still has to be found by walking.

Starting the walk at the dummy rather than `head.next` lets the empty list run the same
code, since the dummy is then the last node.

A real doubly linked list keeps a tail pointer (or a second sentinel at the back), and
this becomes O(1). `collections.deque` is that list, which is why the built-in section
below matters more than this function.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. Walk from the dummy while `curr.next`, landing on the last node.
2. `curr.next = new` and `new.prev = curr`.
3. **Only two links here, against four in `insert_front`.** `new` is the tail, so
   its `next` is already `None` and there is no following node with a `prev` to
   repair.

```python
def insert_end(head, val):
    new = ListNode(val)
    curr = head
    while curr.next:  # walk to the last node; the dummy is it when list is empty
        curr = curr.next
    curr.next = new
    new.prev = curr


def test_insert_end():
    head = ListNode(-1)
    insert_end(head, 1)  # into an empty list
    assert to_list(head) == [1]
    insert_end(head, 2)
    insert_end(head, 3)
    assert to_list(head) == [1, 2, 3]
    # prev links chain back to the dummy
    assert head.next.prev is head
    assert head.next.next.prev is head.next


test_insert_end()
```

### Delete front

Hop the dummy over the first node, then repair the new first node's `prev`. The outer guard
is for the empty list. The inner one is for deleting the only node, where there is no new
first node left to repair.

This is the smallest instance of the card's warning. Drop the `prev` repair and `to_list`
still returns the right answer, because it only follows `next`. The list is broken in the
one direction nothing is looking.

**Time:** O(1) &nbsp; **Space:** O(1)

**Recipe**

1. `if head.next:` guards the empty list.
2. `head.next = head.next.next` unlinks forwards.
3. `if head.next:` **again**, because the list may have just become empty and
   there is no new first node to fix. **Two separate guards on the same
   expression, checked before and after the unlink.**
4. `head.next.prev = head` repairs the backward link.

```python
def delete_front(head):
    if head.next:
        head.next = head.next.next
        if head.next:  # list may now be empty
            head.next.prev = head


def test_delete_front():
    head = ListNode(-1)
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    delete_front(head)
    assert to_list(head) == [2, 3]
    assert head.next.prev is head

    # delete down to empty, then once more
    delete_front(head)
    delete_front(head)
    assert to_list(head) == []
    delete_front(head)
    assert head.next is None


test_delete_front()
```

### Delete end

Deleting always costs two things: finding the node, and unlinking it. Separating them is
what makes this function's O(n) make sense. Unlinking the last node is free here - `prev`
hands you its predecessor - where a singly linked list has to walk to find that
predecessor. Finding the last node is still O(n), because nothing points at the back.

So the cost that remains is the search, not the delete. Given a tail pointer the whole
function collapses to `tail = tail.prev`, and that collapse is the reason to pay for the
second pointer at all.

Without one we walk, stopping one node short via `curr.next.next`. The empty-list guard has
to come first, or that expression reads a field off `None`.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. Empty list, return.
2. Walk while `curr.next.next` to stop on the second-to-last node.
3. `curr.next = None`.
4. **Nothing else needs fixing.** The new tail's `prev` already pointed where it
   should; only the dropped node held pointers that are now stale, and it is
   unreachable.
5. Note this is still O(n) even in a doubly linked list, because the walk starts
   from the dummy. Keeping a tail pointer is what makes it O(1), and this
   notebook does not.

```python
def delete_end(head):
    if head.next is None:  # empty list
        return
    curr = head
    while curr.next.next:  # stop on the second-last node
        curr = curr.next
    curr.next = None


def test_delete_end():
    head = ListNode(-1)
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    delete_end(head)
    assert to_list(head) == [1, 2]

    # down to a single element, then empty, then a no-op
    delete_end(head)
    assert to_list(head) == [1]
    delete_end(head)
    assert to_list(head) == []
    delete_end(head)
    assert head.next is None


test_delete_end()
```

### Delete a node you already hold

This is the operation the second pointer exists for, and the only row in the table at the top
where the two list types differ by more than a constant.

In a singly linked list, deleting a node you are holding is awkward for one reason: you need
the node *before* it to redirect, and from the node itself there is no way back. So you walk
from the head to find the predecessor, and an O(1)-looking operation costs O(n). The `prev`
pointer removes the search entirely - the predecessor is one dereference away.

Be precise about the claim, though. It is the *unlink* that is O(1). Locating the node in the
first place is still a walk, so `delete_node` only pays off when something else already handed
you the reference - which is exactly the situation an LRU cache is in, holding a dict from key
to node so the list never has to be searched at all.

Two details. The tail has nobody behind it, so the backward repair has to be guarded, the same
shape of guard as `delete_front`. And the removed node's own pointers are cleared afterwards:
nothing in the list still references it, but the caller's variable does, and leaving it wired
to its old neighbours means a stale reference can still walk into a list it is no longer part
of.

**Time:** O(1) &nbsp; **Space:** O(1)

**Recipe**

The operation the whole structure exists for: unlink in O(1) with no walk.

1. Return if `node is None`, or if `node.prev is None`. **The second test
   identifies the dummy, which must never be removed.**
2. `node.prev.next = node.next` closes the gap forwards. **This line is why a
   doubly linked list can do it in constant time: the node behind is one hop
   away, rather than a full traversal away.**
3. `if node.next: node.next.prev = node.prev` closes it backwards, guarded
   because a tail has nobody behind it.
4. `node.prev = node.next = None`. **Not tidiness. A caller still holding this
   reference could otherwise keep walking into the live list from a node no
   longer in it.**

```python
def delete_node(node):
    """Unlink a node you already hold a reference to. Time: O(1)"""
    if node is None or node.prev is None:
        return  # nothing to do, or this is the dummy head, which never leaves
    node.prev.next = node.next
    if node.next:  # a tail has nobody behind it to repair
        node.next.prev = node.prev
    node.prev = node.next = None  # so a stale reference cannot walk the old list


def test_delete_node():
    head = ListNode(-1)
    for v in (1, 2, 3, 4):
        insert_end(head, v)

    middle = head.next.next  # the node holding 2
    delete_node(middle)
    assert to_list(head) == [1, 3, 4]
    assert head.next.next.val == 3
    assert head.next.next.prev is head.next  # backward direction repaired too
    assert middle.prev is None and middle.next is None  # detached

    tail = head.next.next.next  # the node holding 4
    delete_node(tail)
    assert to_list(head) == [1, 3]
    assert head.next.next.next is None

    delete_node(head.next)  # the first real node; the dummy takes over
    assert to_list(head) == [3]
    assert head.next.prev is head

    delete_node(head.next)  # down to empty
    assert to_list(head) == []

    # handed the dummy, or nothing at all: a no-op, not a crash
    delete_node(head)
    delete_node(None)
    assert to_list(head) == []


test_delete_node()
```

### Reverse

Reversing a [singly linked list](singly-linked-list.md) means moving nodes, one at a time,
out of the untouched part and onto the front of the reversed part. Here nothing moves. Every
node already holds both of its neighbours, so reversing the list means each node swaps which
neighbour it calls `next`. One swap per node and it is done.

The temporary variable disappears, and that is the second pointer paying for itself. In a
singly linked list, overwriting `curr.next` destroys the only route to the rest of the list,
so the route has to be saved first. Here it is not destroyed, it is moved: after the swap
the old `next` is sitting in `curr.prev`. That is why the walk continues with
`curr = curr.prev`, which looks backwards and is correct.

`prev` in this loop does not mean what it meant in the singly version. It is not the head of
a reversed region - it is just the last node visited. When the loop ends, the last node
visited is the old final node, which is the new first node.

One line is load-bearing and easy to leave out: `curr.prev = None` before the loop. The dummy
is not part of the list being reversed, but the first node points back at it. Leave that
pointer alone and the swap turns it into the new tail's `next`, so the list runs back into
the dummy and `to_list` never terminates. Detaching first makes the new tail end in `None`,
and the two lines after the loop attach the dummy at the other end instead.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `curr = head.next`. If the list is non-empty, set `curr.prev = None` first.
   **The old first node becomes the new tail, and its `prev` currently points at
   the dummy, which would leave a link into a node that is no longer behind it.**
2. `prev = None`, then loop while `curr`.
3. Set `prev = curr` at the **top** of the body, so that when the loop ends
   `prev` still holds the last node visited. That is the new head.
4. Reverse the node itself with one swap: `curr.prev, curr.next = curr.next,
   curr.prev`. **In a doubly linked list, reversing a node is just exchanging its
   two pointers. There is no temporary and no `next` to save, because the
   forward pointer survives in `prev`.**
5. Advance with `curr = curr.prev`, **not `curr.next`**. The swap already
   happened, so the node's original `next` now lives in `prev`.
6. `head.next = prev`, and `prev.prev = head` if the list was not empty.

```python
def reverse(head):
    curr = head.next
    if curr:
        curr.prev = None  # detach from dummy so the new tail terminates the list
    prev = None
    while curr:
        # remember curr: when the loop ends, prev holds the old last node,
        # which becomes the new first node
        prev = curr
        # reversing a DLL node just means swapping its two pointers
        curr.prev, curr.next = curr.next, curr.prev
        # after the swap the old next is reachable through prev
        curr = curr.prev
    head.next = prev
    if prev:
        prev.prev = head


def test_reverse():
    head = ListNode(-1)
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    reverse(head)
    assert to_list(head) == [3, 2, 1]
    # prev links are consistent in the reversed list
    assert head.next.prev is head
    assert head.next.next.prev is head.next

    # reversing twice restores the original order
    reverse(head)
    assert to_list(head) == [1, 2, 3]

    # single element and empty list
    head = ListNode(-1)
    insert_end(head, 1)
    reverse(head)
    assert to_list(head) == [1]

    head = ListNode(-1)
    reverse(head)
    assert to_list(head) == []


test_reverse()
```

# Python Built-in: `collections.deque`

Python's `collections.deque` is implemented as a **doubly-linked list** of fixed-size blocks.

| Operation | deque | list |
|-----------|-------|------|
| Append right | O(1) | O(1) amortized |
| Append left | O(1) | O(n) - shifts all elements |
| Pop right | O(1) | O(1) |
| Pop left | O(1) | O(n) - shifts all elements |

Use `deque` whenever you need efficient operations on both ends.

```python
from collections import deque

d = deque([1, 2, 3])

d.appendleft(0)   # O(1) - [0, 1, 2, 3]
d.append(4)        # O(1) - [0, 1, 2, 3, 4]
d.popleft()        # O(1) - returns 0, deque is [1, 2, 3, 4]
d.pop()            # O(1) - returns 4, deque is [1, 2, 3]

# rotate: move n elements from one end to the other
d.rotate(1)        # [3, 1, 2] - right rotate
d.rotate(-1)       # [1, 2, 3] - left rotate

# bounded deque: automatically discards from opposite end
bounded = deque(maxlen=3)
for i in range(5):
    bounded.append(i)
print(list(bounded))  # [2, 3, 4] - oldest elements dropped
```
