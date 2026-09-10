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


## Iterative Binary Search

The condition being sought is an index `i` with `arr[i] == target`, and nothing beyond that:
if the target appears more than once, any one of its indices satisfies it.

`lo` and `hi` are not cursors walking the array. `lo` is the first index not yet ruled out and
`hi` is the last one, so the closed window `[lo, hi]` is exactly the set of indices that could
still hold the target. Everything outside it has been *proven* not to.

One comparison at `mid` rules out an entire side. If `arr[mid] < target`, sortedness says
every index at or below `mid` holds a value no larger than `arr[mid]`, so all of them are below
the target too, and `lo` jumps to `mid + 1`. If `arr[mid] > target` the mirror argument moves
`hi` to `mid - 1`. Sortedness is doing all the work: without it, one comparison tells you about
one element instead of half the array.

Each step halves the window, so the step count is the number of times n can be halved:
log₂n. Twenty steps cover a million elements, thirty cover a billion.

What this variant cannot tell you is *which* copy it found. Searching `[1, 3, 3, 3, 5, 7]` for
3 returns index 2, whichever copy `mid` landed on first, not the leftmost 3. Closing that gap
is what `lower_bound` below is for.

**Cold recall:** closed window, `lo <= hi`, and both updates step past `mid`.

**Time:** O(log n) &nbsp; **Space:** O(1)

**Recipe**

1. `lo, hi = 0, len(arr) - 1`. Both ends are real indices, so an empty array
   starts at `hi = -1` and the loop test rejects it before any indexing happens.
2. Loop while `lo <= hi`, **including the `=`.** Drop it and a one-element window
   is never examined at all: `binary_search([1], 1)` returns `-1`.
3. `mid = (lo + hi) // 2`; return `mid` on equality.
4. `arr[mid] < target`: `lo = mid + 1`. Otherwise `hi = mid - 1`.
5. **The `+ 1` and `- 1` are what terminate the loop**, not the halving. `mid` has
   just been compared, so leaving it in the window lets a two-element step
   reproduce itself forever.
6. Fall out of the loop and return `-1`.

`(lo + hi) // 2` is safe at any size in Python. Writing this in a fixed-width
language needs `lo + (hi - lo) // 2`, since `lo + hi` can overflow.

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
    assert binary_search(arr, 2) == 0         # first index
    assert binary_search(arr, 91) == 9        # last index
    assert binary_search(arr, 50) == -1
    assert binary_search([], 1) == -1         # empty: hi = -1, loop never runs
    assert binary_search([7], 7) == 0         # the window the `=` saves
    assert binary_search([7], 3) == -1
    # with duplicates it returns *a* match, not the leftmost one
    assert binary_search([1, 3, 3, 3, 5, 7], 3) == 2

test_binary_search()
```

## Recursive Binary Search

Same condition, same window, but the window travels in the argument list instead of in two
reassigned variables. `lo` and `hi` still mean "first and last index not yet ruled out"; the
difference is that each call owns its own pair and never mutates its caller's.

Discarding a half is now expressed by *which subrange you hand down*: `(mid + 1, hi)` throws
away everything up to and including `mid`, `(lo, mid - 1)` everything from `mid` on. The empty
window `lo > hi` is where the recursion bottoms out, and it is exactly the loop test negated.
If those two ever drift apart, the two functions disagree about which windows are worth
looking at.

Nothing happens on the way back up, so each call just forwards its child's answer unchanged.
That is what makes this a loop in disguise, and also why it costs a stack frame per level for
no benefit: Python does not eliminate the tail call. Prefer the iterative version in practice.

**Cold recall:** the loop test negated is the base case; the two updates become the two calls.

**Time:** O(log n) &nbsp; **Space:** O(log n) - call stack

**Recipe**

1. Take `lo` and `hi` as parameters. There is no other state, so the caller has to
   supply the starting window: `binary_search_rec(arr, target, 0, len(arr) - 1)`.
2. `if lo > hi: return -1` **before touching `arr`.** On an empty array the caller
   passes `hi = -1`, and this test is the only thing between you and an index
   error.
3. `mid = (lo + hi) // 2`; return `mid` on a hit.
4. Too small, recurse on `(mid + 1, hi)`. Too big, recurse on `(lo, mid - 1)`.
5. **`return` the recursive call, do not just make it.** There is nothing to fix up
   on the way back, so a bare call leaves the function returning `None`, which is
   not `-1` and passes no caller's "not found" check.

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
    assert binary_search_rec(arr, 2, 0, len(arr) - 1) == 0
    assert binary_search_rec(arr, 50, 0, len(arr) - 1) == -1
    assert binary_search_rec([7], 7, 0, 0) == 0
    assert binary_search_rec([], 1, 0, -1) == -1   # base case, no indexing
    # base case and loop test agree, so the two versions agree on every target
    assert all(
        binary_search_rec(arr, t, 0, len(arr) - 1) == binary_search(arr, t)
        for t in range(100)
    )

test_binary_search_rec()
```

## Lower Bound (First Occurrence)

The condition here is not "equal to the target" but a **boundary**: the first index where
`arr[i] >= target`. Sortedness means the array is a run of values `< target` followed by a run
of values `>= target`, and the answer is the single index where one run becomes the other.
Equality can no longer end the search, because a match is not evidence that it is the leftmost
match.

That changes what the two variables mean. `lo` keeps its old identity - nothing below it can
be the answer, because every index left of `lo` holds a value `< target`. But `hi` is no
longer a ruled-out index. It is the **leftmost candidate found so far**, and everything from
`hi` rightwards is known to satisfy `>= target`. So the window is half-open, `[lo, hi)`, and
starting `hi` at `len(arr)` says "no candidate yet" - which doubles as the correct answer when
every element is too small.

Branch elimination falls straight out of those meanings. `arr[mid] < target` puts `mid` in the
left run, so `mid` and everything below it are out: `lo = mid + 1`. Otherwise `mid` satisfies
the condition and is the best candidate seen, so it has to stay inside the window: `hi = mid`.
When `lo` and `hi` meet, the run boundary is pinned between them, and that index *is* the
answer.

```
lower_bound(3) in [1, 3, 3, 3, 5, 7]

lo=0 hi=6  mid=3  arr[3]=3 >= 3  → hi=3   (keep 3 as a candidate)
lo=0 hi=3  mid=1  arr[1]=3 >= 3  → hi=1
lo=0 hi=1  mid=0  arr[0]=1 <  3  → lo=1
lo=hi=1 → answer 1
```

**Cold recall:** half-open window, `lo < hi`, and the qualifying branch keeps `mid` by writing
`hi = mid`.

**Time:** O(log n) &nbsp; **Space:** O(1)

**Recipe**

The half-open window, the loop test and the `hi = mid` update are a single package;
mixing any one of them with the closed-window version breaks the result.

1. `lo, hi = 0, len(arr)`, with `hi` one past the end.
2. Loop while `lo < hi`, **no `=`.** `hi` is a candidate rather than a ruled-out
   index, so `lo == hi` already pins the boundary. With `lo <= hi` the function
   hangs on a hit and raises `IndexError` on `arr[mid]` when no element qualifies.
3. `arr[mid] < target`: `lo = mid + 1`.
4. Otherwise `hi = mid`, **not `mid - 1`.** With `mid - 1` a search for 3 in
   `[1, 3, 3, 3, 5, 7]` returns 0, because the only correct answer gets stepped
   over on the way past.
5. `hi = mid` still shrinks the window even without a `- 1`: while `lo < hi`,
   `mid = (lo + hi) // 2` is at most `hi - 1`. That is the entire termination
   argument for this shape.
6. Return `lo`. There is no `-1` case and no bounds check, so a caller wanting
   "found or not" has to test `lo < len(arr) and arr[lo] == target` itself.

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
    assert lower_bound(arr, 3) == 1   # leftmost 3, not the one mid lands on
    assert lower_bound(arr, 4) == 4   # first element >= 4 is 5 at index 4
    assert lower_bound(arr, 0) == 0   # all >= 0
    assert lower_bound(arr, 8) == 6   # none >= 8, so len(arr)
    assert lower_bound([], 3) == 0    # empty: 0 and len(arr) coincide
    assert lower_bound([3, 3, 3], 3) == 0   # every element qualifies

test_lower_bound()
```

## Upper Bound (First Strictly Greater)

The same boundary machinery, one notch further along: the first index where `arr[i] > target`.
The array again splits into two runs, but the cut now falls *after* the copies of the target
instead of before them, so an element equal to the target belongs on the discarded side.

That relocation of equality is the whole change. In `lower_bound`, `arr[mid] == target`
qualifies as a candidate and moves `hi`; here it fails the condition, which puts it in the
ruled-out branch alongside everything below it. Turning `arr[mid] < target` into
`arr[mid] <= target` moves equality across that line, and the meaning of `lo` and `hi` shifts
with it: everything left of `lo` is now `<= target`, everything at `hi` and beyond is
`> target`.

The pair brackets all copies of a value, which is what makes counting and range queries
possible without a second scan:

```
[1, 3, 3, 3, 5, 7]

lower_bound(3) = 1      first 3
upper_bound(3) = 4      first element past the 3s
count of 3s    = 4 - 1 = 3
```

Because both return a boundary rather than a hit, the subtraction is also right for a value
that is absent: the two land on the same index and the count is 0.

**Cold recall:** `lower_bound` keeps equals as candidates, `upper_bound` pushes them left. One
character: `<` becomes `<=`.

**Time:** O(log n) &nbsp; **Space:** O(1)

**Recipe**

Copy `lower_bound` and change one character: `arr[mid] < target` becomes
`arr[mid] <= target`.

1. The `lo, hi = 0, len(arr)` window, the `lo < hi` test and the `hi = mid` update
   stay identical. `upper_bound - lower_bound` is a count only because both
   functions index the same way; change the interval convention in one and the
   subtraction is mixing two coordinate systems.
2. **The `=` belongs on the comparison against `target`, not on the loop test.**
   Putting it on `lo < hi` does not shift the boundary, it hangs the function.

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
    assert upper_bound(arr, 7) == 6   # none greater, so len(arr)
    assert upper_bound(arr, 0) == 0   # all greater
    assert upper_bound([], 3) == 0
    # the pair brackets a run of equals, and gives 0 for an absent value
    assert upper_bound(arr, 3) - lower_bound(arr, 3) == 3
    assert upper_bound(arr, 4) - lower_bound(arr, 4) == 0

test_upper_bound()
```

## Search in Rotated Sorted Array

The condition is the plain one again, an index `i` with `arr[i] == target`, but the
precondition is weaker. `[4, 5, 6, 7, 0, 1, 2]` is a sorted array cut at some pivot with the
two pieces swapped, so it rises everywhere except at exactly one place where it drops. That
single drop is all that separates this from plain binary search, and it is enough to destroy
the branch test: `arr[mid] < target` no longer tells you which side the target is on.

`lo`, `hi` and `mid` mean exactly what they meant in the plain version - a closed window of
indices not yet ruled out. The new piece of state is not a variable at all, it is a property of
the window: **it contains at most one drop.** Every step has to hand that property down to the
half it keeps, or the next step's reasoning is invalid.

**Key insight:** cutting at `mid` always leaves at least one *sorted* half - the rotation
point can only be in one of them. Identify the sorted half with a single comparison
(`arr[lo] <= arr[mid]`), then check whether the target falls inside its known range. If it
does, search there; otherwise the answer can only be in the other half.

Why that one comparison settles it: rotation takes a sorted run and moves a chunk from the
front to the back, so there is exactly one place where a value drops instead of rising. If
`arr[lo] <= arr[mid]`, no drop happened between `lo` and `mid`, so that side is a clean
ascending run and its contents are exactly the values from `arr[lo]` to `arr[mid]`. If the
comparison fails, the drop is in there, which puts the clean run on the other side. Either
way one side becomes a range you can test a value against in constant time - which is the
thing plain binary search gets for free and rotation takes away.

The half you keep is then a shorter window with at most one drop in it, so the property
survives and the argument repeats.

This needs **distinct values**, and with duplicates the failure is a wrong answer rather than
a slow one. When `arr[lo] == arr[mid]` the comparison reports "left is sorted" while the drop
may be sitting inside it, and the code discards the half holding the target:
`search_rotated([0, 1, 0, 0, 0], 1)` returns `-1` though the 1 is at index 1. The repair is to
make the tie its own case and surrender one element per step (`lo += 1` when
`arr[lo] == arr[mid]`), which is correct but degrades to O(n) on an array of equal values.

```
find 1 in [4, 5, 6, 7, 0, 1, 2]      ranges below are VALUE ranges, not index ranges

lo=0 hi=6  mid=3  arr[3]=7    arr[0]=4 <= 7, so the left half holds values 4..7, sorted
                              is the target 1 in 4..7 (7 excluded)? no -> go right, lo=4
lo=4 hi=6  mid=5  arr[5]=1    found at index 5
```

The value/index confusion is easy here because this array's values happen to look like
indices. `lo`, `hi` and `mid` are always indices; `4..7` is a span of values.

So the extra work versus plain binary search is one comparison per step to decide which
half is the trustworthy one - the complexity is unchanged.

**Cold recall:** one half is always sorted; find it with `arr[lo] <= arr[mid]`, then keep the
half whose value range brackets the target.

**Time:** O(log n) &nbsp; **Space:** O(1)

**Recipe**

1. Same closed window and same `lo <= hi` loop as plain binary search. Return
   `mid` on a hit, which also rules `mid` out for every test below.
2. `arr[lo] <= arr[mid]` means the left side is sorted. **The `=` is required, not
   stylistic. On a two-element window `lo == mid`, and a strict `<` judges that
   side unsorted and sends the search the wrong way.** `[1, 0]` searching for `0`
   returns `-1` with `<`.
3. Left sorted: if `arr[lo] <= target < arr[mid]` the target can only be there, so
   `hi = mid - 1`. Otherwise `lo = mid + 1`.
4. Right sorted: mirror it. `arr[mid] < target <= arr[hi]` gives `lo = mid + 1`,
   else `hi = mid - 1`.
5. **Both range tests are closed on their outer end - `arr[lo] <=` and
   `<= arr[hi]` - and that is where the off-by-one actually bites.** Tighten
   either to a strict `<` and a target sitting exactly on that end is lost:
   `[4, 5, 6, 7, 0, 1, 2]` searching `4` returns `-1` with `arr[lo] < target`, and
   `[5, 1, 2, 3, 4]` searching `4` returns `-1` with `target < arr[hi]`. The `mid`
   end is the free one, since step 1 already ruled `mid` out.

```python
def search_rotated(arr, target):
    """Returns index of target, or -1. Requires distinct values."""
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
    assert search_rotated(arr, 4) == 0    # on the sorted half's closed lo end
    assert search_rotated(arr, 2) == 6
    assert search_rotated(arr, 3) == -1
    assert search_rotated([5, 1, 2, 3, 4], 4) == 4   # closed hi end, right half
    assert search_rotated([1, 0], 0) == 1   # needs `=` in arr[lo] <= arr[mid]
    assert search_rotated([0, 1, 2, 4, 5], 5) == 4   # zero rotation is valid
    assert search_rotated([1], 1) == 0
    assert search_rotated([], 1) == -1
    # documented limitation: duplicates defeat the sorted-half test, so the 1
    # at index 1 is reported absent
    assert search_rotated([0, 1, 0, 0, 0], 1) == -1

test_search_rotated()
```

## Python Built-in: `bisect` module

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
