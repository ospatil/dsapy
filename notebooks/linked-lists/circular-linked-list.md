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

# Circular Linked List

Take a [singly linked list](singly-linked-list.md) and delete the `None` at the
end: the last node points back at the first instead. That single change is the
whole topic. Every difference below follows from it.

The list now has no end to fall off, so every node can reach every other node.
That is what makes it fit round-robin scheduling and ring buffers, where "next"
should never run out. It also means one pointer reaches both ends at once: stand
on the last node and the first node is one hop away. That is why the O(1)
inserts below are possible, and why adding to the front and adding to the back
turn out to be the same operation.

Each insert appears twice: the obvious O(n) version that walks to the last node,
and an O(1) version that swaps values instead of walking.

> **Mental model.** A ring with a label on it. `head.next` is the label, and all it
> says is which node counts as first - which also fixes the last node, since the
> last node is whichever one points at the first. Nothing in the pointers marks
> either end, so moving the label is enough to turn an insert at the front into an
> insert at the back.
>
> **Load-bearing:** the stopping rule of every loop. `while curr` never becomes
> false here, because `next` is never `None`. A walk has to stop when it arrives
> back where it started, so the *first* node is the boundary instead of a `None` at
> the end. The empty list is the case that needs care, because there is no node to
> come back to - that is what every `if not first` guard is for.


We'll use a dummy head for all functions. It sits *outside* the ring: the last
node points back at the first real node, never at the dummy. So `head` is not
part of the structure, it only holds the label.


![Circular Linked List](images/circular-linked-list.png)


### Node and traversal helper

The node is unchanged - one value, one `next`. Nothing inside a node says the
list is circular. Only the shape of the links does.

That is enough to break the loop every singly linked walk uses. `while curr:`
waits for a `None` that never comes, so it spins forever. A walk needs some other
way to know it is finished, and the only landmark a ring offers is the node the
walk started from. Stop when you get back to it: `while curr is not first`.

Making the first node the boundary has a side effect. Start the loop on `first`
and the test is false immediately, so the walk ends before reading anything. The
first value therefore has to be collected before the loop, and the loop starts
one node later.

An empty list has no starting node, so there is nothing to come back to and the
wrap-around test has nothing to compare against. Hence the early return.

```python
class ListNode:
    def __init__(self, val=0):
        self.val = val
        self.next = None

def to_list(head):
    ls = []
    first = head.next
    if not first: # empty list
        return ls
    ls.append(first.val)
    curr = first.next
    while curr is not first: # continue till list wraps around
        ls.append(curr.val)
        curr = curr.next
    return ls
```

### Insert at beginning, the direct way

Reaching the first node is free - it is `head.next`. Putting a *new* node in front
of it is not the same job. The pointer that has to change belongs to the **last**
node, because that is the pointer aimed at the front of the list. A ring offers no
route backwards to it, so getting there costs a full lap.

The expense is the search, not the insert. The splice is the usual two
assignments, in the usual order: the new node adopts the rest of the ring first,
then the old last node lets go of it. Do it the other way round and `curr.next` is
overwritten while nothing else points at the first node, which loses the whole
list.

`head.next = new` is the line that actually makes the new node first. The
pointers by themselves never said which node was.

**Time:** O(n), essentially all of it spent finding the last node &nbsp;
**Space:** O(1)

```python
def insert_begin_linear(head, val):
    new = ListNode(val)
    first = head.next # keep reference to first node for wraparound check
    if not first: # empty list, new node becomes the head
        new.next = new # make circular
    else:
        curr = first.next
        while curr.next is not first: # find the last node
            curr = curr.next
        # insert new node
        new.next = curr.next # link new node to the last node
        curr.next = new
    head.next = new # update head to new node


def test_insert_begin_linear():
    head = ListNode(-1)
    insert_begin_linear(head, 1)
    assert to_list(head) == [1]
    insert_begin_linear(head, 2)
    assert to_list(head) == [2, 1]
    insert_begin_linear(head, 3)
    assert to_list(head) == [3, 2, 1]

test_insert_begin_linear()
```

### Insert at beginning in O(1)

The lap is only there to make a new *node* first. Nobody asked for that. What was
asked is that the new *value* be read first. Give up on moving nodes and the walk
disappears: hook the new node into second place, which needs no walk because the
first node is right there, then swap the two values.

```
insert 9 into      D → [1] → [2] → ...
link after first   D → [1] → [9] → [2] → ...
swap the values    D → [9] → [1] → [2] → ...
```

The nodes never move. Only what they hold changes, and the node that was already
first is still first, so `head` is untouched and the last node is never needed.

The price is that a value no longer stays in one node. Any reference a caller kept
to the old first node now reads a different value. That is fine for a list of
values and wrong when a node itself is the thing being tracked.

**Time:** O(1) &nbsp; **Space:** O(1)

```python
def insert_begin_constant(head, val):
    # neat trick, insert new node at second place and swap data with first node
    new = ListNode(val)
    first = head.next # keep reference to first node for wraparound check
    if not first: #empty list
        new.next = new # make circular
        head.next = new # update head to new node
    else:
        # add new node after first node
        new.next = first.next
        first.next = new
        new.val, first.val = first.val, new.val # swap data
        # no need to update head as first node is still the first node


def test_insert_begin_constant():
    head = ListNode(-1)
    insert_begin_constant(head, 1)
    assert to_list(head) == [1]
    insert_begin_constant(head, 2)
    assert to_list(head) == [2, 1]
    insert_begin_constant(head, 3)
    assert to_list(head) == [3, 2, 1]

test_insert_begin_constant()
```

### Insert at end, the direct way

The same walk as the linear insert-at-beginning, with one difference: `head` is left
alone. The new node is spliced in after the last node, so it becomes the new last
node rather than the new first.

Insert-at-beginning and insert-at-end differ *only* in whether `head` moves - in a
ring there is no other distinction between the two ends.

**Time:** O(n) &nbsp; **Space:** O(1)

```python
def insert_end_linear(head, val):
    new = ListNode(val)
    first = head.next # keep reference to first node for wraparound check
    if not first: # empty list
        new.next = new # make circular
        head.next = new # update head to new node
    else:
        curr = first.next
        while curr.next is not first: # find the last node
            curr = curr.next
        # insert new node after the last
        new.next = curr.next # link new node to the last node
        curr.next = new


def test_insert_end_linear():
    head = ListNode(-1)
    insert_end_linear(head, 1)
    assert to_list(head) == [1]
    insert_end_linear(head, 2)
    assert to_list(head) == [1, 2]
    insert_end_linear(head, 3)
    assert to_list(head) == [1, 2, 3]

test_insert_end_linear()
```

### Insert at end in O(1)

The same two assignments as the O(1) insert at the beginning, plus one move of the
label. After the swap the new value sits in the first node and the old first value
sits in the second. Point `head` at that second node and reading now starts there,
which leaves the node holding the new value sitting just before the label - and
just before the label is last.

```
after link and swap      [9] → [1] → [2] → [3] → back to 9    9 reads first
then head.next = second  [1] → [2] → [3] → [9] → back to 1    9 reads last
```

Those two lines are the same ring. Not one pointer between nodes differs; only
`head` changed. This is the card in its sharpest form - a ring has no ends of its
own, so which node is last is a decision rather than a fact, and both O(1)
variants are just that decision being made differently.

**Time:** O(1) &nbsp; **Space:** O(1)

```python
def insert_end_constant(head, val):
    # neat trick, insert new node at second place, swap data with head and new node becomes head
    new = ListNode(val)
    first = head.next # keep reference to first node for wraparound check
    if not first: # empty list
        new.next = new # make circular
        head.next = new # update head to new node
    else:
        # add new node after first node
        new.next = first.next
        first.next = new
        new.val, first.val = first.val, new.val # swap data
        head.next = new # update head to new node


def test_insert_end_constant():
    head = ListNode(-1)
    insert_end_constant(head, 1)
    assert to_list(head) == [1]
    insert_end_constant(head, 2)
    assert to_list(head) == [1, 2]
    insert_end_constant(head, 3)
    assert to_list(head) == [1, 2, 3]

test_insert_end_constant()
```
