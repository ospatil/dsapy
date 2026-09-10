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

| Algorithm | Best | Worst | Space | Stable | In-place |
|-----------|------|-------|-------|--------|----------|
| Bubble Sort | Θ(n) | Θ(n²) | Θ(1) | Yes | Yes |
| Selection Sort | Θ(n²) | Θ(n²) | Θ(1) | No | Yes |
| Insertion Sort | Θ(n) | Θ(n²) | Θ(1) | Yes | Yes |

Two separate questions get tangled in a table like this, so keep them apart. *Which input*
is the best/worst split. *Which kind of bound* is the choice of O, Θ or Ω. Naming the input
answers the second question exactly, which is why every cell above is Θ: on already-sorted
input bubble sort takes Θ(n), not merely O(n). Writing a single entry as "O(n²), Ω(n)" mixes
the axes - it looks like two bounds on one quantity when it is really one bound on each of
two different inputs, and Ω gets read as a synonym for "best case", which it is not.
Selection sort's two columns being identical is the whole story of that algorithm: no input
is a fast one.

> **Mental model.** All three cost Θ(n²) in the worst case for the same reason: each element
> ends up compared against many others, and n elements times roughly n comparisons each is
> n². What separates them is what they *do* with a comparison. Bubble sort swaps the pair on
> the spot, so a value crawls towards its place one slot at a time. Selection sort refuses to
> move anything until it has scanned the whole unsorted remainder and knows the true minimum,
> then puts it straight where it belongs. Insertion sort compares only until it meets
> something smaller, and stops there.
>
> **Load-bearing:** that "stops there". Insertion sort is the only one of the three that is
> genuinely fast on nearly-sorted input, because a value that is already close to its place
> stops after one or two comparisons - Θ(n) for the whole array. Bubble sort's `swapped` flag
> only spots an array that is *already* sorted and does nothing for one that is merely close,
> and selection sort has no fast case at all, since the scan always covers the entire
> remainder. That is why real library sorts, Timsort included, fall back to insertion sort on
> short runs rather than to either of the other two.


## Bubble Sort

Compare each adjacent pair and swap when they are out of order. One pass over the array
drags the largest remaining element all the way to the right - it "bubbles" up - so after
pass i the last i elements are final and the next pass can stop i short.

The `swapped` flag is what makes the best case Θ(n): a pass with no swaps proves the array
is already sorted, so there is no point continuing.

**Time:** Θ(n²) worst, Θ(n) on already-sorted input &nbsp; **Space:** Θ(1) - in-place, stable

**Recipe**

1. Outer pass `i` from `0` to `n - 2`.
2. Inner loop `j` over `range(n - i - 1)` - **the `- i` skips the tail that is
   already final.**
3. Compare neighbours, `l[j] > l[j + 1]`, and swap.
4. Set `swapped = True` inside the `if`, and reset it at the top of every outer
   pass.
5. A pass that swapped nothing means sorted, so return.

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

## Selection Sort

Scan the unsorted remainder for the smallest element and swap it into place. After i
rounds the first i positions hold the i smallest values, permanently.

Two consequences of *scanning* rather than *swapping neighbours*:

- The scan always covers the whole remainder, so there is no early exit and no adaptive
  best case - Θ(n²) even on sorted input, unlike bubble and insertion sort
- It performs exactly n - 1 swaps, one per round, which is why it is the choice when writes
  are expensive (flash memory, for instance). On reverse-sorted input of 20 elements that is
  19 swaps against bubble sort's 190.

The long-distance swap is also what breaks stability. `[1, 1.0, 0]` is the smallest input
that shows it: the minimum `0` sits at the end, so it is swapped into slot `0` and the value
that was there is thrown to the back of the array, behind its own equal twin. The scan is
not at fault - `l[j] < l[min_idx]` is strict, so it keeps the *earliest* of several equal
minima.

That claim needs care to check, because the obvious way to check it is wrong. Equal integers
are indistinguishable, so plain `[1, 1, 0]` cannot show a reorder at all. Tagging them,
`[[1, "a"], [1, "b"], [0, "c"]]`, is worse than useless: list comparison then *sees* the tag,
and that extra comparison quietly repairs the order, so the test passes and proves nothing.
`1` and `1.0` are equal to every comparison the sort makes yet still tell apart in the
output, which is the only reason the assert below is honest.

**Time:** Θ(n²) always &nbsp; **Space:** Θ(1) - in-place, not stable

**Recipe**

1. Outer `i` from `0` to `n - 2`, marking the slot to fill.
2. `min_idx = i`, then scan `j` from `i + 1` to the end for anything smaller.
3. Track the **index**, not the value. You have to swap with it later, and a
   value cannot tell you where it lives.
4. Swap `l[i]` with `l[min_idx]` once, after the scan.
5. **There is no early exit to add here**, however tempting - nothing is known
   until each scan finishes.

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

    # not stable: 1 and 1.0 compare equal, so the sort cannot tell them apart,
    # but str() can - the later one comes out first
    l = [1, 1.0, 0]
    selection_sort(l)
    assert [str(x) for x in l] == ["0", "1.0", "1"]

test_selection_sort()
```

## Insertion Sort

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

**Time:** Θ(n²) worst, Θ(n) best &nbsp; **Space:** Θ(1) - in-place, stable, adaptive

**Recipe**

1. `i` from `1`, not `0`. A one-element prefix is already sorted, so there is
   nothing to do at `0`.
2. Save `x = l[i]` first. **The shifting loop overwrites `l[i]`, so the value has
   to be out of the array before the hole opens.**
3. `j = i - 1`, then while `j >= 0 and x < l[j]`, copy `l[j]` up to `l[j + 1]`
   and step `j` back. This shifts, it does not swap: one write per element
   instead of three.
4. **`j >= 0` has to come first in the `and`.** Without it, `j` reaching `-1`
   does not raise - `l[-1]` wraps to the last element, so the loop carries on
   comparing against the far end. From there it either walks off the front and
   raises `IndexError` from a line that looks innocent (`[2, 1]` does this,
   leaving `[2, 2]` behind), or stops early and writes `x` near the end of the
   list, returning a wrong answer with no error at all (`[1, 0, 0, 2]` comes back
   as `[0, 0, 2, 1]`).
5. Write `x` into `l[j + 1]`. **`j + 1`, because the loop exits one slot past
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

    # stable, on the same input that catches selection sort
    l = [1, 1.0, 0]
    insertion_sort(l)
    assert [str(x) for x in l] == ["0", "1", "1.0"]

test_insertion_sort()
```

## Python Built-in: `sorted()` and `list.sort()`

Python uses **Timsort** - a hybrid of merge sort + insertion sort.

| Function | Returns | In-place | Stable |
|----------|---------|----------|--------|
| `sorted(iterable)` | New list | No | Yes |
| `list.sort()` | None | Yes | Yes |

**Time complexity:** Θ(n log n) worst case, Θ(n) on nearly sorted data (adaptive).

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
