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
    # prev links point back: 3 -> dummy, 2 -> 3, 1 -> 2
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
