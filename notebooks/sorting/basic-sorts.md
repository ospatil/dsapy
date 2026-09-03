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

# Basic Sorting Algorithms

## Sorting Algorithm Properties

- **In-place:** Uses O(1) extra space
- **Stable:** Maintains relative order of equal elements
- **Adaptive:** Performs better on partially sorted arrays

## Comparison of Basic Sorts

| Algorithm | Time Complexity | Space | Stable | In-place |
|-----------|----------------|-------|--------|----------|
| Bubble Sort | O(n²) | O(1) | Yes | Yes |
| Selection Sort | Θ(n²) | O(1) | No | Yes |
| Insertion Sort | O(n²), Ω(n) | O(1) | Yes | Yes |

> **Mental model.** All three cost O(n²) for the same reason: each element ends up compared
> against many others, and n elements times roughly n comparisons each is n². What separates
> them is what they *do* with a comparison. Bubble sort swaps the pair on the spot, so a
> value crawls towards its place one slot at a time. Selection sort refuses to move anything
> until it has scanned the whole unsorted remainder and knows the true minimum, then puts it
> straight where it belongs. Insertion sort compares only until it meets something smaller,
> and stops there.
>
> **Load-bearing:** that "stops there". Insertion sort is the only one of the three that is
> genuinely fast on nearly-sorted input, because a value that is already close to its place
> stops after one or two comparisons - Θ(n) for the whole array. Bubble sort's `swapped` flag
> only spots an array that is *already* sorted and does nothing for one that is merely close,
> and selection sort has no fast case at all, since the scan always covers the entire
> remainder. That is why real library sorts, Timsort included, fall back to insertion sort on
> short runs rather than to either of the other two.


# Bubble Sort

Compare each adjacent pair and swap when they are out of order. One pass over the array
drags the largest remaining element all the way to the right - it "bubbles" up - so after
pass i the last i elements are final and the next pass can stop i short.

The `swapped` flag is what makes the best case O(n): a pass with no swaps proves the array
is already sorted, so there is no point continuing.

**Time:** O(n²), Ω(n) on already-sorted input &nbsp; **Space:** O(1) - in-place, stable

**Recipe**

1. Outer pass `i` from `0` to `n - 2`. After pass `i` the largest `i + 1`
   elements are parked at the end for good.
2. Inner loop `j` over `range(n - i - 1)`. **The `- i` is the point of the whole
   thing: the tail is already final, so re-scanning it is the difference between
   this and a pure quadratic.**
3. Compare neighbours, `l[j] > l[j + 1]`, and swap.
4. Set `swapped = True` inside the `if`, and reset it at the top of every outer
   pass.
5. A pass that swapped nothing means sorted, so return. **This flag is the only
   reason bubble sort is O(n) on already-sorted input. Drop it and the best case
   becomes the worst case.**

```python
def bubble_sort(l):
    n = len(l)
    for i in range(n - 1):
        swapped = False
        for j in range(n - i - 1):
            if l[j] > l[j + 1]:
                l[j], l[j + 1] = l[j + 1], l[j]
                swapped = True
        if not swapped:
            return

def test_bubble_sort():
    l = [6, 4, 8, 3, 10]
    bubble_sort(l)
    assert l == [3, 4, 6, 8, 10]

    # Test already sorted
    l = [1, 2, 3, 4, 5]
    bubble_sort(l)
    assert l == [1, 2, 3, 4, 5]

test_bubble_sort()
```

# Selection Sort

Scan the unsorted remainder for the smallest element and swap it into place. After i
rounds the first i positions hold the i smallest values, permanently.

Two consequences of *scanning* rather than *swapping neighbours*:

- The scan always covers the whole remainder, so there is no early exit and no adaptive
  best case - Θ(n²) even on sorted input, unlike bubble and insertion sort
- It performs only O(n) swaps total, which is why it is the choice when writes are
  expensive (flash memory, for instance)

The long-distance swap is also what breaks stability: it can jump an element past an equal
one.

**Time:** Θ(n²) always &nbsp; **Space:** O(1) - in-place, not stable

**Recipe**

1. Outer `i` from `0` to `n - 2`, marking the slot to fill.
2. `min_idx = i`, then scan `j` from `i + 1` to the end for anything smaller.
3. Track the **index**, not the value. You have to swap with it later, and a
   value cannot tell you where it lives.
4. Swap `l[i]` with `l[min_idx]` once, after the scan.
5. **No early exit exists here.** Unlike bubble sort, a sorted array still costs
   a full scan per slot, because nothing is learned until the scan finishes.

```python
def selection_sort(l):
    n = len(l)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if l[j] < l[min_idx]:
                min_idx = j
        l[i], l[min_idx] = l[min_idx], l[i]

def test_selection_sort():
    l = [6, 4, 8, 3, 10]
    selection_sort(l)
    assert l == [3, 4, 6, 8, 10]

    # Test reverse sorted
    l = [5, 4, 3, 2, 1]
    selection_sort(l)
    assert l == [1, 2, 3, 4, 5]

test_selection_sort()
```

# Insertion Sort

Think of sorting a hand of cards. The left part of the array is the sorted hand; take the
next card and slide it left past every card larger than it, then drop it in.

The inner loop **shifts** rather than swaps: `l[j + 1] = l[j]` opens a gap one slot at a
time, and the held value `x` is written once at the end.

```
[6, 4, 8, 3, 10]      | marks the sorted boundary

6 | 4 8 3 10     take 4: 6>4, shift → 4 6 | 8 3 10
4 6 | 8 3 10     take 8: 6<8, stops immediately → 4 6 8 | 3 10
4 6 8 | 3 10     take 3: shifts past 8, 6, 4 → 3 4 6 8 | 10
3 4 6 8 | 10     take 10: stops immediately → done
```

Because the loop stops at the first smaller element, nearly-sorted input costs almost
nothing - Θ(n) in the best case. That adaptiveness is why Timsort (Python's `sorted`)
uses insertion sort on small runs.

**Time:** Θ(n²) worst, Θ(n) best &nbsp; **Space:** O(1) - in-place, stable, adaptive

**Recipe**

1. `i` from `1`, not `0`. A one-element prefix is already sorted, so there is
   nothing to do at `0`.
2. Save `x = l[i]` first. **The shifting loop overwrites `l[i]`, so the value has
   to be out of the array before the hole opens.**
3. `j = i - 1`, then while `j >= 0 and x < l[j]`, copy `l[j]` up to `l[j + 1]`
   and step `j` back. This shifts, it does not swap: one write per element
   instead of three.
4. **`j >= 0` has to come first in the `and`.** Python does not raise on `l[-1]`,
   it wraps to the last element, so a missing guard corrupts data quietly
   instead of crashing.
5. Drop `x` into `l[j + 1]`. **`j + 1`, because the loop exits one slot past
   where `x` belongs, having stepped `j` back once too far.**

```python
def insertion_sort(l):
    for i in range(1, len(l)):
        x = l[i]
        j = i - 1
        while j >= 0 and x < l[j]:
            l[j + 1] = l[j]
            j -= 1
        l[j + 1] = x

def test_insertion_sort():
    l = [6, 4, 8, 3, 10]
    insertion_sort(l)
    assert l == [3, 4, 6, 8, 10]

    # Test single element
    l = [42]
    insertion_sort(l)
    assert l == [42]

    # Test empty list
    l = []
    insertion_sort(l)
    assert l == []

test_insertion_sort()
```

# Python Built-in: `sorted()` and `list.sort()`

Python uses **Timsort** - a hybrid of merge sort + insertion sort.

| Function | Returns | In-place | Stable |
|----------|---------|----------|--------|
| `sorted(iterable)` | New list | No | Yes |
| `list.sort()` | None | Yes | Yes |

**Time complexity:** O(n log n) worst case, O(n) on nearly sorted data (adaptive).

Timsort exploits existing order in data - it finds natural "runs" (already sorted subsequences),
extends them with insertion sort, then merges them. This is why both merge sort and insertion sort
are covered above - Timsort combines the best of both.

```python
# sorted() returns a new list, works on any iterable
print(sorted([6, 4, 8, 3, 10]))           # [3, 4, 6, 8, 10]
print(sorted([6, 4, 8, 3, 10], reverse=True))  # [10, 8, 6, 4, 3]

# list.sort() sorts in-place, returns None
l = [6, 4, 8, 3, 10]
l.sort()
print(l)  # [3, 4, 6, 8, 10]

# key parameter - sort by custom criteria
words = ['banana', 'pie', 'Washington', 'book']
print(sorted(words, key=len))              # ['pie', 'book', 'banana', 'Washington']

# stable sort - equal elements maintain original order
pairs = [(1, 'b'), (2, 'a'), (1, 'a'), (2, 'b')]
print(sorted(pairs, key=lambda x: x[0]))   # [(1, 'b'), (1, 'a'), (2, 'a'), (2, 'b')]
```
