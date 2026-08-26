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

# Monotonic Stack

A stack that maintains elements in sorted order (increasing or decreasing). When pushing a new element, pop all elements that violate the monotonic property.

**Key insight:** Each element is pushed and popped at most once → O(n) total despite the inner while loop.

**When to use:** Problems asking for the **next greater/smaller element**, or **nearest larger/smaller** to the left or right.

| Pattern | Stack type | Pop when |
|---------|-----------|----------|
| Next greater element | Decreasing | top <= current |
| Next smaller element | Increasing | top >= current |

**Time:** O(n) &nbsp; **Space:** O(n)

> **Mental model.** The stack holds exactly the elements that are still waiting for an
> answer, and it stays sorted because of what arriving elements do to it. A new element
> answers everyone it beats and disqualifies them permanently, since any element further
> away would meet the new one first. So the inner loop is not extra work being done, it is
> elements leaving for good.
>
> **Load-bearing:** every element is pushed once and popped at most once, which is the only
> reason a nested loop costs O(n) rather than O(n squared). The moment a discarded element
> could come back, or the scan could revisit a position, that argument dies and the bound
> reverts to quadratic.


# Next Greater Element

**Problem:** Given an array, for each element find the first element to its **right** that is
greater than it. Report -1 where no such element exists.

`[4, 5, 2, 25]` → `[5, 25, 25, -1]`

**Why scan right to left?** The answer for a position always lies to its *right*. Walk the
array backwards and you have already seen every element that could possibly be an answer
before you need it, so the work becomes bookkeeping: keep the useful ones, throw the rest
away.

What the stack is for, then:

- **It holds only positions still waiting for an answer**, with values decreasing as you go
  up. So the top is the smallest thing still in play.
- **The top is the answer** for an arriving element, once everything not bigger than it has
  been removed - it is the nearest survivor, and nearest is what the problem asks for.
- **Removing is safe because those elements are unreachable, not just unhelpful.** An
  arriving element that is at least as big is also *nearer*, so anything further left meets
  the arriving element first and can never see past it. "At least as big" includes equal,
  because an answer has to be strictly greater.

```
arr = [4, 5, 2, 25]     stack holds positions, printed as values, top on the right

i=3  arr[3]=25   stack empty       -> result[3] = -1    push 25   [25]
i=2  arr[2]=2    top 25 >  2       -> result[2] = 25    push 2    [25, 2]
i=1  arr[1]=5    top  2 <= 5       -> pop it, gone for good       [25]
                 top 25 >  5       -> result[1] = 25    push 5    [25, 5]
i=0  arr[0]=4    top  5 >  4       -> result[0] = 5     push 4    [25, 5, 4]

result: [5, 25, 25, -1]
stack:  [25, 5, 4]      still decreasing upward, as it was the whole way
```

The inner loop looks like it should make this quadratic, but count the work across the whole
scan rather than at a single position. Every element is pushed exactly once, when the scan
reaches it, so there are n pushes in total. And a discarded element is gone permanently -
once it loses out it never returns to the stack. Every pop therefore consumes a distinct push,
which caps the total pops, and with them the total inner-loop work, at n:

```
total pops  <=  total pushes  =  n
```

So the scan costs n steps plus at most n pops - O(n). The two loops don't multiply because
they're coupled through the stack: a position can only discard many elements if earlier
positions piled them up, and that cost was already paid when they were pushed. The pops are
pre-paid.

The extremes make it concrete. An increasing array never discards anything, while an array
that forces repeated discarding can only afford one pop per position:

```
[1, 2, 3, 4, 5]   each arriving element is smaller than the top, so nothing
                  is ever discarded                        → 0 pops

[1, 1, 1, 1, 9]   each arriving 1 discards the previous 1 and takes its place
                                                           → 3 pops, 1 per position
```

A position that discards a lot leaves the stack short, so the next position finds little left
to discard. You can pay heavily at one position or lightly at many, but the budget for the
whole scan is capped at n.

This is the same accounting as the [dynamic array
analysis](../analysis/05-amortized-analysis.md) - a single append may trigger an O(n)
resize, yet n appends still cost O(n) because the cheap appends pre-pay for it. The argument
rests on that invariant: if a discarded element could ever return to the stack, or the scan
could revisit a position, "popped at most once" fails and the bound reverts to O(n²).

**Time:** O(n) &nbsp; **Space:** O(n)

```python
def next_greater(arr):
    """For each element, find next greater to the right. Time: O(n)"""
    n = len(arr)
    result = [-1] * n
    stack = []  # indices of candidates still awaiting an answer; values decrease upward
    for i in range(n - 1, -1, -1):  # right to left, so answers are already on the stack
        # arr[i] is nearer and at least as large, so these can never be anyone's answer again
        while stack and arr[stack[-1]] <= arr[i]:
            stack.pop()
        if stack:
            result[i] = arr[stack[-1]]  # nearest survivor is the first greater element
        stack.append(i)  # one push per element - this is what bounds the total pops
    return result

def test_next_greater():
    assert next_greater([4, 5, 2, 25]) == [5, 25, 25, -1]
    assert next_greater([13, 7, 6, 12]) == [-1, 12, 12, -1]
    assert next_greater([3, 2, 1]) == [-1, -1, -1]

test_next_greater()
```

# Next Smaller Element

**Problem:** Given an array, for each element find the first element to its **right** that is
smaller than it. Report -1 where no such element exists.

`[4, 8, 5, 2, 25]` → `[2, 5, 2, -1, -1]`

The mirror image: the same scan with the comparison reversed. An arriving element now
discards tops that are greater than or equal to it, so the survivors *increase* as you go up
instead of decreasing, and the top is the largest thing still in play.

That symmetry is the useful takeaway - "nearest larger" and "nearest smaller" are the same
algorithm with the comparison flipped, and scanning left to right instead of right to left
flips "next" to "previous". Four problems, one template.

**Time:** O(n) &nbsp; **Space:** O(n)

```python
def next_smaller(arr):
    """For each element, find next smaller to the right. Time: O(n)"""
    n = len(arr)
    result = [-1] * n
    stack = []  # indices of candidates still awaiting an answer; values increase upward
    for i in range(n - 1, -1, -1):  # right to left, so answers are already on the stack
        # arr[i] is nearer and no larger, so these can never be anyone's answer again
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        if stack:
            result[i] = arr[stack[-1]]  # nearest survivor is the first smaller element
        stack.append(i)
    return result

def test_next_smaller():
    assert next_smaller([4, 8, 5, 2, 25]) == [2, 5, 2, -1, -1]
    assert next_smaller([1, 2, 3]) == [-1, -1, -1]

test_next_smaller()
```

# Application: Daily Temperatures

**Problem:** Given daily temperatures, return for each day **how many days you must wait** for
a warmer temperature. Report 0 for days with no warmer day ahead.

`[73, 74, 75, 71, 69, 72, 76, 73]` → `[1, 1, 4, 2, 1, 1, 0, 0]`

Same question as next-greater, but the answer is the **distance** rather than the value.

That one change makes it natural to flip the scan direction. Going left to right, each
arriving day is the answer for every colder day still waiting on the stack, and because the
stack holds positions rather than temperatures, the wait is simply the gap between the two
positions. Days still waiting when the scan ends never found a warmer day and keep their 0.

```
temps = [73, 74, 75, 71, 69, 72, 76, 73]
                                          stack holds indices, top on the right
                                          the answer is a distance, so it is i - j

i=0 (73)  push 0                                        stack [0]
i=1 (74)  74 > 73 -> pop 0, result[0] = 1-0 = 1          stack []
          push 1                                        stack [1]
i=2 (75)  75 > 74 -> pop 1, result[1] = 2-1 = 1          stack []
          push 2                                        stack [2]
i=3 (71)  push 3                                        stack [2, 3]
i=4 (69)  push 4                                        stack [2, 3, 4]
i=5 (72)  72 > 69 -> pop 4, result[4] = 5-4 = 1          stack [2, 3]
          72 > 71 -> pop 3, result[3] = 5-3 = 2          stack [2]
          push 5                                        stack [2, 5]
i=6 (76)  76 > 72 -> pop 5, result[5] = 6-5 = 1          stack [2]
          76 > 75 -> pop 2, result[2] = 6-2 = 4          stack []
          push 6                                        stack [6]
i=7 (73)  push 7                                        stack [6, 7]
                    6 and 7 are never popped, so they keep result 0

result: [1, 1, 4, 2, 1, 1, 0, 0]
```

**Time:** O(n) &nbsp; **Space:** O(n)

```python
def daily_temperatures(temps):
    """Days until warmer temperature. Time: O(n)"""
    n = len(temps)
    result = [0] * n  # days that never find a warmer one keep 0
    stack = []  # indices of days still waiting; temperatures decrease upward
    for i in range(n):  # left to right: each new day resolves the colder days behind it
        while stack and temps[i] > temps[stack[-1]]:
            j = stack.pop()   # day j has found its warmer day
            result[j] = i - j  # positions on the stack turn the answer into a subtraction
        stack.append(i)
    return result

def test_daily_temps():
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    assert daily_temperatures([30, 40, 50, 60]) == [1, 1, 1, 0]
    assert daily_temperatures([30, 20, 10]) == [0, 0, 0]

test_daily_temps()
```

# Application: Largest Rectangle in Histogram

**Problem:** Given bar heights in a histogram, each bar one unit wide, find the **area of the
largest rectangle** that fits inside. The rectangle must span contiguous bars and cannot exceed
the height of the shortest bar it covers.

`[2, 1, 5, 6, 2, 3]` → `10` (height 5 across the two bars 5 and 6)

Every candidate rectangle is limited by its shortest bar, so ask a different question: for
each bar, **how wide a rectangle can it support at its own height?** It extends until it
meets a shorter bar on either side, so what is needed is the nearest shorter bar left and
right - monotonic stack territory.

The stack keeps increasing heights. A bar shorter than the top means the top's right
boundary has been found, so pop it and settle its rectangle: the height is the popped bar,
and the width runs between its left boundary - the bar now exposed underneath - and the
shorter bar that stopped it.

```
heights = [2, 1, 5, 6, 2, 3] + [0]    the trailing 0 is a sentinel, not real data
                                      stack holds indices, top on the right
                                      `3:6` means index 3, whose bar is 6 tall

i=0  h=2   push                                        stack: 0:2
i=1  h=1   pop 0:2   width 1          area 2           stack: empty
           push                                        stack: 1:1
i=2  h=5   push                                        stack: 1:1  2:5
i=3  h=6   push                                        stack: 1:1  2:5  3:6
i=4  h=2   pop 3:6   width 4-2-1 = 1  area 6           stack: 1:1  2:5
           pop 2:5   width 4-1-1 = 2  area 10  <- best stack: 1:1
           push                                        stack: 1:1  4:2
i=5  h=3   push                                        stack: 1:1  4:2  5:3
i=6  h=0   pop 5:3   width 6-4-1 = 1  area 3           stack: 1:1  4:2
           pop 4:2   width 6-1-1 = 4  area 8           stack: 1:1
           pop 1:1   width 6          area 6           stack: empty

max area: 10, from the bar of height 5 spanning indices 2 and 3
```

The width is index arithmetic, which is why it reads oddly next to the heights: `i` is the
shorter bar that stopped us, `stack[-1]` is the bar now exposed on the left, and the rectangle
fits strictly between the two - hence the `- 1`. When the stack empties there is nothing
shorter to the left at all, so the width is the whole span up to `i`.

Two details that are easy to get wrong:

- The zero-height bar appended to the end is shorter than every real bar, so it forces every
  survivor off the stack to be measured. Without it, a rising histogram like `[1, 2, 3]` would
  finish with bars still on the stack and their rectangles never computed
- When the stack empties during a pop, the bar just removed was the shortest seen so far, so
  nothing bounds it on the left and its rectangle stretches all the way back to the first bar

**Time:** O(n) &nbsp; **Space:** O(n)

```python
def largest_rectangle(heights):
    """Largest rectangle area in histogram. Time: O(n)"""
    stack = []  # indices of bars whose right boundary is unknown; heights increase upward
    max_area = 0
    heights = heights + [0]  # shorter than every bar, so it drains the stack at the end
    for i, h in enumerate(heights):
        # h is the first shorter bar right of the top, fixing that bar's right boundary
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            # left boundary is the bar now exposed; an empty stack means nothing shorter
            # lies to the left, so the rectangle spans everything up to i
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area

def test_largest_rect():
    assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10  # 5×2
    assert largest_rectangle([2, 4]) == 4
    assert largest_rectangle([6, 2, 5, 4, 5, 1, 6]) == 12  # 4×3

test_largest_rect()
```
