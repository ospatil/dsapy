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

# Singly Linked List

A chain of nodes, each holding a value and one `next` pointer. The list is
identified by its head, so there is no random access - reaching position i
costs O(i).

| Operation | Time |
|---|---|
| Insert / delete at front | O(1) |
| Insert / delete at end | O(n) - no tail pointer |
| Search | O(n) |
| Access by position | O(n) |
| Reverse | O(n) |

**Space:** O(n), with one extra pointer of overhead per node.
> **Mental model.** A chain you can only walk forwards, one node at a time. Every
> operation comes down to parking a pointer on the node *before* the spot you want to
> change, then rewiring - which is the whole reason for the dummy head: it guarantees
> that "node before" always exists, even in an empty list, so no operation needs a
> special case for the front.
>
> **Load-bearing:** you cannot step backwards. Anything that needs the node before the
> target pays a walk to find it - that alone is why `delete_last` is O(n) while
> `delete_first` is O(1) - and any pointer you are about to overwrite must be saved
> first, or the rest of the list becomes unreachable.

```python
class ListNode:
    def __init__(self, val=0):
        self.val = val
        self.next = None

def to_list(head):
    ls = []
    curr = head.next
    while curr:
        ls.append(curr.val)
        curr = curr.next
    return ls
```

We'll use a **dummy head** for all the functions: a node that holds no real data and never
moves, sitting in front of the first real node. Its value is irrelevant - the code below uses
`-1` - because nothing ever reads it; only its `next` pointer matters. It exists so that
"insert at the front" and "delete the first node" are ordinary pointer updates instead of
special cases, since there is always a node in front of the one being changed. That is also why
`to_list` starts at `head.next` rather than `head`.

> **Procedural vs class-based:** The functions below take a `head` node and operate on it directly - a procedural style closer to how you'd write it in an interview or in C. These can also be organized as a `LinkedList` class with methods like `insert_front()`, `delete()`, etc. The class approach is the conventional OOP teaching style but the underlying logic is identical.


## Insert at front

Decide the finished shape before writing anything: `dummy -> new -> old first -> ...`.
Two arrows differ from the current shape, and the pointer that has to be *read* to build
one of them, `head.next`, is the same pointer the other one *overwrites*. That collision
is the whole content of this function.

The way out is to write into the arrow nothing else depends on yet. `new.next` is
uninitialised, so it can take the copy for free; the instant it holds that copy there are
two routes into the old first node and `head.next` is safe to clobber. There is no cursor
here at all, and no empty-list branch either, because the dummy is a real node whether or
not anything follows it.

**Time:** O(1) &nbsp; **Space:** O(1)

**Recipe**

1. `new = ListNode(val)`.
2. `new.next = head.next` **first**, then `head.next = new`.
3. **Reversed, `new.next = head.next` reads the pointer it has just overwritten**, so
   `new` points at itself and every real node becomes unreachable.
4. No guard. On an empty list `head.next` is `None`, and `None` is exactly the right
   `next` for the only node in a one-element list.

```python
def insert_front(head, val):
    new = ListNode(val)
    new.next = head.next
    head.next = new

def test_insert_front():
    head = ListNode(-1) # dummy head
    insert_front(head, 3)
    insert_front(head, 2)
    insert_front(head, 1)
    ls = to_list(head)
    assert ls == [1, 2, 3]

test_insert_front()
```

## Insert at end

The target shape is `... -> old tail -> new -> None`, so the pointer that changes belongs
to the tail. Nothing in a singly linked list points at the tail, so it has to be found
first, and that search is the entire O(n) - the splice after it is one assignment.

`curr` is the node the walk currently takes to be the tail, and `curr.next` is the
disproof: a node with a successor was never the tail, so step onto the successor and
believe that instead. Starting that belief on the dummy is what erases the empty-list
case, since with no real nodes the dummy is never disproved and is itself the node to
attach to.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. Create the node, then start `curr` at the **dummy**, not at `head.next`.
2. Walk while `curr.next` is truthy, so `curr` finishes on the last real node.
   **The test is `curr.next`, not `curr`. Stopping on `curr is None` walks off
   the end and leaves nothing to attach to.**
3. `curr.next = new`. `new.next` is already `None`, which is what a tail needs.
4. No guard: the empty list is just the run where `curr` never moves.

```python
def insert_end(head, val):
    new = ListNode(val)
    curr = head
    while curr.next: # traverse to the last node
        curr = curr.next
    curr.next = new


def test_insert_end():
    head = ListNode(-1) # dummy head
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    ls = to_list(head)
    assert ls == [1, 2, 3]

test_insert_end()
```

## Delete first

The dummy head holds the pointer to the first real node, so deleting it is one pointer
hop - `head.next = head.next.next` - with no traversal and no special case beyond the
empty list, which the `if head.next` guard covers.

**Time:** O(1) &nbsp; **Space:** O(1)

**Recipe**

1. Guard the empty list, then `head.next = head.next.next`.
2. **The guard is not decoration**: `head.next.next` on an empty list reads a
   field off `None`.
3. Returns nothing, and on an empty list it is a silent no-op rather than an
   error - the caller cannot tell whether anything was removed.
4. Nothing frees the skipped node explicitly; once nothing points at it Python
   collects it.

```python
def delete_first(head):
    if head.next:
        head.next = head.next.next


def test_delete_first():
    head = ListNode(-1) # dummy head
    # add three nodes
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    # delete first two
    delete_first(head)
    delete_first(head)
    ls = to_list(head)
    assert ls == [3]

test_delete_first()
```

## Delete last

The target shape is `... -> second-to-last -> None`, so the pointer that changes belongs
to the second-to-last node. That is the general shape of every deletion here: the node
being removed is never the node being edited, its predecessor is, and a singly linked list
cannot step backwards to reach one. So the predecessor is found by walking, and `curr` is
the node the walk currently takes to be it.

`curr.next.next` is the disproof this time, one link further ahead than `insert_end` needs,
because the walk has to stop one node earlier. That extra dereference is also what forces
the guard: on an empty list the dummy's `next` is `None` and `curr.next.next` reads a field
off it.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. Empty list, `head.next is None`, return. **This guard has to come first**, or
   the loop reads `curr.next.next` on `None` and raises.
2. Start `curr` at the dummy.
3. Walk while **`curr.next.next`** is truthy, which parks `curr` on the
   *second-to-last* node.
4. `curr.next = None`.
5. A one-element list needs no branch of its own: the loop never runs, `curr` is
   still the dummy, and the dummy's `next` is exactly the pointer to clear.

```python
def delete_last(head):
    if head.next is None: # empty list, nothing to drop
        return
    curr = head
    # we need to stop at second-last node, therefore curr.next.next check
    while curr.next.next:
        curr = curr.next
    curr.next = None


def test_delete_last():
    head = ListNode(-1) # dummy head

    # test deletion for empty list
    delete_last(head)
    assert head.next is None

    # test deletion for list with one element
    insert_end(head, 1)
    delete_last(head)
    assert head.next is None

    # test deletion for list with multiple elements
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    # delete last two
    delete_last(head)
    delete_last(head)
    ls = to_list(head)
    assert ls == [1]

test_delete_last()
```

## Insert at position

This is the card's rule in its general form: to change position `p` you need the node at
`p-1`, and since you cannot step backwards you have to walk there first. That single
constraint explains the whole function - the loop exists only to park `curr` on the node
before the gap, which takes `p-1` steps from the dummy.

Splicing is then two assignments, and their order is the same trap as `insert_front`:

```
new.next  = curr.next     first: the new node adopts the rest of the list
curr.next = new           then:  the list lets go of it
```

Do it the other way round and `curr.next` is overwritten before anything else points at
the tail, so everything after the insertion point is unreachable.

Positions are 1-based, and the dummy head is what makes position 1 need no special case:
`p-1 = 0` steps leaves `curr` on the dummy, which is a real node to splice after. If `p`
runs past the end, the loop stops early on `curr.next is None` and the node lands at the
tail instead of failing.

**Time:** O(p) &nbsp; **Space:** O(1)

**Recipe**

1. Positions are 1-based, and `curr` starts on the dummy.
2. Move `position - 1` times. **Counting from the dummy is what makes that
   arithmetic work**: to insert at position 4 you must be holding node 3, three
   steps along.
3. Inside the loop, break early if `curr.next is None`.
4. Then the same two lines as `insert_front`, in the same order: `new.next =
   curr.next`, `curr.next = new`.

```python
# Position is 1 based
def insert_at(head, val, position):
    new = ListNode(val)
    curr = head
    # consider the following list: Dummy -> 1 -> 2 -> 3 -> 4
    # when we start curr is at position "Dummy"
    # so to add to 4th position, we need to point to 3rd and curr needs to be moved 3 times
    # for pos 3, curr needs to be moved 2 time
    # i.e. (pos - 1) times
    for _ in range(position - 1):
        # the position could be beyond the length of the list, break out so the new node is added at the end
        if curr.next is None:
            break
        curr = curr.next
    new.next = curr.next
    curr.next = new


def test_insert_at():
    head = ListNode(-1) # dummy head

    # test insertion at position 1
    insert_at(head, 1, 1)
    assert head.next.val == 1
    assert head.next.next is None

    # test insertion at position 2
    insert_at(head, 2, 2)
    assert head.next.next.val == 2
    assert head.next.next.next is None

    # test insertion at position 3
    insert_at(head, 3, 3)
    assert head.next.next.next.val == 3
    assert head.next.next.next.next is None

    # test insertion at position 5 (out of range), it should be added to the end
    insert_at(head, 5, 5)
    assert head.next.next.next.next.val == 5
    assert head.next.next.next.next.next is None

    insert_at(head, 100, 1)

    ls = to_list(head)
    assert ls == [100, 1, 2, 3, 5]

test_insert_at()
```

## Search

Walk from the first real node, counting as you go. Return the 1-based position on
a match, -1 if the list runs out. Starting at `head.next` skips the dummy so the
count lines up with the caller's positions.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `pos, curr = 1, head.next` - **both halves encode the 1-based convention**,
   skipping the dummy and starting the count at 1.
2. Walk while `curr`, returning `pos` on a match.
3. Advance `pos` and `curr` **on every iteration, without exception**, or the
   returned position drifts by however many times they disagreed.
4. The loop ended without a match, so return `-1`.

```python
# Return the position of val if found else return -1. Position is 1 based.
def search(head, val):
    pos, curr = 1, head.next
    while curr:
        if curr.val == val:
            return pos
        pos += 1
        curr = curr.next
    return -1


def test_search():
    head = ListNode(-1) # dummy head

    # test search for empty list
    assert search(head, 1) == -1

    # test search for list with one element
    insert_end(head, 1)
    assert search(head, 1) == 1
    assert search(head, 2) == -1

    # test search for list with multiple elements
    insert_end(head, 2)
    insert_end(head, 3)
    insert_end(head, 4)
    assert search(head, 1) == 1
    assert search(head, 2) == 2
    assert search(head, 3) == 3
    assert search(head, 4) == 4
    assert search(head, 5) == -1

    # duplicates: the walk returns on the first match, so the later one is invisible
    insert_end(head, 2)
    assert to_list(head) == [1, 2, 3, 4, 2]
    assert search(head, 2) == 2

test_search()
```

## Sorted insert

The same splice as `insert_at`, but the stopping condition is a comparison instead
of a counter: stop on the last node whose value is still smaller than `val`, then
insert after it.

The comparison is strict (`curr.next.val < val`), so the walk stops at the first
value that is *not* smaller. A duplicate therefore lands in front of the equal
values already there. Switch to `<=` and the walk steps past them instead, which
is what you want when equal keys have to keep their insertion order.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. Start on the dummy and walk while **`curr.next and curr.next.val < val`**.
2. Look at `curr.next.val`, not `curr.val`. You need to stop *before* the first
   node that is too big, since that is the node whose incoming pointer you are
   about to rewrite.
3. **`curr.next` must be tested first in the `and`.** It short-circuits at the
   end of the list; reverse the two and the walk reads `.val` on `None`.
4. **Strict `<` puts a duplicate in front of its equals; `<=` puts it behind.**
   Values alone cannot tell those two apart, so the test below pins it by node
   *identity* instead - which is the only way this claim can fail loudly.
5. Splice with the usual pair, `new.next = curr.next` then `curr.next = new`.

```python
def sorted_insert(head, val):
    new = ListNode(val)
    curr = head
    while curr.next and curr.next.val < val:
        curr = curr.next
    new.next = curr.next
    curr.next = new


def test_sorted_insert():
    head = ListNode(-1) # dummy head

    # test insertion in empty list
    sorted_insert(head, 2)
    assert to_list(head) == [2]

    # test insertion at the end
    sorted_insert(head, 5)
    assert to_list(head) == [2, 5]

    # test insertion at the beginning
    sorted_insert(head, 1)
    assert to_list(head) == [1, 2, 5]

    # test insertion in the middle
    sorted_insert(head, 3)
    assert to_list(head) == [1, 2, 3, 5]

    # test insertion of duplicate
    existing_3 = head.next.next.next  # the node already holding 3
    sorted_insert(head, 3)
    assert to_list(head) == [1, 2, 3, 3, 5]
    # strict < stopped before the equal value, so the new node landed in front of
    # it. With <= the walk would step past and these two asserts would flip.
    assert head.next.next.next is not existing_3
    assert head.next.next.next.next is existing_3


test_sorted_insert()
```

## Reverse using a stack

A stack hands items back in the opposite order to which they arrived: last in, first
out. Reversing is that property used directly - push every value, then pop them back
into the list.

The price is O(n) extra memory, and it builds fresh nodes instead of rewiring the
existing ones. Worth writing once anyway, because the in-place version below is this
same "push onto the front" motion, with the list's own pointers doing the stack's job.

**Time:** O(n) &nbsp; **Space:** O(n)

**Recipe**

1. Walk the list pushing every **value** onto a list used as a stack.
2. Reset `curr` to the dummy.
3. Pop until the stack is empty, and for each popped value create a node and
   link it on: `curr.next = ListNode(stack.pop())`, then advance
   `curr = curr.next`.
4. **No guard, and nothing to terminate by hand.** An empty list pushes nothing,
   so the second loop never runs and `head.next` keeps its `None`; otherwise the
   last node built is fresh, so its `next` is already `None`.
5. **Any reference a caller was holding into the old list still points at the
   discarded nodes**, since every node here is replaced rather than rewired. The
   old chain stays intact and walkable, just detached - which is worse than a
   crash, because it looks like a list.

```python
def reverse_using_stack(head):
    stack = []
    curr = head.next
    while curr:
        stack.append(curr.val)
        curr = curr.next
    curr = head
    while stack:
        curr.next = ListNode(stack.pop())
        curr = curr.next


def test_reverse_using_stack():
    head = ListNode(-1) # dummy head
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    old_first = head.next  # the node holding 1
    reverse_using_stack(head)
    assert to_list(head) == [3, 2, 1]
    # every node was rebuilt, so the caller's old reference is not in the new list
    assert old_first is not head.next.next.next
    assert old_first.val == 1 and old_first.next is not None  # still walkable, detached

    # empty list, and a single element
    head = ListNode(-1)
    reverse_using_stack(head)
    assert to_list(head) == []
    insert_end(head, 7)
    reverse_using_stack(head)
    assert to_list(head) == [7]

    # duplicates survive as duplicates
    head = ListNode(-1)
    for v in (1, 2, 2, 3):
        insert_end(head, v)
    reverse_using_stack(head)
    assert to_list(head) == [3, 2, 2, 1]

test_reverse_using_stack()
```

## Reverse in place

Split the list into two parts and track the boundary between them:

```
1 -> 2 -> 3 -> 4, two iterations in:

     reversed          untouched
     2 -> 1 -> None    3 -> 4 -> None
     ^                 ^
     prev              curr
```

`prev` is the front of the part already flipped; `curr` is the front of the part not yet
touched. Every arrow is a `next` pointer. Left of the boundary they now run backward
through the original order - the list had `1 -> 2`, the prefix has `2 -> 1` - so following
them from `prev` ends at the node that started out as the head. Right of the boundary they
still point forward, untouched.

So `prev` is **not** "the previous node", and reading it that way is what makes this loop
hard to rebuild cold. "Three-pointer technique" undersells it too: there are two *regions*
and one temporary. The temporary is the untouched region *minus the node about to leave it*,
which is why it is called `rest` below - it is what remains to be done once `curr` has
moved across.

Each iteration moves exactly one node across the boundary, from the front of untouched to
the front of reversed. That is a stack push, which is why this and the stack version above
are the same algorithm - except that here the prefix *is* the stack, built out of the very
nodes being moved, and that is what makes it free.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `prev, curr = None, head.next`. **`prev` starts as `None` because the reversed
   prefix is empty, and that `None` becomes the new tail's `next`, terminating
   the list.**
2. Loop while `curr`.
3. `rest = curr.next` before anything else. **The following line overwrites
   `curr.next`, which is the only route into the untouched suffix.**
4. `curr.next = prev` moves one node across the boundary.
5. Advance the pair, `prev = curr` then `curr = rest`. **In that order. Assign
   `curr` first and `prev = curr` copies the new value, losing the prefix.**
6. Loop ends with `curr is None`, so the suffix is empty and `prev` is the head
   of the whole reversed list. Attach it to the dummy: `head.next = prev`.
7. Empty list: the loop never runs, `prev` is still `None`, and `head.next = None`
   is correct rather than an accident.

```python
def reverse(head):
    # two regions, prev and curr, plus one temporary: rest
    prev, curr = None, head.next
    while curr:
        rest = curr.next # the untouched part, minus the node about to move
        curr.next = prev
        prev = curr # curr joins the reversed prefix, and is now its head
        curr = rest # the untouched region shrinks by one
    head.next = prev


def test_reverse():
    head = ListNode(-1) # dummy head
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    old_first = head.next  # the node holding 1
    reverse(head)
    assert to_list(head) == [3, 2, 1]
    # nodes were rewired, not rebuilt: the old head is the same object, now the tail
    assert head.next.next.next is old_first
    assert old_first.next is None  # prev's starting None became the new terminator

    # empty list, and a single element
    head = ListNode(-1)
    reverse(head)
    assert to_list(head) == []
    insert_end(head, 7)
    reverse(head)
    assert to_list(head) == [7]

    # duplicates survive as duplicates
    head = ListNode(-1)
    for v in (1, 2, 2, 3):
        insert_end(head, v)
    reverse(head)
    assert to_list(head) == [3, 2, 2, 1]

test_reverse()
```

## Reverse recursively

The same two regions, except `prev` and `curr` travel as arguments instead of being
reassigned: each call moves one node across the boundary and hands the new boundary to
the next call. The base case is the empty suffix, and what it returns is the reversed
prefix - `prev`, which by then is the last node of the original list.

It does the same work as the loop, it just costs more: one stack frame per node, because
Python keeps every call alive even when that call is the last thing the function does.

**Time:** O(n) &nbsp; **Space:** O(n) - one frame per node

**Recipe**

1. Base case is the empty **suffix**, `curr is None`: **return `prev`, not `curr`**.
   `curr` is `None` here, so returning it hands back an empty list.
2. **Say "empty suffix", never "empty list".** Phrase the base case as "if the list
   is empty, return `None`" and a one-element list breaks: the single node is
   `curr` on the first call, not `None`, and the frame that finally sees `None` is
   the one holding that node in `prev`.
3. Save `rest = curr.next` before anything else, exactly as the loop does.
4. `curr.next = prev` moves one node across the boundary.
5. Recurse with `(curr, rest)`, the new prefix head and the new suffix head, and
   return what it returns unchanged. Nothing happens on the way back up, which is
   what makes the recursion pure plumbing here.
6. The outer function returns nothing. It starts the walk past the dummy and
   assigns the returned head back:
   `head.next = reverse_recursive_util(None, head.next)`.

```python
def reverse_recursive(head):
    # the idea is we reverse the first link and then make recursive call to reverse next link
    def reverse_recursive_util(prev, curr):
        if curr is None:
            # base case: the untouched suffix is empty, so prev is the head of the
            # fully reversed prefix - the node that used to be last
            return prev
        rest = curr.next # the untouched part, minus the node about to move
        curr.next = prev # reverse the link
        return reverse_recursive_util(curr, rest)

    head.next = reverse_recursive_util(None, head.next)


def test_reverse_recursive():
    head = ListNode(-1) # dummy head
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    old_first = head.next  # the node holding 1
    reverse_recursive(head)
    assert to_list(head) == [3, 2, 1]
    assert head.next.next.next is old_first  # rewired, not rebuilt
    assert old_first.next is None

    # empty list: the base case fires on the very first call and returns None
    head = ListNode(-1)
    reverse_recursive(head)
    assert to_list(head) == []

    # single element: the case that catches a base case phrased as "empty list"
    insert_end(head, 7)
    reverse_recursive(head)
    assert to_list(head) == [7]
    assert head.next.next is None

    # duplicates survive as duplicates
    head = ListNode(-1)
    for v in (1, 2, 2, 3):
        insert_end(head, v)
    reverse_recursive(head)
    assert to_list(head) == [3, 2, 2, 1]

test_reverse_recursive()
```

## Python Built-in Note

Python has **no built-in singly linked list**. This is by design - Python's `list` is a dynamic array with O(1) random access, which is more versatile.

The closest built-in is `collections.deque` (a doubly-linked list of blocks) which gives O(1) append/pop on both ends. See the doubly-linked-list notebook for details.

When to use a linked list over `list`:
- Frequent insertions/deletions in the middle (given a reference to the node)
- When you need O(1) splicing of two lists
- LeetCode/interview problems that explicitly require linked list manipulation
