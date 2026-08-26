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


# Stack using Array (list)

A stack needs push and pop at the *same* end, and for a Python `list` that end must be the
**right** one: `append` and `pop()` are O(1) amortized because they touch only the tail,
while `insert(0, x)` and `pop(0)` shift every element and cost O(n).

So `items[-1]` is the top, and the whole structure is a list plus a naming convention. The
value the class adds is the guard rails - popping or peeking an empty stack raises a clear
error instead of returning garbage or an `IndexError` from deep inside.

**Time:** O(1) amortized for every operation &nbsp; **Space:** O(n)

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
    assert s.peek() == 3
    assert s.pop() == 3
    assert s.pop() == 2
    assert s.size() == 1
    assert s.pop() == 1
    assert s.is_empty()

test_stack()
```

# Queue using Array (list)

A queue removes from the *opposite* end from where it adds, which is exactly what a list is
bad at: `pop(0)` shifts all n elements left.

The fix is to stop moving the data and move the **indices** instead. Keep `front` and
`size`; the rear is wherever `(front + size) % cap` lands. Both ends then wander rightwards
through a fixed array and wrap around at the end - hence *circular* queue.

```
cap = 3, front = 0, size = 0

enqueue 1, 2, 3      arr [1, 2, 3]   front=0 size=3   (full)
dequeue → 1          arr [_, 2, 3]   front=1 size=2
enqueue 4            rear = (1 + 2) % 3 = 0 → arr [4, 2, 3]   front=1 size=3
dequeue → 2, 3, 4    front walks 2 → 0 → 1, wrapping around
```

`size` is what distinguishes full from empty - both leave `front` and the computed rear
pointing at the same slot, so a lone pair of indices could not tell them apart.

**Time:** O(1) for every operation &nbsp; **Space:** O(capacity), fixed up front

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
    assert q.peek() == 1
    assert q.dequeue() == 1
    q.enqueue(4)  # wraps around
    assert q.dequeue() == 2
    assert q.dequeue() == 3
    assert q.dequeue() == 4
    assert q.is_empty()

test_queue()
```

# Classic Problem: Balanced Parentheses

The problem that most obviously *is* a stack. Nesting means the bracket that must close
first is the one that opened most recently - last in, first out.

So push every opener; on a closer, the top of the stack has to be its partner. If it isn't,
the brackets interleave rather than nest. The `pairs` dict maps each closer to the opener it
requires, which turns matching into a single lookup.

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

# Python Built-in: `collections.deque`

> **Procedural vs class-based:** The `Stack` and `CircularQueue` classes above follow the conventional OOP teaching approach. In practice (and in interviews), you rarely need a wrapper class - Python's `list` already *is* a stack (`append`/`pop`), and `collections.deque` already *is* a queue (`append`/`popleft`). The procedural approach is shown below.

`deque` serves as both stack and queue with O(1) operations on both ends.

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
