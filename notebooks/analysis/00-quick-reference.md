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

# Complexity Quick Reference

A field guide for naming the time and space complexity of unfamiliar code on sight. Condensed from
notebooks [01](01-notation.md)-[05](05-amortized-analysis.md), which carry the derivations.

## What asymptotic analysis is

It answers one question: **as the input grows, how does the amount of work grow?**

Not seconds. Absolute time isn't a property of the algorithm - it shifts with the CPU, the language
and the compiler. The growth rate survives all of them. A quadratic algorithm stays quadratic on
faster hardware; it just needs a bigger input before it becomes unusable.

The quickest intuitive test is to **ask what happens when $n$ doubles**:

| Complexity | Work when $n$ doubles | Feel |
|---|---|---|
| $O(1)$ | unchanged | free |
| $O(\log n)$ | one extra step | scales forever |
| $O(n)$ | doubles | proportional |
| $O(n \log n)$ | slightly more than doubles | the practical ceiling for large inputs |
| $O(n^2)$ | $\times 4$ | fine to a few thousand |
| $O(2^n)$ | squares | only tiny inputs |

Because only growth matters, two mechanical rules reduce any work count to its complexity:

1. **Drop lower-order terms** - $n^2 + n + 6 \rightarrow n^2$
2. **Drop constant factors** - $3n \rightarrow n$

Both are justified in the limit: a lower-order term becomes a vanishing fraction of the total, and a
constant factor leaves the growth rate unchanged. So $\frac{n}{4}$, $2n + 3$ and $100n$ are all
$O(n)$ - one class, differing only by constants we can't measure portably anyway.

> **The caveat that matters in practice:** constants decide *small* inputs, growth decides *large*
> ones. $O(n^2)$ with tiny constants beats $O(n \log n)$ at $n = 20$ - which is exactly why Timsort
> drops to insertion sort on short runs.

> **Rough sizing.** Python runs $\approx 10^7$ simple operations per second. So $n \leqslant 10^5$
> rules out $O(n^2)$ and points at $O(n \log n)$; $n \leqslant 3000$ leaves room for $O(n^2)$;
> $n \leqslant 20$ invites exponential search. Read that backwards and the stated input limit tells
> you the complexity to aim for.


## Case vs notation - two independent axes

**Case = which input you're analyzing.** For a given algorithm and size $n$, different actual inputs
run faster or slower. Picking a case gives you a specific function $T(n)$. This step involves no
$O$, $\Omega$ or $\Theta$ at all.

- **Best case** - the input that makes it fastest
- **Worst case** - the input that makes it slowest
- **Average case** - expected over some distribution of inputs

**Notation = how tightly you bound that function**, once you have it.

- **Big O** - upper bound, "grows no faster than"
- **Big Ω** - lower bound, "grows no slower than"
- **Big Θ** - tight bound, both at once, "grows exactly like"

The choices are independent: you can say "the best case is $O(n^2)$" - true, just a useless loose
bound.

**Why people conflate them:** analyzing the worst case, you usually want the ceiling, so you reach
for $O$. Analyzing the best case, you usually want the floor, so you reach for $\Omega$. That's a
*pairing of convenience*, not a rule.

Linear search in an unsorted array:

| Case | Runtime function | Tightest notation |
|---|---|---|
| Best (item is first) | $T(n) = 1$ | $\Theta(1)$ |
| Worst (item is last or absent) | $T(n) = n$ | $\Theta(n)$ |

Both cases take a *tight* $\Theta$ bound - tightness is unrelated to which case it is.

Quick sort:

| Case | Complexity |
|---|---|
| Worst (bad pivot every time, e.g. sorted input with naive pivot) | $\Theta(n^2)$ |
| Best (pivot always splits evenly) | $\Theta(n \log n)$ |

Both are expressed with $\Theta$ here, but you could state the worst case as $O(n^2)$ alone if all
you wanted was the upper-bound guarantee and you didn't care to prove the matching $\Omega$.

> **Short version:** *case* answers "which input am I plugging in?", *notation* answers "how
> precisely do I want to characterize the resulting function?"
>
> **Worst case is what you quote**, because it's the only guarantee that holds for every input.
> And $\Theta$ doesn't always exist - a function that's constant for odd $n$ and linear for even $n$
> can't be sandwiched by any single $g(n)$. Fix the case first, then the tight bound reappears.

<!-- #region -->
## Time: pattern → complexity

### 1. Single loop → $O(n)$

```python
for i in range(0, n, c):   # c is any constant step
    ...
```

Runs $\frac{n}{c}$ times; the constant drops → $O(n)$.

A loop with a bound that doesn't depend on $n$ (`range(100)`) is $O(1)$, however long the body.

### 2. Nested loops → multiply the bounds

```python
for i in range(n):
    for j in range(n):
        ...
```

$n \times n \rightarrow O(n^2)$.

```python
for i in range(n):
    for j in range(m):
        ...
```

Two *different* input sizes → $O(n \cdot m)$, not $O(n^2)$. Don't collapse different variables into
one.

Triangular / dependent nesting:

```python
for i in range(n):
    for j in range(i, n):
        ...
```

The inner loop shrinks each pass → $n + (n-1) + \dots + 1 = \frac{n(n+1)}{2} \rightarrow O(n^2)$
once the constant drops.

### 3. Counter multiplied or divided → $O(\log n)$

```python
i = 1
while i < n:
    i *= 2      # or i //= 2
```

$\log_2 n$ iterations → $O(\log n)$.

> **Multiplicative step is the log signal; additive step (`i += c`) is the linear signal.**

The base of the log never matters - bases differ by a constant factor. Squaring the counter
(`i = i ** 2`) applies the log twice → $O(\log \log n)$.

### 4. Halving inside a linear loop → $O(n \log n)$

```python
for i in range(n):
    j = 1
    while j < n:
        j *= 2
```

$n$ outer $\times \log n$ inner → $O(n \log n)$. Also the signature of the efficient sorts and of
divide-and-conquer with linear merge work.

### 5. Sequential blocks → add, then keep the dominant term

```python
for i in range(n):          # O(n)
    ...
for i in range(n):
    for j in range(n):      # O(n²)
        ...
```

$O(n) + O(n^2) \rightarrow O(n^2)$.

### 6. Loop bound tied to the input's value, not its size

```python
for i in range(2, n):
    if n % i == 0: ...
```

$O(n)$ - the loop runs $n$ times whatever the body does. Trial division only up to $\sqrt{n}$ is
$O(\sqrt{n})$.

> Careful with the meaning of $n$ here: it's the input *value*, not the input's size in bits. An
> algorithm linear in a numeric value is *pseudo-polynomial* - knapsack's $O(n \cdot W)$ is the
> classic case, fast for small $W$ and exponential in the bit length of $W$.

### 7. Built-in operations - know their real cost

Where people lose points, by assuming $O(1)$ too liberally.

| Operation | Cost |
|---|---|
| `lst[i]`, `len(lst)`, `lst.append(x)`, `lst.pop()` | $O(1)$ (append amortized) |
| `lst.insert(0, x)` / `lst.pop(0)` | $O(n)$ - shifts everything; use `deque` |
| `x in lst` | $O(n)$ |
| `x in s` / `x in d` (set/dict) | $O(1)$ average |
| `sorted(lst)`, `lst.sort()` | $O(n \log n)$, $O(n)$ on nearly sorted (Timsort is adaptive) |
| `s += c` in a loop | $O(n)$ per op → $O(n^2)$ total; use `"".join(parts)` |
| `lst[a:b]` (slice) | $O(b - a)$ - it copies |
| `min`, `max`, `sum`, `count`, `index` | $O(n)$ |
| `heapq.heappush/heappop` / `heapify` | $O(\log n)$ / $O(n)$ |
| `bisect_left/right` / `insort` | $O(\log n)$ / $O(\log n)$ + $O(n)$ shift |

### Checklist

1. **How many times does each loop run**, in terms of $n$ - additive step → linear, multiplicative
   step → log.
2. **Nested or sequential?** Nested → multiply. Sequential → add, keep the max.
3. **Is the inner bound dependent on the outer variable?** → sum it; usually still $O(n^2)$-ish.
4. **Recursive?** Write the recurrence, then pattern-match or apply the Master Theorem.
5. **Check every built-in call inside a loop** - a hidden $O(n)$ operation inside an $O(n)$ loop
   silently makes it $O(n^2)$. This is the #1 way candidates misjudge complexity.

Deeper: [02 Common Loops](02-common-loops.md)
<!-- #endregion -->

<!-- #region -->
## Recursion: estimate it from the tree

**Write the recurrence first**, mechanically:

$$T(n) = (\text{number of recursive calls}) \times T\!\left(\frac{n}{\text{shrink factor}}\right) + (\text{work outside the calls})$$

Then read the answer off the tree, or pattern-match the table below, or apply the Master Theorem.

Recurrences are precise but not intuitive. To *see* the result, draw the tree and ask three
questions:

1. **How many levels?** - how many times the input shrinks before hitting the base case (depth)
2. **How much work per level, in total?**
3. **Multiply**, when work per level is roughly constant across levels

### Case 1 - one call, shrinking by a fraction

```python
def f(n):
    if n <= 1: return
    f(n // 2)
```

Depth $= \log n$, $O(1)$ per level → $O(\log n)$. Binary search's shape: one call, input divided →
$\log n$.

### Case 2 - one call, shrinking by a constant

```python
def f(n):
    if n <= 0: return
    f(n - 1)
```

Depth $= n$, $O(1)$ per level → $O(n)$.

### Case 3 - two calls, each on half the input

```python
def f(n):
    if n <= 1: return
    f(n // 2)
    f(n // 2)
```

The tree *doubles* in width per level while the pieces *halve* in size. Count work level by level,
not call by call - with $O(n)$ work per call:

- Level 0: $1$ call of size $n \rightarrow n$
- Level 1: $2$ calls of size $\frac{n}{2} \rightarrow n$
- Level 2: $4$ calls of size $\frac{n}{4} \rightarrow n$

Every level totals $O(n)$ because branching and shrinking cancel. Levels $= \log n$, so
$O(n \log n)$. Merge sort exactly.

With only $O(1)$ work per call, the leaves dominate instead: $n$ leaves → $O(n)$.

### Case 4 - two calls, barely shrinking

```python
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```

Branching ($2$) beats the shrink rate ($-1$), so work per level explodes rather than staying level.
Depth $\approx n$, width roughly doubles each level → $\approx 2^n$ nodes → $O(2^n)$.

> Shortcut: **branching factor $b$, depth $d$ → total calls $\approx b^d$**, unless the input
> shrinks fast enough to cancel the branching (merge sort, where the two collapse to $n \log n$).
>
> The tight bound for `fib` is actually $\Theta(\varphi^n)$ where
> $\varphi = \frac{1 + \sqrt{5}}{2} \approx 1.618$, since the tree is incomplete. Assuming a full
> tree is what gives the (correct, slightly loose) upper bound $O(2^n)$.

### The most useful mental shortcut

> **Total work $\approx$ (number of leaf calls $\times$ work per leaf) + (work done by internal
> nodes combining results)**

- Cheap combine ($O(1)$) and no shrink-vs-branch cancellation → dominated by the **number of
  leaves** (Fibonacci: $\approx 2^n$).
- Expensive combine ($O(n)$ per level, merge sort) → dominated by **levels $\times$ work per
  level**.

### Pattern table

| Shape | Recurrence | Recognize by | Complexity |
|---|---|---|---|
| 1 call, $n \rightarrow \frac{n}{2}$ | $T(n) = T(\frac{n}{2}) + O(1)$ | halving, no combine work - binary search | $O(\log n)$ |
| 1 call, $n \rightarrow n-1$ | $T(n) = T(n-1) + O(1)$ | decrement, constant work | $O(n)$ |
| 1 call, $n \rightarrow \frac{n}{2}$, $O(n)$ work outside | $T(n) = T(\frac{n}{2}) + O(n)$ | halving + linear scan - quickselect average | $O(n)$ |
| 2 calls, $n \rightarrow \frac{n}{2}$, $O(1)$ work | $T(n) = 2T(\frac{n}{2}) + O(1)$ | branching cancels, leaves dominate | $O(n)$ |
| 2 calls, $n \rightarrow \frac{n}{2}$, $O(n)$ combine | $T(n) = 2T(\frac{n}{2}) + O(n)$ | divide and conquer with linear combine - merge sort | $O(n \log n)$ |
| 1 call, $n \rightarrow n-1$, $O(n)$ work | $T(n) = T(n-1) + O(n)$ | linear work at every level | $O(n^2)$ - quick sort worst case |
| 2 calls, $n \rightarrow n-1$ | $T(n) = 2T(n-1) + O(1)$ | branching, barely shrinking - subsets | $O(2^n)$ |
| 2 calls, uneven decrement | $T(n) = T(n-1) + T(n-2) + O(1)$ | naive Fibonacci | $O(2^n)$ |
| $k$ calls, $n \rightarrow \frac{n}{k}$, $O(n)$ work | $T(n) = kT(\frac{n}{k}) + O(n)$ | $k$-way divide and conquer | $O(n \log n)$ still |

### Master Theorem - the shortcut for the tree

$$T(n) = a \, T\!\left(\frac{n}{b}\right) + O(n^d)$$

Compare $d$ to $\log_b a$:

| Condition | Result | Why |
|---|---|---|
| $d < \log_b a$ | $O(n^{\log_b a})$ | leaves dominate |
| $d = \log_b a$ | $O(n^d \log n)$ | every level does equal work |
| $d > \log_b a$ | $O(n^d)$ | the root dominates |

It only applies to the balanced $\frac{n}{b}$ shape. For uneven splits go back to the tree: if the
work per level shrinks geometrically - $T(n) = T\left(\frac{n}{2}\right) + T\left(\frac{n}{4}\right) + n$,
ratio $\frac{3}{4}$ - the series converges and the root dominates, giving $O(n)$.

### In an interview

Ask, in order: **how many times does the input shrink before the base case** (depth), **how many
calls happen at each step** (branching), **is there extra work besides the calls** (combining,
looping) - that last one decides whether you multiply by levels or just count leaves.

Deeper: [03 Recursion](03-recursion.md)
<!-- #endregion -->

<!-- #region -->
## Space: the field guide

Trips people up more than time, because of one blind spot: **the call stack counts as space.**

### Two buckets

1. **Auxiliary space** - everything beyond the input itself. This is what "space complexity" means
   in an interview unless stated otherwise.
2. **Input space** - the input itself, usually excluded. Any array input is $\Theta(n)$ by
   definition, which is why the auxiliary number is the interesting one.

### 1. No extra structures → $O(1)$

```python
def sum_array(arr):
    total = 0
    for x in arr:
        total += x
    return total
```

A few scalars regardless of $n$ → $O(1)$, even though the loop runs $n$ times. Time and space are
independent axes.

### 2. Structures that scale with the input

```python
def doubled(arr):
    return [x * 2 for x in arr]          # O(n)

def freq_count(arr):
    counts = {}
    for x in arr:
        counts[x] = counts.get(x, 0) + 1  # up to n entries → O(n)
```

An $n \times m$ matrix or DP table → $O(n \cdot m)$.

### 3. Recursion - count the stack

Every call adds a frame that lives until the call returns.

```python
def f(n):
    if n <= 0: return
    f(n - 1)
```

Depth $n$ → $O(n)$ space, with no explicit array anywhere. The iterative equivalent is $O(1)$. This
is the classic "recursion trades space for shorter code."

> **Rule: recursive space $= O(\text{max depth of the call stack})$**, not the total number of
> calls.

- Recursive binary search: depth $\log n$ → $O(\log n)$
- Naive Fibonacci: $O(2^n)$ time but only $O(n)$ space - only one root-to-leaf path is on the stack
  at a time
- Merge sort: $O(\log n)$ stack but $O(n)$ merge buffers → $O(n)$ dominates

### 4. Stack shape

| Pattern | Stack depth | Space |
|---|---|---|
| Linear recursion (1 call, shrink by 1) | $n$ | $O(n)$ |
| Halving recursion (1 call, shrink by $\frac{1}{2}$) | $\log n$ | $O(\log n)$ |
| Binary branching (2 calls, shrink by 1) | $n$ (deepest path) | $O(n)$ - **not $O(2^n)$** |
| Binary branching (2 calls, shrink by $\frac{1}{2}$) + $O(n)$ buffer | $\log n$ stack + buffers | $O(n)$ |

Key insight: **only one path down the tree is live on the stack at any instant** - the rest have
been popped. Branching costs a lot of *time* without necessarily costing much space.

### 5. In-place vs out-of-place

- **In-place** - modifies the input, no new structure proportional to $n$: reversing by swapping,
  quick sort's partitioning → $O(1)$ auxiliary. Quick sort's recursion stack is still $O(\log n)$,
  so don't forget it.
- **Out-of-place** - builds a new structure: merge sort's merge step, converting to a new list/set
  → $O(n)$.

"Can you do this in $O(1)$ space?" almost always means "in-place, and if you recurse, keep the
recursion shallow or make it iterative."

### 6. Memoization / DP → space = size of the memo

```python
def fib(n, memo={}):
    if n in memo: return memo[n]
    if n <= 1: return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]
```

Memo holds up to $n$ entries → $O(n)$, *plus* an $O(n)$ stack. They **add**, not multiply → $O(n)$.

2-D DP (edit distance) is $O(n \cdot m)$ and usually the dominant cost - but if each cell depends
only on the previous row, keep 1-2 rows for $O(m)$ space. Interviewers love this as a follow-up.

### Checklist

1. **Any new array/list/dict/set that grows with the input?** → count its size.
2. **Any recursion?** → count max stack depth, not total calls.
3. **Multiple structures?** → add, then keep the dominant term:
   $O(n) + O(\log n) \rightarrow O(n)$.
4. **Nested structures?** → multiply the dimensions.
5. **Asked for $O(1)$ space?** → look for in-place swaps and pointers, or turning recursion into
   iteration. Note that an explicit stack still costs $O(n)$ - it moves the cost from the call stack
   into a visible data structure rather than removing it. (It does avoid `RecursionError`, since
   Python's default recursion limit is $\approx 1000$ frames.)

### Gotchas interviewers test

- Naive recursive Fibonacci - $O(2^n)$ time, $O(n)$ space, not $O(2^n)$ space
- Merge sort - $O(n \log n)$ time, $O(n)$ space, not $O(n \log n)$ space; merge buffers are reused
  level by level, not stacked all at once
- In-place quick sort - $O(n \log n)$ average time, $O(\log n)$ space from the recursion stack alone
- "I replaced recursion with my own stack" - **you haven't saved space**, only made the $O(n)$
  explicit

Deeper: [04 Space Complexity](04-space-complexity.md)
<!-- #endregion -->

<!-- #region -->
## Amortization

Stop thinking *per operation*, start thinking *per sequence*. The question isn't "how expensive is
this one call?" but "if I do this $n$ times in a row, what's the guaranteed average cost per call?"

Worst-case-per-call is **too pessimistic** when the occasional expensive operation is rare enough to
be paid off by a long run of cheap ones.

### The classic: dynamic array `append`

```python
arr = []
for i in range(n):
    arr.append(i)
```

Most appends drop the value in the next free slot - $O(1)$. Occasionally the array is full, so it
allocates a new one (double the size) and copies everything - that call is $O(\text{current size})$.
Judging by that call alone gives "worst case $O(n)$", which is misleading for what the loop actually
costs.

### Piggy-bank intuition

**Overpay slightly on every cheap operation and stash the credit. When the expensive one arrives,
pay from the bank rather than in the moment.** By the time the array fills and doubles, the cheap
appends since the last resize have banked exactly enough to cover the copy. Nothing ever feels
expensive from the bank's perspective - it was pre-paid gradually.

### Why doubling is the trick

Geometric growth, not arithmetic:

- Resize by **+1 slot** → a resize on every append → genuinely $O(n)$ each, nothing to amortize.
- **Double** → resizes at sizes $1, 2, 4, 8, 16, \dots$ - exponentially rarer as the array grows.
  Copy costs $1 + 2 + 4 + \dots + n$ sum to $\approx 2n$ total, spread over $n$ appends →
  $O(1)$ amortized, even though an individual resize is $O(n)$.

> **Expensive operations become exponentially rarer exactly as fast as they become expensive**, so
> the total stays linear.

### The three formal methods

1. **Aggregate** - total cost of $n$ ops $\div \, n$ (total copying $\approx 2n$ over $n$ appends →
   $O(1)$ each)
2. **Accounting** - the piggy bank: fix a charge per operation, some overpay, some underpay, the
   balance never goes negative
3. **Potential** - the same idea with a potential function $\Phi$ measuring "stored energy" in the
   structure's current state

The accounting framing is almost always enough to explain your reasoning out loud.

### Amortized $\neq$ average case

- **Average case** assumes a *distribution over inputs* - "what if the input is random or typical?"
- **Amortized** is a guarantee over a *sequence of operations on any input* - no randomness or
  typicality assumed.

Hand it an adversarial sequence designed to be nasty and amortized $O(1)$ per append **still
holds**. That's what makes it the stronger guarantee.

### Classic examples

| Structure / op | Occasional expensive op | Amortized |
|---|---|---|
| Dynamic array append (`list`, `vector`) | resize + copy - $O(n)$ | $O(1)$ |
| Dynamic array pop from end | occasional shrink | $O(1)$ |
| Hash table insert | resize + rehash - $O(n)$ | $O(1)$ |
| Union-Find with path compression | occasional long path traversal | $O(\alpha(n))$, practically $O(1)$ |
| Incrementing a binary counter | occasional long carry chain | $O(1)$ |
| Monotonic stack pass | inner while loop pops many | $O(1)$ per element |

> **One-sentence version:** don't judge an operation by its worst moment - judge it by its fair
> share of the total cost across a long sequence, and if expensive moments become rare fast enough,
> that share is small even when individual worst cases aren't.

Deeper: [05 Amortized Analysis](05-amortized-analysis.md)
<!-- #endregion -->
