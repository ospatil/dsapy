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

# Two Pointers & Sliding Window

Techniques for solving array/string problems in O(n) by avoiding nested loops.

## Two Pointers

Use two indices that move towards each other or in the same direction.

**Common patterns:**
- Opposite ends: start from both ends, move inward (pair sum, palindrome)
- Same direction: slow/fast pointers (remove duplicates, linked list cycle)

## Sliding Window

Maintain a window (subarray/substring) that expands or shrinks.

**Common patterns:**
- Fixed-size window: max sum of k consecutive elements
- Variable-size window: smallest subarray with sum ≥ target

> **Mental model.** Both patterns are the same trick: never move a pointer backwards. Two
> indices sweep the array, each one only ever going forward, so the total work is linear even
> though the two ends move independently of each other. That is what replaces the nested loop.
> A step does not just test one candidate, it retires a whole family of candidates for good.
>
> **Load-bearing:** the condition you test has to move in one direction only. Growing the
> window can push it one way but never back, so once you shrink you never have to reconsider.
> The word for that is *monotonic*. Non-negative values make a sum monotonic in the window
> size; allow one negative value and shrinking could raise the sum, and the argument
> collapses.

![Sliding Window](images/sliding-window.png)


## Two Sum (Sorted Array)

Checking every pair is O(n²) because each check settles one pair. Reframe the question: instead
of "does this pair sum to the target?", ask **"which index can I prove has no partner left?"**
On sorted input a single comparison answers that, and an index proved partnerless is gone for
good, so n comparisons settle the whole array.

`lo` and `hi` are more than "the two ends". `lo` is the smallest value not yet ruled out and
`hi` the largest, so the closed range `lo..hi` is exactly the set of indices that could still
take part in a match. The invariant: if a matching pair exists at all, both of its indices lie
inside that range.

Each step maintains it by comparing `arr[lo] + arr[hi]` against the target.

- **Too small.** `hi` is the largest partner `lo` has left, so every remaining pair using `lo`
  sums to at most this, and all of them fall short. `lo` has no partner left, so discard it:
  `lo += 1`.
- **Too large.** The mirror argument. `lo` is the smallest partner `hi` has left, so every
  remaining pair using `hi` sums to at least this, and all overshoot. Discard `hi`: `hi -= 1`.

What gets discarded is an *index*, not a pair. Retiring `lo` retires the `hi - lo` pairs that
used it in one step, and that is where the factor of n goes.

```
[2, 7, 11, 15]  target 9

lo=0 hi=3   2 + 15 = 17 > 9  → 15 is too big for anything → hi=2
lo=0 hi=2   2 + 11 = 13 > 9  → hi=1
lo=0 hi=1   2 +  7 =  9      → found (0, 1)
```

Sortedness is the whole prerequisite, and its job is exact: it is what makes "`hi` is the
largest partner `lo` has left" a true statement. Unsorted, that sentence is false and the
discard throws the answer away. `[3, 1, 2]` with target 3 computes `3 + 2 = 5`, too large, so
it drops the 2; then `3 + 1 = 4`, still too large, so it drops the 1; the pointers meet and it
reports `(-1, -1)` with `1 + 2 = 3` sitting untouched. On unsorted input use a hash set
instead: still O(n) time, but O(n) space rather than O(1).

Empty and one-element inputs need no guard. `hi` starts at `-1` and `0` respectively, `lo < hi`
is false on entry, nothing is read, and the answer is `(-1, -1)`. That strict `<` is also what
stops an element pairing with itself: `[5]` with target 10 returns `(-1, -1)`, not `(0, 0)`.

Duplicates and ties are decided by the sweep order. Pairs are examined from the outside in, so
the first match found is the widest one: `[1, 3, 3, 5]` with target 6 returns `(0, 3)`, the
`1 + 5`, not the inner `3 + 3`. `[3, 3]` with target 6 returns `(0, 1)`, since equal values are
still two distinct indices. Only one pair comes back; enumerating all of them means continuing
the sweep past the first hit instead of returning.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `lo, hi = 0, len(arr) - 1`. No empty or singleton guard is needed, step 2 covers both.
2. Loop `while lo < hi`, **strictly**. `<=` lets an element pair with itself, so any target of
   `2 * arr[i]` reports a false hit at `(i, i)`.
3. One sum per iteration, `s = arr[lo] + arr[hi]`. On `s == target` return `(lo, hi)` at once.
4. `s < target`: `lo += 1`. `s > target`: `hi -= 1`. Exactly one pointer moves per iteration,
   which is what makes the loop terminate. **On unsorted input these two branches discard the
   answer** and the function reports no pair at all.
5. Past the loop the pointers met with no match: return `(-1, -1)`, a pair of indices matching
   the success shape.

```python
def two_sum_sorted(arr, target):
    """Returns indices (0-based) of two elements that sum to target, or (-1, -1)."""
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        s = arr[lo] + arr[hi]
        if s == target:
            return (lo, hi)
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return (-1, -1)

def test_two_sum():
    assert two_sum_sorted([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum_sorted([1, 2, 3, 4, 5], 8) == (2, 4)
    assert two_sum_sorted([1, 2, 3], 10) == (-1, -1)
    assert two_sum_sorted([], 9) == (-1, -1)
    assert two_sum_sorted([5], 10) == (-1, -1)  # no pairing with itself
    assert two_sum_sorted([3, 3], 6) == (0, 1)  # equal values, distinct indices
    # two valid pairs: the outermost is reached first
    assert two_sum_sorted([1, 3, 3, 5], 6) == (0, 3)
    # precondition violated: unsorted input misses 1 + 2 = 3
    assert two_sum_sorted([3, 1, 2], 3) == (-1, -1)

test_two_sum()
```

## Remove Duplicates In-Place

A list cannot lose an element without shifting everything behind it, so deleting duplicates
where they sit costs O(n²) of memory movement. Reframe: delete nothing, and ask **"what is the
shortest prefix that holds the answer, and can I build it in the space I am already reading?"**

Two indices moving the same way with two different jobs. `fast` is the next element to read,
and it reads every one. `slow` is the last index of the answer written so far, so
`arr[:slow + 1]` is the finished part and `arr[slow]` is the most recently kept value. That
second identity is the one the comparison uses.

Because the input is sorted, equal values are adjacent, so "is `arr[fast]` new?" is answerable
by looking at one element. `arr[slow]` is the only value `arr[fast]` could duplicate.

Writing into the array being read is safe because `slow` starts one behind `fast` and advances
at most once per step, so `slow <= fast` always holds. Every write lands on a slot the scan has
already read, and no unread input is ever clobbered.

```
[1, 1, 2, 2, 3, 4, 4]      before
[1, 2, 3, 4, 3, 4, 4]      after, return 4
 ^^^^^^^^^^  ^^^^^^^
 the answer  stale, ignored
```

Everything past the returned length is leftover junk and the caller is expected to ignore it.
That is the standard in-place-array convention (it is how the C++ `std::unique` idiom works
too), since a list cannot be shortened without moving memory.

Sortedness is load-bearing in a specific way: the test catches *runs* of equal values, so an
out-of-order repeat sails through. `[1, 2, 1]` returns 3 and leaves `[1, 2, 1]` as the answer,
a duplicate in the output and no complaint. Deduplicating unsorted input needs a set, O(n)
space, or a sort first, O(n log n).

The empty guard is about the return value, not the loop: with `arr == []` the loop body never
runs and nothing crashes, but `slow + 1` would claim one element in an empty list. A singleton
needs no case at all, since the loop does not run and `slow + 1` is already 1. All duplicates,
`[2, 2, 2]`, never advances `slow`, so nothing is written, the array is untouched, and the
answer is 1.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `if not arr: return 0`. **The guard is for step 6, not the loop** - on an empty list the
   return would otherwise claim one element that is not there.
2. `slow = 0`, keeping the first element unconditionally: a one-element prefix cannot hold a
   duplicate.
3. `for fast in range(1, len(arr))` - start at 1, since `fast` has to stay ahead of `slow`.
4. Act only on a difference, `if arr[fast] != arr[slow]`. Equal means already kept, so skip and
   let `fast` move on alone.
5. Advance, then write: `slow += 1` and only then `arr[slow] = arr[fast]`. **Writing before
   advancing overwrites the value just kept**, and the result is a silently wrong array rather
   than a crash.
6. Return `slow + 1`, converting a last-used index into a count. Everything from that length
   onwards is stale.

```python
def remove_duplicates(arr):
    """Returns new length. arr[:length] contains unique elements."""
    if not arr:
        return 0
    slow = 0
    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]
    return slow + 1

def test_remove_dups():
    arr = [1, 1, 2, 2, 3, 4, 4]
    length = remove_duplicates(arr)
    assert length == 4
    assert arr[:length] == [1, 2, 3, 4]
    assert arr == [1, 2, 3, 4, 3, 4, 4]  # the tail is left as junk

    assert remove_duplicates([]) == 0
    assert remove_duplicates([1]) == 1

    arr = [2, 2, 2]
    assert remove_duplicates(arr) == 1
    assert arr == [2, 2, 2]  # slow never moves, so nothing is written

    # precondition violated: unsorted input keeps a duplicate
    arr = [1, 2, 1]
    length = remove_duplicates(arr)
    assert length == 3
    assert arr[:length] == [1, 2, 1]

test_remove_dups()
```

## Container With Most Water

**Problem:** each number is the height of a vertical line standing on the x-axis. Pick two
lines; together with the axis they hold water. The amount is limited by the *shorter* of the
two, so it is `min(left, right) × distance between them`. Find the maximum.

`[1, 8, 6, 2, 5, 4, 8, 3, 7]` → `49` (the 8 at index 1 and the 7 at index 8: `min(8,7) × 7`)

Area is `min(left, right) × width`, so the two ends are where the width term is largest and
every move inward gives some of it away for good. Reframe the search accordingly: not "which
pair is best?" but **"which of these two walls can I prove is finished?"**

`lo` and `hi` are the two walls being scored, and since the sweep only moves inward they are
also the widest pair not yet scored. `best` is the largest area proved so far.

Take the shorter of the two, say `lo`. Every *other* pair still available to it is narrower,
because `hi` is its farthest remaining partner, and none can be deeper, because `min` caps the
depth at `heights[lo]` whatever partner it gets. Narrower and no deeper: every remaining pair
using the shorter wall is at most the area just scored. The shorter wall is finished, and that
is why it is the one to discard.

Moving the taller wall proves nothing. The shorter wall sets `min`, so the depth cannot improve
while the width strictly shrinks, and the pairs being thrown away were never bounded. Do it
anyway and the sweep walks straight past the answer: on the array above, always moving the
taller wall returns `8` instead of `49`.

The failure is quiet because every step still scores a legal pair:

```
wrong rule: always move the taller wall

lo=0, h=1   hi=8, h=7   width 8   area 8
lo=0, h=1   hi=7, h=3   width 7   area 7
                        ...
lo=0, h=1   hi=1, h=8   width 1   area 1
```

`lo` never moves because its height 1 is shorter than every partner. It caps every
area at the shrinking width, so the areas are `8, 7, ..., 1` and `best` stays 8.
The true pair, indices 1 and 8, is never considered.

Ties settle themselves. Equal walls cap the depth identically, so the argument above holds for
each of them and either may go. The code tests `heights[lo] < heights[hi]`, which sends a tie
down the `else` branch and moves `hi`; writing `<=` moves `lo` instead and the answer is
unchanged. Both walls being finished, moving both at once is also safe, an optimization this
version skips.

Note what is *not* claimed: the best pair is not found by walking towards it. The scan only
ever discards pairs it has proved cannot beat what it has seen, and the running maximum keeps
whatever survived.

Fewer than two lines means no pair exists, `lo < hi` fails on entry, and `best` stays `0`. `0`
is also a genuine answer, as `[0, 0]` shows, so there is no sentinel here and nothing for a
caller to distinguish.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `lo, hi = 0, len(heights) - 1` and `best = 0`. **`best = 0` is a real answer, not a
   sentinel**, which is why empty input needs no guard.
2. `while lo < hi`, strictly: a wall holds no water against itself.
3. Score the pair before moving anything:
   `area = min(heights[lo], heights[hi]) * (hi - lo)`, then `best = max(best, area)`.
   **Move first and the widest pair never gets scored.**
4. `if heights[lo] < heights[hi]: lo += 1` else `hi -= 1`. The shorter wall is the one that
   goes. **Moving the taller wall is the plausible wrong turn**, since it looks like chasing a
   deeper pair.
5. Return `best`, a running maximum with no conversion.

```python
def max_water(heights):
    lo, hi = 0, len(heights) - 1
    best = 0
    while lo < hi:
        area = min(heights[lo], heights[hi]) * (hi - lo)
        best = max(best, area)
        if heights[lo] < heights[hi]:
            lo += 1
        else:
            hi -= 1
    return best

def test_max_water():
    assert max_water([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert max_water([1, 1]) == 1
    assert max_water([]) == 0          # no pair exists
    assert max_water([5]) == 0
    assert max_water([8, 8]) == 8      # tie: either wall may go
    assert max_water([6, 6, 6, 6]) == 18  # all ties, the widest pair wins
    assert max_water([0, 0]) == 0      # 0 is an answer, not a failure

test_max_water()
```

## Fixed-Size Sliding Window: Max Sum of k Elements

Recomputing each window from scratch re-adds the k-1 elements the previous window already
counted - O(n × k) for information you already had. Reframe: **a fixed width means the left
edge is not a decision.** It is `i - k + 1`, forced by the right edge. Nothing has to be
chosen, so nothing has to be searched, and all that is left is to track what changed.

`window_sum` is the sum of the k elements ending at the element just processed, and `best` is
the largest such sum seen. Consecutive windows differ by exactly two elements, so one step is
a rotation: add the element arriving on the right, subtract the one falling off the left. Over
the whole run each element is added once and subtracted once.

Note what this section does *not* assume: nothing about order, and nothing about sign. There is
no discard argument to protect here, so negative values are perfectly fine, which stops being
true of the variable-size window below.

```
[1, 4, 2, 10, 2, 3, 1, 0, 20]   k = 4

window [1, 4, 2, 10]      sum 17
+2  -1     [4, 2, 10, 2]  sum 18
+3  -4     [2, 10, 2, 3]  sum 17
+1  -2     [10, 2, 3, 1]  sum 16
+0  -10    [2, 3, 1, 0]   sum 6
+20 -2     [3, 1, 0, 20]  sum 24   ← best
```

Seeding `best` with the first window rather than with 0 is load-bearing. On all-negative input
a zero seed reports a window that does not exist: `[-2, -3]` with `k = 2` gives `-5` as
written, and `0` with the seed changed.

The `n < k` guard covers one bad input and no more, and `-1` is a weak sentinel because it is
also a legitimate answer: `max_sum_k([-5, -1, -3], 1)` returns `-1` for the true maximum,
indistinguishable from "the window does not fit". A caller that must tell those apart wants
`None` or an exception. Past the guard, `k = 0` returns `0`, the sum of an empty window, and a
negative `k` sends `arr[i - k]` off the end into `IndexError`.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `n = len(arr)`, then `if n < k: return -1`. **Only `k > n` is guarded**: `k == 0` returns 0
   and a negative `k` raises `IndexError` from step 3.
2. Seed with the only full sum in the function, `window_sum = sum(arr[:k])`, then
   `best = window_sum`. **Seeding `best = 0` breaks all-negative input.**
3. `for i in range(k, n)`: `window_sum += arr[i] - arr[i - k]`. `i` is the element entering,
   `i - k` the one falling out of the back.
4. `best = max(best, window_sum)`, after the update, never before it.
5. Return `best`, a sum, no conversion. **An off-by-one in `i - k` returns plausible wrong
   numbers rather than crashing**, so check it once against a recomputed
   `sum(arr[i - k + 1:i + 1])` instead of by eye.

```python
def max_sum_k(arr, k):
    """Maximum sum of k consecutive elements."""
    n = len(arr)
    if n < k:
        return -1
    window_sum = sum(arr[:k])
    best = window_sum
    for i in range(k, n):
        window_sum += arr[i] - arr[i - k]  # slide: add new, remove old
        best = max(best, window_sum)
    return best


def test_max_sum_k():
    # windows of 4: 17, 18, 17, 16, 6, 24 - best is [3, 1, 0, 20]
    assert max_sum_k([1, 4, 2, 10, 2, 3, 1, 0, 20], 4) == 24
    assert max_sum_k([100, 200, 300, 400], 2) == 700
    # k larger than the array
    assert max_sum_k([1, 2], 5) == -1
    # k equal to the whole array
    assert max_sum_k([1, 2, 3], 3) == 6
    assert max_sum_k([7], 1) == 7
    # negatives are fine, and expose the sentinel: -1 here is a real maximum
    assert max_sum_k([-5, -1, -3], 1) == -1
    assert max_sum_k([-2, -3], 2) == -5  # a zero-seeded best would say 0
    # k = 0 slips past the guard: the empty window
    assert max_sum_k([1, 2, 3], 0) == 0


test_max_sum_k()
```

## Variable-Size Sliding Window: Smallest Subarray with Sum ≥ Target

Reframe: for a given right end, the shortest qualifying window is the one whose start is as far
right as possible. So ask, for every `right`, **"how far right can the start go while the sum
still reaches the target?"** Call that furthest start `s(right)`; the answer to the problem is
the smallest `right - s(right) + 1`.

Two facts about `s` make one forward pass enough, and both come from the values being
non-negative:

1. Shrinking a window never raises its sum, so for a fixed `right` the qualifying starts are a
   prefix `0..s(right)`. Once shrinking has failed it keeps failing, so a `while` that stops at
   the first failure has landed exactly on `s(right)`.
2. Extending a window rightwards never lowers its sum, so a start that qualified at `right`
   still qualifies at `right + 1`, and `s` never decreases. That is what lets `left` stay where
   it is between iterations instead of rewinding.

The state: `window_sum` is the sum of `arr[left..right]`, `left` is the leftmost index still
inside the window, and `best` is the shortest qualifying length seen. The inner `while` records
`right - left + 1` for every start from `left` up to `s(right)` and exits with
`left = s(right) + 1`. Some of what it records is longer than necessary, which is harmless for
a minimum, and the shortest window for this `right` is always among them. The diagram at the
top of the notebook traces this on `[2, 3, 1, 2, 4, 3]` with target 7.

The nested `while` is not a second pass: `left` only ever moves forward, so across the whole
run each element is added once and removed once - O(n) total, the same amortized argument as
the monotonic stack.

Non-negative, not strictly positive, is the real requirement. Zeros preserve both facts, the
sums simply fail to move, and `[0, 0, 5]` with target 5 correctly returns 1. A single negative
value breaks fact 1 and the `while` then stops too early: `[1, -1, 5]` with target 5 returns 3
even though `[5]` alone qualifies with length 1. Removing the `1` dropped the sum to 4, the
loop gave up, and removing the `-1` next would have pushed it back to 5. Prefix sums are the
tool once values can be negative.

The target has to be positive as well, and nothing checks it. At `target <= 0` the empty window
already qualifies, so the inner `while` has no way to fail, and `left` walks off the end of the
array into `IndexError`.

**Time:** O(n) &nbsp; **Space:** O(1)

**Recipe**

1. `best = math.inf`, `window_sum = 0`, `left = 0`. **`best` cannot start at 0**, which is
   smaller than every real length, so `min` would never replace it. Anything above `n` works;
   `inf` says "nothing yet" plainly.
2. `for right in range(n)`: `window_sum += arr[right]`. The only place the window grows, one
   element per step.
3. Then a **`while`**, not an `if`: while `window_sum >= target`, record first,
   `best = min(best, right - left + 1)`. **Recording after the shrink measures a window that
   may no longer qualify.**
4. Shrink in this order: `window_sum -= arr[left]`, then `left += 1`. Reversed, it subtracts
   the wrong element and `window_sum` stops describing the window.
5. **An `if` here returns a too-long window.** One large element can leave several successive
   shrinks all still qualifying, and an `if` stops after the first: `[2, 3, 1, 2, 4, 3]` with
   target 7 gives 4 instead of 2, and `[1, 2, 3, 50]` with target 50 gives 4 instead of 1.
6. Return `best if best != math.inf else 0`, converting "never qualified" into 0.
   **A `target` of 0 or less is not supported input** and raises `IndexError` from step 4.

```python
import math

def min_subarray_sum(arr, target):
    """Returns length of smallest subarray with sum >= target, or 0 if none."""
    n = len(arr)
    best = math.inf
    window_sum = 0
    left = 0
    for right in range(n):
        window_sum += arr[right]
        while window_sum >= target:
            best = min(best, right - left + 1)
            window_sum -= arr[left]
            left += 1
    return best if best != math.inf else 0

def test_min_subarray():
    assert min_subarray_sum([2, 3, 1, 2, 4, 3], 7) == 2  # [4, 3]
    assert min_subarray_sum([1, 1, 1, 1], 10) == 0       # impossible
    assert min_subarray_sum([1, 4, 4], 4) == 1            # [4]
    assert min_subarray_sum([], 5) == 0
    assert min_subarray_sum([5], 5) == 1                  # exactly the target
    assert min_subarray_sum([4], 5) == 0
    assert min_subarray_sum([100], 5) == 1                # overshooting is fine
    assert min_subarray_sum([1, 1, 1], 1) == 1            # duplicates
    assert min_subarray_sum([0, 0, 5], 5) == 1            # zeros are allowed
    # precondition violated: one negative stops the shrink early - [5] is 1
    assert min_subarray_sum([1, -1, 5], 5) == 3
    # precondition violated: target <= 0 walks left off the end
    try:
        min_subarray_sum([1, 2], 0)
        raise AssertionError('expected IndexError')
    except IndexError:
        pass

test_min_subarray()
```

## Longest Substring Without Repeating Characters

Reframe: for a given right end, ask **"what is the earliest start that keeps the window
duplicate-free?"** The longest valid substring ending at `right` begins exactly there, and that
start only ever moves right, which is what makes one forward pass enough.

The state: `seen` holds exactly the characters currently inside the window, `left` is the
leftmost index inside it, and `best` is the longest valid length so far. The invariant worth
memorizing is `seen == set(s[left:right])` at the top of each iteration, the window as it
stands *before* the arriving character is admitted. Every `add` and `remove` exists to keep
that true, and the duplicate test is only trustworthy while it is.

`s[right] in seen` means the window already holds an earlier copy of that character, at some
index `d` with `left <= d < right`. Every window containing both copies is invalid, so the
start has to end up past `d`. It cannot stop short of `d + 1`, and it has no reason to go
further, so `d + 1` is exactly where it belongs.

A set holds no positions, so the loop cannot jump there; it walks, dropping `s[left]` one
character at a time until the offending copy is gone. Dropping characters that were not the
offender is not waste, because everything dropped on the way sits to the left of `d` and had to
leave anyway. In `'abba'` the arriving `'b'` at index 2 evicts `'a'` before it reaches the `'b'`
at index 1, and `'a'` was never going to survive a start past index 1. (Storing each
character's last index in a dict instead lets `left` jump in one step, at the cost of keeping
positions around.)

```
'pwwkew'

right=0 'p'   window 'p'      best 1
right=1 'w'   window 'pw'     best 2
right=2 'w'   duplicate → drop 'p' (left=1), drop 'w' (left=2)
              window 'w'      best 2
right=3 'k'   window 'wk'     best 2
right=4 'e'   window 'wke'    best 3   ← best
right=5 'w'   duplicate → drop 'w' (left=3)
              window 'kew'    best 3
```

Order is load-bearing: shrink first, then add. Add `s[right]` before the `while` and the test
can no longer tell a duplicate from the character just inserted, so the window drains to
nothing on every character and the function returns 0 for every input. It does not hang, which
is what makes it worth naming.

Empty and singleton inputs need no guard. `''` never enters the loop and `best = 0` is the true
answer rather than a sentinel; `'bbbbb'` shrinks on every step and settles at 1. Since
`right - left + 1` counts a closed range, both ends are included.

Same skeleton as `min_subarray_sum` with the validity test inverted: there the window shrinks
while it *is* valid, to find a minimum; here it shrinks while it is *not* valid, to find a
maximum.

**Time:** O(n) - `left` and `right` each traverse the string once &nbsp;
**Space:** O(min(n, alphabet size))

**Recipe**

1. `seen = set()`, `left = 0`, `best = 0`. `best = 0` is the correct answer for `''`, so no
   empty-input guard is needed.
2. `for right in range(len(s))`, and shrink before adding:
   `while s[right] in seen: seen.remove(s[left]); left += 1`.
3. **Adding `s[right]` before the `while` breaks the duplicate test** and returns 0 for every
   input, silently.
4. Remove and advance together, `seen.remove(s[left])` then `left += 1`, so `seen` never stops
   being exactly the window's contents.
5. `seen.add(s[right])`, then `best = max(best, right - left + 1)`. Record after adding, since
   the new character belongs to the window being measured.
6. Return `best`. `right - left + 1` already converted two inclusive indices into a count.

```python
def longest_unique_substr(s):
    """Returns length of longest substring without repeating characters."""
    seen = set()
    best = 0
    left = 0
    for right in range(len(s)):
        while s[right] in seen:
            seen.remove(s[left])
            left += 1
        seen.add(s[right])
        best = max(best, right - left + 1)
    return best

def test_longest_unique():
    assert longest_unique_substr('abcabcbb') == 3  # 'abc'
    assert longest_unique_substr('bbbbb') == 1     # 'b'
    assert longest_unique_substr('pwwkew') == 3    # 'wke'
    assert longest_unique_substr('') == 0
    assert longest_unique_substr('a') == 1
    assert longest_unique_substr('abba') == 2      # 'ab', then 'ba'
    assert longest_unique_substr('tmmzuxt') == 5   # 'mzuxt'
    assert longest_unique_substr('dvdf') == 3      # 'vdf'

test_longest_unique()
```
