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


### Insert at front

Point the new node at the old first node, then point the dummy at the new node.
Two assignments, no special case for the empty list - the dummy always exists.

Order matters: overwrite `head.next` first and the rest of the list is lost.

**Time:** O(1) &nbsp; **Space:** O(1)

**Recipe**

1. Create the node: `new = ListNode(val)`.
2. `new.next = head.next` **first**, then `head.next = new`.
3. **That order is the whole cell.** Assign `head.next = new` first and
   `head.next` no longer names the old first node, so the next line points `new`
   at itself and the rest of the list is unreachable.
4. No empty-list case is needed. `head` is the dummy, so `head.next` is `None`
   on an empty list and the same two lines still work.

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

### Insert at end

There is no tail pointer, so the tail has to be found first - that walk is the
whole cost. `curr.next is None` identifies the tail, and on an empty list the
dummy head *is* the last node, so the same code handles it.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. Start `curr` at the **dummy**, not at `head.next`.
2. Walk while `curr.next` is truthy, so `curr` finishes on the last real node.
   **The test is `curr.next`, not `curr`. Stopping on `curr is None` walks off
   the end and leaves nothing to attach to.**
3. `curr.next = new`.
4. Starting at the dummy is what removes the empty-list special case: the loop
   runs zero times and the dummy itself is the node to attach to.

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

### Delete first

The dummy head holds the pointer to the first real node, so deleting it is one pointer
hop - `head.next = head.next.next` - with no traversal and no special case beyond the
empty list, which the `if head.next` guard covers.

**Time:** O(1) &nbsp; **Space:** O(1)

**Recipe**

1. Guard the empty list: nothing to do if `head.next` is `None`.
2. `head.next = head.next.next`, skipping over the first real node.
3. Nothing frees the node explicitly; once nothing points at it Python collects
   it.

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

### Delete last

To drop the last node you need the node *before* it, and a singly linked list cannot step
backwards. So walk while `curr.next.next` exists - that parks `curr` on the second-to-last
node - then cut with `curr.next = None`.

The `head.next is None` guard covers the empty list, where `curr.next.next` would raise.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. Empty list, `head.next is None`, return. **This guard has to come first.
   Without it the loop reads `curr.next.next` on `None` and raises.**
2. Start `curr` at the dummy.
3. Walk while **`curr.next.next`** is truthy, so `curr` stops on the
   *second-to-last* node. Deleting from a singly linked list means editing the
   pointer that points at the node being removed, and only the node before it
   holds that pointer.
4. `curr.next = None`.
5. A one-element list works because `curr` stays on the dummy and the dummy's
   `next` is what gets cleared.

```python
def delete_last(head):
    if head.next is None: # this is an empty list
        return
    else:
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

### Insert at position

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
2. Move `position - 1` times. **Count from the dummy and the arithmetic comes out
   right: to insert at position 4 you must be holding node 3, which is three
   steps from the dummy.**
3. Inside the loop, break early if `curr.next is None`. **This is what turns an
   out-of-range position into "append" instead of a crash.**
4. Then the same two lines as `insert_front`, in the same order: `new.next =
   curr.next`, `curr.next = new`.
5. Position 1 needs no special case, because zero steps leaves `curr` on the
   dummy, which is exactly what `insert_front` uses.

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

### Search

Walk from the first real node, counting as you go. Return the 1-based position on
a match, -1 if the list runs out. Starting at `head.next` skips the dummy so the
count lines up with the caller's positions.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `pos, curr = 1, head.next`. **Both halves of that line encode the 1-based
   convention: skip the dummy, and start the count at 1 rather than 0.**
2. Walk while `curr`, returning `pos` on a match.
3. Advance `pos` and `curr` together. They must move as a pair or the returned
   position is off by the number of times they disagreed.
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

test_search()
```

### Sorted insert

The same splice as `insert_at`, but the stopping condition is a comparison instead
of a counter: stop on the last node whose value is still smaller than `val`, then
insert after it.

The comparison is strict (`curr.next.val < val`), so a duplicate lands *after* the
existing equal values - the insert is stable.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. Start on the dummy and walk while **`curr.next and curr.next.val < val`**.
2. Look at `curr.next.val`, not `curr.val`. You need to stop *before* the first
   node that is too big, since that is the node whose incoming pointer you are
   about to rewrite.
3. **`curr.next` must be tested first in the `and`.** It short-circuits at the
   end of the list; reverse the two and the walk reads `.val` on `None`.
4. **The comparison is strict `<`.** Equal values fail the test, so the walk
   stops before them and a duplicate lands ahead of its equals rather than
   scanning past the whole run.
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
    sorted_insert(head, 3)
    assert to_list(head) == [1, 2, 3, 3, 5]


test_sorted_insert()
```

### Reverse using a stack

Reversing and a stack are the same idea in different clothes: a stack hands things back
in the opposite order to which they arrived. So just do that literally - push every
value, then pop them back into the list.

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
4. **This rebuilds rather than rewires.** Every original node is discarded and
   replaced, so any reference a caller held into the old list now points at
   nodes that are no longer in it. The two versions below reverse the same list
   in place instead.
5. The cost is O(n) for the stack plus O(n) for the new nodes, which is what the
   next cell is written to avoid.

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
    reverse_using_stack(head)
    assert to_list(head) == [3, 2, 1]

test_reverse_using_stack()
```

### Reverse in place

At every moment during the walk, the list is in two pieces:

```
   reversed prefix                 untouched suffix
prev -> ... -> old head -> None    curr -> ... -> None
```

The arrows all mean `next`. In the reversed prefix they now run backwards through the original
order, which is why following them from `prev` ends at the node that used to be the head.

`prev` is not "the previous node" - it is **the head of the part already reversed**, and
`curr` is the head of the part not yet touched. Every line of the loop follows from that
split.

One step moves a single node across the boundary: unhook the first node of the untouched
suffix and push it onto the front of the reversed prefix. That is a stack push - which is
why this and the stack version above are the same algorithm. The difference is that here
the reversed prefix *is* the stack, built out of the very nodes being removed, and that
is what makes it free.

The temporary `next` isn't step one of a recipe, it's the cost of having one hand tied:
`curr.next` is the only route to the rest of the suffix, and pushing `curr` onto the
prefix overwrites it. Save it or lose the list. A doubly linked list needs no temporary
at all, because the suffix stays reachable from the node just moved.

The loop ends when the untouched suffix is empty, which means the whole list is now the
reversed prefix. So `prev` is the new head, and the last line hooks the dummy onto it.

"Three-pointer technique" undersells it: there are two *regions* and one temporary.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `prev, curr = None, head.next`. **`prev` starts as `None` because the reversed
   prefix is empty, and that `None` becomes the new tail's `next`, terminating
   the list.**
2. Loop while `curr`.
3. `next = curr.next` before anything else. **The following line overwrites
   `curr.next`, which is the only route into the untouched suffix.**
4. `curr.next = prev` moves one node across the boundary.
5. Advance the pair, `prev = curr` then `curr = next`. **In that order. Assign
   `curr` first and `prev = curr` copies the new value, losing the prefix.**
6. Loop ends with `curr is None`, so the suffix is empty and `prev` is the head
   of the whole reversed list. Attach it to the dummy: `head.next = prev`.

```python
def reverse(head):
    # three pointers technique: prev, curr, next
    prev, curr = None, head.next
    while curr:
        next = curr.next # store reference to next node
        curr.next = prev
        prev = curr # prev becomes curr
        curr = next # curr becomes next
    head.next = prev


def test_reverse():
    head = ListNode(-1) # dummy head
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    reverse(head)
    assert to_list(head) == [3, 2, 1]

test_reverse()
```

### Reverse recursively

The same two regions, except `prev` and `curr` travel as arguments instead of being
reassigned: each call moves one node across the boundary and hands the new boundary to
the next call. The base case is the empty suffix, and what it returns is the reversed
prefix - `prev`, which by then is the last node of the original list.

It does the same work as the loop, it just costs more: one stack frame per node, because
Python keeps every call alive even when that call is the last thing the function does.

**Time:** O(n) &nbsp; **Space:** O(n) - one frame per node

**Recipe**

1. Base case is the empty suffix, `curr is None`: return `prev`. **Return `prev`,
   not `curr`. `prev` is the part already reversed, and once the suffix is empty
   that is the whole list.**
2. Save `next = curr.next` before anything else. **The next line overwrites
   `curr.next`, and that pointer is the only route into the untouched suffix.**
3. `curr.next = prev` moves one node across the boundary.
4. Recurse with `(curr, next)`, the new prefix head and the new suffix head, and
   return what it returns unchanged. Nothing happens on the way back up.
5. The outer function starts the walk past the dummy and assigns the returned
   head back: `head.next = reverse_recursive_util(None, head.next)`.

```python
def reverse_recursive(head):
    # the idea is we reverse the first link and then make recursive call to reverse next link
    def reverse_recursive_util(prev, curr):
        if curr is None:
            # base case, compare to iterative reverse above. We reached to the end of list and prev points to the last node that is new head
            return prev
        next = curr.next # store reference to next node
        curr.next = prev # reverse the link
        return reverse_recursive_util(curr, next)

    head.next = reverse_recursive_util(None, head.next)


def test_reverse_recursive():
    head = ListNode(-1) # dummy head
    insert_end(head, 1)
    insert_end(head, 2)
    insert_end(head, 3)
    reverse_recursive(head)
    assert to_list(head) == [3, 2, 1]

test_reverse_recursive()
```

# Python Built-in Note

Python has **no built-in singly linked list**. This is by design - Python's `list` is a dynamic array with O(1) random access, which is more versatile.

The closest built-in is `collections.deque` (a doubly-linked list of blocks) which gives O(1) append/pop on both ends. See the doubly-linked-list notebook for details.

When to use a linked list over `list`:
- Frequent insertions/deletions in the middle (given a reference to the node)
- When you need O(1) splicing of two lists
- LeetCode/interview problems that explicitly require linked list manipulation
