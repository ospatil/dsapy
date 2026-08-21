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

# Binary Search

Search a **sorted** array by repeatedly dividing the search interval in half.

**Time complexity:** O(log n)  
**Space complexity:** O(1) iterative, O(log n) recursive

**Prerequisite:** Array must be sorted.

## Comparison with Linear Search

| n | Linear O(n) | Binary O(log n) |
|---|-------------|----------------|
| 1,000 | 1,000 | 10 |
| 1,000,000 | 1,000,000 | 20 |
| 1,000,000,000 | 1,000,000,000 | 30 |

> **Mental model.** The loop is not really hunting for a value. It maintains a window
> `[lo, hi]` that is guaranteed to contain the answer, if the answer exists at all. Each step
> looks at the middle and throws away the half that cannot hold it. Sortedness is what makes
> that discard safe - one comparison rules out everything on one side at once.
>
> **Load-bearing:** what the window means at its edges. Is `hi` inside the window or one past
> it? Does a match stop the search or stay a candidate while you keep looking left? Those two
> choices are the entire difference between plain search, `lower_bound` and `upper_bound` -
> and they are why every off-by-one bug here lives in the `lo` and `hi` update lines, never in
> the comparison.


# Iterative Binary Search

Keep a window `[lo, hi]` that is guaranteed to contain the target if it is present at all.
Look at the middle: one comparison either finds it or discards half the window.

The loop condition is `lo <= hi`, not `lo < hi`, because a one-element window is still a
window worth checking - that off-by-one is the classic binary search bug.

Each step halves the window, so the step count is the number of times n can be halved:
log₂n. Twenty steps cover a million elements, thirty cover a billion.

**Time:** O(log n) &nbsp; **Space:** O(1)

```python
def binary_search(arr, target):
    """Returns index of target, or -1 if not found."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def test_binary_search():
    arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    assert binary_search(arr, 23) == 5
    assert binary_search(arr, 2) == 0
    assert binary_search(arr, 91) == 9
    assert binary_search(arr, 50) == -1
    assert binary_search([], 1) == -1

test_binary_search()
```

# Recursive Binary Search

The same three cases expressed as recursion, with `lo` and `hi` passed down instead of
reassigned. `lo > hi` - the empty window - is the base case that returns -1.

It reads more like the definition, but each level costs a stack frame, so the iterative
version is what you want in practice. (Python does not eliminate the tail call.)

**Time:** O(log n) &nbsp; **Space:** O(log n) - call stack

```python
def binary_search_rec(arr, target, lo, hi):
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if arr[mid] == target:
        return mid
    if arr[mid] < target:
        return binary_search_rec(arr, target, mid + 1, hi)
    return binary_search_rec(arr, target, lo, mid - 1)

def test_binary_search_rec():
    arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    assert binary_search_rec(arr, 23, 0, len(arr) - 1) == 5
    assert binary_search_rec(arr, 50, 0, len(arr) - 1) == -1

test_binary_search_rec()
```

# Lower Bound (First Occurrence)

Plain binary search returns *some* matching index; with duplicates that is not enough.
Lower bound answers a sharper question: the **first** index where `arr[i] >= target`.

Two deliberate differences from the search above:

- `hi` starts at `len(arr)`, not `len(arr) - 1`, so "no such element" can be expressed as
  the answer `len(arr)`
- a match does **not** stop the loop - it sets `hi = mid`, keeping the candidate in the
  window while continuing to look further left

```
lower_bound(3) in [1, 3, 3, 3, 5, 7]

lo=0 hi=6  mid=3  arr[3]=3 >= 3  → hi=3   (keep 3 as a candidate)
lo=0 hi=3  mid=1  arr[1]=3 >= 3  → hi=1
lo=0 hi=1  mid=0  arr[0]=1 <  3  → lo=1
lo=hi=1 → answer 1
```

The invariant: everything left of `lo` is `< target`, everything at `hi` and beyond is
`>= target`. When they meet, that boundary *is* the answer.

**Time:** O(log n) &nbsp; **Space:** O(1)

```python
def lower_bound(arr, target):
    """Returns first index where arr[i] >= target, or len(arr) if all elements < target."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def test_lower_bound():
    arr = [1, 3, 3, 3, 5, 7]
    assert lower_bound(arr, 3) == 1   # first 3
    assert lower_bound(arr, 4) == 4   # first element >= 4 is 5 at index 4
    assert lower_bound(arr, 0) == 0   # all >= 0
    assert lower_bound(arr, 8) == 6   # none >= 8

test_lower_bound()
```

# Upper Bound (First Strictly Greater)

Identical to lower bound with one character changed: `arr[mid] <= target` instead of
`<`. That shifts the boundary from "first element not less than target" to "first element
strictly greater".

The pair brackets all copies of a value, which is what makes counting and range queries
possible without a second scan:

```
[1, 3, 3, 3, 5, 7]

lower_bound(3) = 1      first 3
upper_bound(3) = 4      first element past the 3s
count of 3s    = 4 - 1 = 3
```

**Time:** O(log n) &nbsp; **Space:** O(1)

```python
def upper_bound(arr, target):
    """Returns first index where arr[i] > target, or len(arr) if all elements <= target."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def test_upper_bound():
    arr = [1, 3, 3, 3, 5, 7]
    assert upper_bound(arr, 3) == 4   # first element > 3 is 5 at index 4
    assert upper_bound(arr, 5) == 5   # first element > 5 is 7 at index 5
    # count of 3s = upper_bound - lower_bound = 4 - 1 = 3
    assert upper_bound(arr, 3) - lower_bound(arr, 3) == 3

test_upper_bound()
```

# Search in Rotated Sorted Array

A sorted array rotated at some pivot: `[4, 5, 6, 7, 0, 1, 2]`. The array as a whole is no
longer sorted, so the usual comparison cannot tell you which half to keep.

**Key insight:** cutting at `mid` always leaves at least one *sorted* half - the rotation
point can only be in one of them. Identify the sorted half with a single comparison
(`arr[lo] <= arr[mid]`), then check whether the target falls inside its known range. If it
does, search there; otherwise the answer can only be in the other half.

```
find 1 in [4, 5, 6, 7, 0, 1, 2]

lo=0 hi=6  mid=3  arr[3]=7    arr[0]=4 <= 7, so left half [4..7] is sorted
                              is 1 in [4, 7)? no → go right, lo=4
lo=4 hi=6  mid=5  arr[5]=1    found at index 5
```

So the extra work versus plain binary search is one comparison per step to decide which
half is the trustworthy one - the complexity is unchanged.

**Time:** O(log n) &nbsp; **Space:** O(1)

```python
def search_rotated(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        # left half is sorted
        if arr[lo] <= arr[mid]:
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        # right half is sorted
        else:
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

def test_search_rotated():
    arr = [4, 5, 6, 7, 0, 1, 2]
    assert search_rotated(arr, 0) == 4
    assert search_rotated(arr, 4) == 0
    assert search_rotated(arr, 2) == 6
    assert search_rotated(arr, 3) == -1
    assert search_rotated([1], 1) == 0

test_search_rotated()
```

# Python Built-in: `bisect` module

The `bisect` module provides binary search on sorted lists.

| Function | Equivalent to |
|----------|---------------|
| `bisect_left(a, x)` | `lower_bound` - first index where `a[i] >= x` |
| `bisect_right(a, x)` | `upper_bound` - first index where `a[i] > x` |
| `insort(a, x)` | Insert `x` into sorted list maintaining order |

```python
from bisect import bisect_left, bisect_right, insort

arr = [1, 3, 3, 3, 5, 7]

# bisect_left = lower_bound
print(bisect_left(arr, 3))    # 1 - first position for 3

# bisect_right = upper_bound
print(bisect_right(arr, 3))   # 4 - past last 3

# count occurrences of 3
print(bisect_right(arr, 3) - bisect_left(arr, 3))  # 3

# exact search using bisect_left
def bisect_search(arr, target):
    i = bisect_left(arr, target)
    if i < len(arr) and arr[i] == target:
        return i
    return -1

print(bisect_search(arr, 5))   # 4
print(bisect_search(arr, 4))   # -1

# insort - insert maintaining sorted order, O(n) due to shifting
sorted_list = [1, 3, 5, 7]
insort(sorted_list, 4)
print(sorted_list)  # [1, 3, 4, 5, 7]
```
