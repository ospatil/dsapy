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

# Stacks and Queues

## Stack

**LIFO** - Last In, First Out

| Operation | Description | Time |
|-----------|-------------|------|
| push(x) | Add to top | O(1) |
| pop() | Remove from top | O(1) |
| peek/top() | View top element | O(1) |
| is_empty() | Check if empty | O(1) |

**Applications:** Function call stack, undo operations, expression evaluation, balanced parentheses, DFS.

## Queue

**FIFO** - First In, First Out

| Operation | Description | Time |
|-----------|-------------|------|
| enqueue(x) | Add to rear | O(1) |
| dequeue() | Remove from front | O(1) |
| front() | View front element | O(1) |
| is_empty() | Check if empty | O(1) |

**Applications:** BFS, scheduling, buffering, producer-consumer.

> **Mental model.** One question separates the two: which end do you take from? Take from the
> same end you added to and the newest item leaves first - that is a stack, LIFO. Take from the
> other end and the oldest leaves first - that is a queue, FIFO. Every use case follows from
> that one choice. Undo, bracket matching and DFS all need the most recent thing back;
> scheduling, buffering and BFS all need the one that has waited longest.
>
> **Load-bearing:** where those ends sit in memory. For a Python `list`, push and pop must both
> happen at the *end*, because inserting or removing at index 0 shifts every remaining element
> and quietly turns O(1) into O(n). A queue needs two opposite ends, so it either walks indices
> through a fixed array (the circular queue below) or uses `deque`, which exists precisely to
> be O(1) at both ends.


## Stack using Array (list)

A stack needs push and pop at the *same* end, and for a Python `list` that end must be the
**right** one: `append` and `pop()` are O(1) amortized because they touch only the tail,
while `insert(0, x)` and `pop(0)` shift every element and cost O(n).

So `items[-1]` is the top, and the whole structure is a list plus a naming convention. The
value the class adds is the guard rails - popping or peeking an empty stack raises a clear
error instead of returning garbage or an `IndexError` from deep inside.

**Time:** O(1) amortized for every operation &nbsp; **Space:** O(n)

**Recipe**

1. Back the stack with a plain `list` holding the **values** themselves. There is
   no second index to maintain: the list's own right end *is* the top.
2. `push` is `append`; `pop` is `items.pop()` **with no argument**, which defaults
   to the last index; `peek` is `items[-1]`, the same read without the removal.
3. **Everything depends on using the *end* of the list.** Python's list is a
   dynamic array: appending and popping at the end are amortized O(1), while the
   same operations at index `0` are O(n) because every other element shifts. A
   stack built on `insert(0, x)` and `pop(0)` is correct and quadratic.
4. `pop` and `peek` check `is_empty()` **before** touching the list, and raise
   rather than returning `None`, so an empty stack cannot be mistaken for one
   holding `None`. **Skip the guard and `items[-1]` raises `IndexError` from
   inside the list**, blaming the wrong line.
5. `is_empty` and `size` both read `len(self.items)`. **Keep no separate counter**
   - a length that is stored twice is a length that can disagree with itself.

```python
class Stack:
    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append(x)

    def pop(self):
        if self.is_empty():
            raise IndexError('pop from empty stack')
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError('peek from empty stack')
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

def test_stack():
    s = Stack()
    assert s.is_empty()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.items[-1] == 3      # the top is the right end of the list
    assert s.peek() == 3
    assert s.pop() == 3
    assert s.pop() == 2
    assert s.size() == 1
    assert s.pop() == 1
    assert s.is_empty()
    # the guards fire, rather than an IndexError leaking out of the list
    for op in ('pop', 'peek'):
        try:
            getattr(Stack(), op)()
        except IndexError:
            pass
        else:
            raise AssertionError(f'{op} on an empty stack must raise')

test_stack()
```

## Queue using Array (list)

A queue removes from the *opposite* end from where it adds, which is exactly what a list is
bad at: `pop(0)` shifts all n elements left.

The fix is to stop moving the data and move the **indices** instead. Keep `front` and
`size`; the rear is wherever `(front + size) % cap` lands. Both ends then wander rightwards
through a fixed array and wrap around at the end - hence *circular* queue.

Be exact about what each end means, because one is stored and the other is computed.
`front` is the index of the **oldest** live element - the one the next `dequeue`
returns, and the one `peek` reads. The derived rear is **one past the newest**: an empty
slot, the one the next `enqueue` writes into. So the queue's live elements are the `size`
slots starting at `front` and walking rightwards with wraparound.

```
cap = 3.  arr is shown by index, left to right.  `_` is a slot never written;
`(x)` is a stale slot - dequeued, so no longer part of the queue, but never
cleared, because dequeue only moves `front`.

                      arr               front  size    live, oldest first
start                 [_, _, _]         0      0       -
enqueue 1, 2, 3       [1, 2, 3]         0      3       1 2 3     full: size == cap
dequeue -> 1          [(1), 2, 3]       1      2       2 3
enqueue 4             [4, 2, 3]         1      3       2 3 4     full again; wrote (1+2) % 3 = 0
dequeue -> 2          [4, (2), 3]       2      2       3 4
dequeue -> 3          [4, (2), (3)]     0      1       4         front wrapped 2 -> 0
dequeue -> 4          [(4), (2), (3)]   1      0       -         empty: size == 0
```

`size` is what distinguishes full from empty - both leave `front` and the computed rear
pointing at the same slot. The trace lands on index 1 twice for that reason. After
`enqueue 4` the queue is full with `front = 1`, and the rear derived from the *new*
`size` is `(1 + 3) % 3 = 1`; at the last row the queue is empty with `front = 1` and the
rear is `(1 + 0) % 3 = 1`. A lone pair of indices cannot tell those two states apart.
(The `% 3 = 0` noted on the `enqueue 4` row is the slot that enqueue *wrote*, derived
before `size` was bumped - a different moment, and the reason step 3 below insists on the
order.)

**Time:** O(1) for every operation &nbsp; **Space:** O(capacity), fixed up front

**Recipe**

1. Store `arr`, `cap`, `front`, and `size`. **Store the size, not the rear.**
2. Derive the rear when you need it: `rear = (front + size) % cap`.
3. `enqueue`: raise if `size == cap`, write at the derived `rear`, then `size +=
   1`. **Derive the rear before the increment** - bump `size` first and you write
   one slot too far, overwriting nothing and losing the element.
4. `dequeue`: raise if empty, read `arr[front]` into a temporary, advance `front =
   (front + 1) % cap`, `size -= 1`, then return the temporary. **Read before
   advancing** - once `front` moves the value is unreachable. `peek` is that same
   read with neither index touched.
5. **The `% cap` belongs on every index move**, in both methods - miss one and
   the queue silently stops wrapping.
6. **`is_empty` tests `size == 0`, never `front == rear`.** Full and empty both
   leave those two equal - both land on index 1 in the trace above - so comparing
   them reports an empty queue when it is actually full. Storing `size` is what
   buys the distinction, so spend it here.

```python
class Queue:
    """Circular queue using a fixed-size array. All operations O(1)."""
    def __init__(self, capacity):
        self.arr = [None] * capacity
        self.cap = capacity
        self.front = self.size = 0

    def enqueue(self, x):
        if self.size == self.cap:
            raise OverflowError('queue is full')
        rear = (self.front + self.size) % self.cap
        self.arr[rear] = x
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError('dequeue from empty queue')
        val = self.arr[self.front]
        self.front = (self.front + 1) % self.cap
        self.size -= 1
        return val

    def peek(self):
        if self.is_empty():
            raise IndexError('peek from empty queue')
        return self.arr[self.front]

    def is_empty(self):
        return self.size == 0

def test_queue():
    q = Queue(3)
    assert q.is_empty()
    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)
    assert q.peek() == 1         # the front holds the oldest element
    assert q.dequeue() == 1
    assert q.arr[0] == 1         # dequeue moved front only; the slot is stale
    q.enqueue(4)  # wraps around
    assert q.dequeue() == 2
    assert q.dequeue() == 3
    assert q.dequeue() == 4
    assert q.is_empty()
    # full and empty both put front and the derived rear on the same slot,
    # so only size can tell them apart
    full = Queue(3)
    for x in (7, 8, 9):
        full.enqueue(x)
    assert full.front == (full.front + full.size) % full.cap
    assert q.front == (q.front + q.size) % q.cap
    assert q.is_empty() and not full.is_empty()

test_queue()
```

## Classic Problem: Balanced Parentheses

The problem that most obviously *is* a stack. Nesting means the bracket that must close
first is the one that opened most recently - last in, first out.

So push every opener; on a closer, the top of the stack has to be its partner. If it isn't,
the brackets interleave rather than nest. The `pairs` dict maps each closer to the opener it
requires, which turns matching into a single lookup.

This stack holds **characters** - the opener itself - not indices, because the answer is a
single yes or no and nothing has to be located afterwards. The top is `stack[-1]`, the right
end of the list, and it means "the bracket opened most recently and still unclosed". A
matching pop is safe because it settles that pair for good: everything opened after it has
already closed, so nothing left to read can refer to it.

```
'({[]})'          stack shown bottom to top, top on the right

(     (               push
{     ( {             push
[     ( { [           push
]     ( {             top was [ - matches ] - pop
}     (               top was { - matches } - pop
)     empty           top was ( - matches ) - pop
end   empty -> balanced

'([)]'
(     (
[     ( [
)     top is [ but ) needs ( -> mismatch -> False
```

Two failure modes, and both need checking: a closer that meets the wrong top (or an empty
stack), and leftover openers at the end - which is why the return value is
`len(stack) == 0` rather than just `True`.

**Time:** O(n) &nbsp; **Space:** O(n) - all openers, e.g. `'((((('`

**Recipe**

1. Map **closer to opener**, `{')': '(', ']': '[', '}': '{'}`. That direction is
   deliberate: the lookup happens when a closer is read.
2. Opener: push it.
3. Closer: fail if the stack is empty, or if the top is not `pairs[ch]`.
   Otherwise pop.
4. **Both halves of that test are needed, and they fail differently.** Drop the
   match check and `"([)]"` is *accepted* - a silently wrong answer. Drop the empty
   check and `")("` raises `IndexError` out of `stack[-1]` instead of returning
   `False`. Neither omission is survivable, but only the first one is quiet.
5. **Check `not stack` first.** Reversing the `or` reads `stack[-1]` on an empty
   list and raises.
6. Return `len(stack) == 0`, not `True`. **`"(("` never fails a check and is
   caught only here.**

```python
def is_balanced(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return len(stack) == 0

def test_balanced():
    assert is_balanced('({[]})')
    assert is_balanced('()()')
    assert not (is_balanced('([)]'))
    assert not (is_balanced('(('))
    assert is_balanced('')

test_balanced()
```

## Python Built-in: `collections.deque`

> **Procedural vs class-based:** The `Stack` and `Queue` classes above follow the conventional OOP teaching approach. In practice (and in interviews), you rarely need a wrapper class - Python's `list` already *is* a stack (`append`/`pop`), and `collections.deque` already *is* a queue (`append`/`popleft`). The procedural approach is shown below.

`deque` serves as both stack and queue with O(1) operations on both ends. Its right end is
`append`/`pop` and its left end is `appendleft`/`popleft`, so the only thing to decide is
which end you take from: a stack pushes and pops at the **right**, while a queue appends at
the right (the rear) and takes from the **left** (the front, `deque[0]`).

| Use as | Push | Pop |
|--------|------|-----|
| Stack | `append(x)` | `pop()` |
| Queue | `append(x)` | `popleft()` |

**Why not `list` for queues?** `list.pop(0)` is O(n) - it shifts every element left.
`deque.popleft()` is O(1).

```python
from collections import deque

# deque as stack (LIFO)
stack = deque()
stack.append(1)
stack.append(2)
stack.append(3)
print(stack.pop())    # 3
print(stack.pop())    # 2

# deque as queue (FIFO)
queue = deque()
queue.append(1)       # enqueue
queue.append(2)
queue.append(3)
print(queue.popleft()) # 1 - dequeue, O(1)
print(queue.popleft()) # 2

# compare: list.pop(0) is O(n)
# For small n it doesn't matter, but for large n deque is significantly faster
```
