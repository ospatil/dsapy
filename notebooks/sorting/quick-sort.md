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

# Quick Sort

Quick sort picks one element as the **pivot** and rearranges the range so the pivot sits in
its final place, with smaller values on its left and larger values on its right. Then it
sorts each side the same way.

## Algorithm Properties

- **Time Complexity:**
  - Best/Average case: O(n log n)
  - Worst case: O(n²)
- **Space Complexity:** O(log n) average, O(n) worst case
- **In-place:** Yes (no auxiliary space for partitioning)
- **Stable:** No

> **Mental model.** Quick sort is merge sort held up to a mirror. Merge sort splits cheaply
> and pays for it in the merge. Quick sort pays up front in the split and then has nothing
> left to do, because partitioning already puts the pivot in the slot it will occupy in the
> finished array - forever. Everything smaller is somewhere on its left, everything larger
> somewhere on its right, so the two sides never have to look at each other again. Sort both
> sides and the array is sorted. There is no combine step at all.
>
> **Load-bearing:** which element you pick as the pivot. The pivot decides how evenly the
> range splits, and only an even split gives log n levels of recursion. A pivot that turns
> out to be the smallest or largest value peels off one element and leaves n-1 behind, so the
> recursion runs n levels deep and the cost climbs to O(n²). The case worth remembering: both
> schemes below take the pivot from a fixed end of the range, so already-sorted input hits
> that worst case every single time.

## Why Quick Sort is Popular

Despite quadratic worst case, it's considered faster because:
- **In-place:** No auxiliary space for partitioning
- **Cache friendly:** Good locality of reference
- **Average case:** O(n log n)
- **Tail recursive:** Can be optimized

## Comparison with Merge Sort

- **Merge Sort:** Simple partition, complex merge
- **Quick Sort:** Complex partition, simple "merge" (no merge needed)

## Partition Schemes

1. **Naive:** Stable, Θ(n) space, 3 passes
2. **Lomuto:** Not stable, Θ(1) space, 1 pass
3. **Hoare:** Not stable, Θ(1) space, 1 pass, faster constants

## Worst-Case Derivation - O(n²)

When pivot is always min/max, recurrence is T(n) = T(n-1) + Θ(n). Expanding: T(n) = n + (n-1) + ... + 1 = n(n+1)/2 = **Θ(n²)**.

## Average-Case Intuition - O(n log n)

On average, pivot splits array into roughly balanced parts, giving same recurrence as merge sort: T(n) = 2T(n/2) + Θ(n) → **O(n log n)**.


# Partition Algorithms

Partitioning is the whole of quick sort: pick a pivot and rearrange so that everything ≤
pivot sits left of everything > pivot. The pivot lands in its final position, and the two
sides can then be sorted independently - there is no merge step to pay for.

**Input:** `a = [3, 8, 6, 12, 10, 7]`, pivot index 5 (value 7)

The naive scheme below does it in the obvious way: two passes collecting the small and
large elements into a temporary list, then copy back. That is easy to read, stable, and
costs Θ(n) extra space - which defeats the main reason to choose quick sort. The Lomuto
and Hoare schemes that follow do the same job in place, with a single pass.

**Time:** O(n) for all three schemes &nbsp; **Space:** Θ(n) naive, O(1) for the others

**Recipe**

1. Swap the chosen pivot to the end, then read `pivot = a[n - 1]`.
2. Pass one: append every element `<= pivot` to a scratch list, in order.
3. Pass two: append every element `> pivot` to the same list.
4. Pass three: `a[:] = temp` to copy back. **`a[:] =` rather than `a = `, or the
   caller sees no change at all.**
5. **This is stable**, since both passes preserve the original relative order,
   and that is the one thing it has over the two schemes below.
6. **The cost is O(n) extra space and three passes**, which is exactly what
   Lomuto and Hoare remove by swapping in place. Nobody uses this in a real
   quicksort; it is here to make the in-place versions look like a repair rather
   than a fact.
7. `is_partitioned` checks the defining property, not a specific arrangement:
   once a value greater than the pivot has been seen, nothing smaller may follow.

```python
def partition_naive(a, p):
    """
    Naive partition scheme
    - Stable but requires Θ(n) auxiliary space
    - Makes 3 passes through the array
    """
    n = len(a)
    a[p], a[n - 1] = a[n - 1], a[p]  # move pivot to end
    pivot = a[n - 1]
    temp = []

    # first pass: collect elements <= pivot
    for x in a:
        if x <= pivot:
            temp.append(x)

    # second pass: collect elements > pivot
    for x in a:
        if x > pivot:
            temp.append(x)

    # third pass: copy back to original array
    a[:] = temp


def is_partitioned(a, pivot_val):
    """True if every element <= pivot_val comes before every element > it."""
    seen_greater = False
    for x in a:
        if x > pivot_val:
            seen_greater = True
        elif seen_greater:
            return False
    return True


def test_partition_naive():
    a = [3, 8, 6, 12, 10, 7]
    partition_naive(a, 5)  # pivot is 7
    assert a == [3, 6, 7, 8, 12, 10]
    assert is_partitioned(a, 7)
    # relative order within each side is preserved - the scheme is stable
    assert a[:3] == [3, 6, 7]
    assert a[3:] == [8, 12, 10]
    # the helper actually rejects an unpartitioned array
    assert is_partitioned([3, 8, 6], 7) is False


test_partition_naive()
```

# Lomuto Partition Scheme

One pass, one extra index, no auxiliary array. Take the last element as pivot and keep the
array divided into three regions:

```
| < pivot | >= pivot | unprocessed | pivot |
         i          j                    h
```

`i` marks the end of the "small" region and `j` scans forward. Every time `j` finds an
element smaller than the pivot, the small region grows by one and the newcomer is swapped
into it. The test is strict (`a[j] < pivot`), so elements *equal* to the pivot stay in the
right-hand region - which is what keeps an all-equal array from piling everything on one
side. The pivot itself waits at `h`, outside the scanned range, until the end. When the scan ends, swapping the pivot into `i + 1` puts it exactly between the
two regions - its final sorted position.

Returning the pivot's true index is what lets `qsort_lomuto` recurse on `[l, p-1]` and
`[p+1, h]` and leave the pivot out of both.

**Time:** O(n) &nbsp; **Space:** O(1) - in place, not stable

**Recipe**

1. Pivot is the **last** element, `a[h]`.
2. `i = l - 1`. Read `i` as "index of the last element known to be smaller than
   the pivot", so starting one before the window means "none yet".
3. Scan `j` from `l` to `h - 1`, stopping short of the pivot itself.
4. `a[j] < pivot`: advance `i`, then swap `a[j]` into `a[i]`. This grows the
   small region by one and pushes a large element out to where `j` was.
5. After the scan, swap the pivot into `a[i + 1]`. **`i + 1` is the first slot of
   the large region, which is exactly the pivot's sorted position.**
6. Return `i + 1`, **the pivot's final index**. Remember which of the two schemes
   returns this, because the driver depends on it.

```python
def partition_lomuto(a, l, h):
    """
    Lomuto partition scheme
    - Uses last element as pivot
    - Returns final position of pivot
    """
    pivot = a[h]
    i = l - 1  # index of last element < pivot

    for j in range(l, h):
        if a[j] < pivot:
            i += 1
            a[j], a[i] = a[i], a[j]

    # place pivot in correct position
    a[i + 1], a[h] = a[h], a[i + 1]
    return i + 1


def test_partition_lomuto():
    a = [3, 8, 6, 12, 10, 7]
    pivot_pos = partition_lomuto(a, 0, 5)
    pivot_val = a[pivot_pos]
    assert pivot_val == 7
    assert pivot_pos == 2

    # check partition property
    for i in range(pivot_pos):
        assert a[i] <= pivot_val
    for i in range(pivot_pos + 1, len(a)):
        assert a[i] > pivot_val

    # already sorted input - pivot is the largest, so it stays put
    a = [1, 2, 3, 4]
    assert partition_lomuto(a, 0, 3) == 3
    assert a == [1, 2, 3, 4]

    # all equal: nothing is strictly less than the pivot
    a = [5, 5, 5]
    assert partition_lomuto(a, 0, 2) == 0


test_partition_lomuto()
```

# Hoare Partition Scheme

Two pointers walking toward each other instead of one scanning forward. `i` advances while
elements are smaller than the pivot, `j` retreats while they are larger; when both stop,
each is sitting on an element that belongs on the other side, so swap them and continue.
When the pointers cross, the array is partitioned.

```
a = [7, 8, 6, 12, 10, 3]   pivot = 7 (the first element)
                           `|` marks the returned boundary, NOT the pivot's position
                           (in the Lomuto trace above the same bar meant the opposite)

after partitioning:   [3, 6 | 8, 12, 10, 7]   returns j = 1
                            ^ boundary        the pivot value 7 ended up at index 5
```

The catch, and the reason `qsort_hoare` differs from `qsort_lomuto`: the returned index is
a **boundary, not the pivot's position**. `j` is the *last index of the left part*, so
`a[l..j]` are all <= the pivot and `a[j+1..h]` all >=, but the pivot value itself is free to
be anywhere - here it finished on the right side. So the recursion has to be `[l, p]` and
`[p+1, h]` - including `p` - rather than excluding it. Using Lomuto's `[l, p-1]` here would
drop an element.

Fewer swaps and better constants than Lomuto, which is why library implementations tend to
prefer it.

**Time:** O(n) &nbsp; **Space:** O(1) - in place, not stable

**Recipe**

1. Pivot is the **first** element, `a[l]`. **Not `a[h]`. Hoare's loop only
   terminates because the pivot sits at the low end.**
2. `i, j = l - 1, h + 1`, one outside the window on each side, because both
   pointers step before they read.
3. Advance `i` while `a[i] < pivot`; retreat `j` while `a[j] > pivot`. The
   comparisons are strict, so both pointers stop on a value equal to the pivot.
   **That is what stops one pointer from running off the end on an array of
   equal values.**
4. Crossed, `i >= j`: return `j`.
5. Otherwise swap `a[i]` and `a[j]` and go round again.
6. Return `j`, which is **a boundary, not the pivot's position**. Nothing is
   guaranteed to be in its final place, unlike Lomuto.

```python
def partition_hoare(a, l, h):
    """
    Hoare partition scheme
    - Uses first element as pivot
    - Returns boundary index (not pivot position)
    """
    pivot = a[l]
    i, j = l - 1, h + 1

    while True:
        # move i right until element >= pivot
        i += 1
        while a[i] < pivot:
            i += 1

        # move j left until element <= pivot
        j -= 1
        while a[j] > pivot:
            j -= 1

        # if pointers crossed, partitioning is done
        if i >= j:
            return j

        # swap out-of-place elements
        a[i], a[j] = a[j], a[i]


def test_partition_hoare():
    a = [7, 8, 6, 12, 10, 3]
    boundary = partition_hoare(a, 0, 5)
    pivot_val = 7  # first element

    # check partition property around boundary
    for i in range(boundary + 1):
        assert a[i] <= pivot_val
    for i in range(boundary + 1, len(a)):
        assert a[i] >= pivot_val

    # the pivot is not necessarily at the boundary - unlike Lomuto
    a = [4, 1, 3, 2]
    boundary = partition_hoare(a, 0, 3)
    assert max(a[: boundary + 1]) <= min(a[boundary + 1 :])

    # all equal: pointers meet in the middle
    a = [5, 5, 5, 5]
    assert partition_hoare(a, 0, 3) == 1


test_partition_hoare()
```

# Quick Sort Implementation

## Lomuto-based Quick Sort

Partition, then recurse on each side. There is no combine step - the pivot is already
final and the two halves are already in the right region, so when the recursion unwinds the
array is sorted.

```
qsort_lomuto([8, 4, 7, 9, 3, 10, 5])
                      `|` marks where the pivot finished, in its final place

partition around 5    -> [4, 3, 5 | 9, 8, 10, 7]   pivot lands at index 2
  left  [4, 3]        -> partition around 3 -> [3, 4]
  right [9, 8, 10, 7] -> partition around 7 -> [7 | 8, 10, 9]
                        then [8, 10, 9]    -> partition around 9 -> [8, 9, 10]

result: [3, 4, 5, 7, 8, 9, 10]
```

`if l < h` is the base case: one element or none needs no sorting.

Because the pivot's exact index is known, both recursive calls exclude it - each call
shrinks the range by at least one element, which is what guarantees termination.

**Time:** O(n log n) average, O(n²) worst &nbsp; **Space:** O(log n) stack average

**Recipe**

1. Do nothing unless `l < h`.
2. `p = partition_lomuto(a, l, h)`.
3. Recurse on `(l, p - 1)` and `(p + 1, h)`. **`p` is excluded from both, because
   Lomuto leaves the pivot in its final sorted position and it never needs
   moving again.**
4. **Using `(l, p)` here recurses forever.** The subproblem never shrinks when
   the pivot is the smallest element.

```python
def qsort_lomuto(a, l, h):
    """
    Quick sort using Lomuto partition
    """
    if l < h:
        p = partition_lomuto(a, l, h)  # get pivot position
        qsort_lomuto(a, l, p - 1)      # sort left part
        qsort_lomuto(a, p + 1, h)      # sort right part


def test_qsort_lomuto():
    a = [8, 4, 7, 9, 3, 10, 5]
    qsort_lomuto(a, 0, len(a) - 1)
    assert a == [3, 4, 5, 7, 8, 9, 10]

    # edge cases
    a = [1]
    qsort_lomuto(a, 0, 0)
    assert a == [1]

    a = [2, 1]
    qsort_lomuto(a, 0, 1)
    assert a == [1, 2]

    a = []
    qsort_lomuto(a, 0, -1)
    assert a == []

    # already sorted and reverse sorted - the O(n²) cases
    a = [1, 2, 3, 4, 5]
    qsort_lomuto(a, 0, 4)
    assert a == [1, 2, 3, 4, 5]

    a = [5, 4, 3, 2, 1]
    qsort_lomuto(a, 0, 4)
    assert a == [1, 2, 3, 4, 5]


test_qsort_lomuto()
```

## Hoare-based Quick Sort

The same shape with the boundary difference carried through: `qsort_hoare(a, l, p)` keeps
index `p` in the left call, because Hoare's return value is a partition boundary and not a
finished pivot position.

Getting this wrong is the classic Hoare bug - write `p - 1` here and elements silently
never get sorted, or the recursion fails to shrink and overflows the stack.

**Time:** O(n log n) average, O(n²) worst &nbsp; **Space:** O(log n) stack average

**Recipe**

1. Same shape, one crucial difference.
2. `p = partition_hoare(a, l, h)`, then recurse on `(l, p)` and `(p + 1, h)`.
3. **`p` is included in the left half.** Hoare returns a boundary, not a sorted
   position, so the element at `p` still has to be sorted by someone.
4. **Copying Lomuto's `(l, p - 1)` here silently drops elements.** It does not
   crash and it passes on plenty of inputs; `[2, 0, 1]` is the smallest array
   that comes back unsorted.

```python
def qsort_hoare(a, l, h):
    """
    Quick sort using Hoare partition
    """
    if l < h:
        p = partition_hoare(a, l, h)  # get boundary index
        qsort_hoare(a, l, p)          # sort left part (includes p)
        qsort_hoare(a, p + 1, h)      # sort right part


def test_qsort_hoare():
    a = [8, 4, 7, 9, 3, 10, 5]
    qsort_hoare(a, 0, len(a) - 1)
    assert a == [3, 4, 5, 7, 8, 9, 10]

    # with duplicates
    a = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    qsort_hoare(a, 0, len(a) - 1)
    assert a == [1, 1, 2, 3, 4, 5, 5, 6, 9]

    # both schemes agree, and agree with sorted()
    import random

    data = [random.randint(0, 50) for _ in range(60)]
    lomuto, hoare = list(data), list(data)
    qsort_lomuto(lomuto, 0, len(lomuto) - 1)
    qsort_hoare(hoare, 0, len(hoare) - 1)
    assert lomuto == hoare == sorted(data)


test_qsort_hoare()
```
