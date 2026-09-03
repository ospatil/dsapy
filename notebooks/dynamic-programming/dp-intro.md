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

# Dynamic Programming

Dynamic programming is recursion that refuses to answer the same question twice.

Two things have to be true for it to help:

1. A bigger answer can be assembled from smaller answers. The proper name for that is
   **optimal substructure**
2. The same smaller question keeps coming back. That is what **overlapping subproblems**
   means

> **Mental model.** Write the honest recursion first. Its call tree asks the same small
> question over and over, so the tree is huge while the number of *different* questions in it
> is tiny. Everything called "DP" is only bookkeeping that makes sure each different question
> is answered once. The cache or the table is not the idea - it is the receipt.
>
> **Load-bearing:** both properties, together. If the subproblems never repeat there is
> nothing to save, and caching only adds cost. If a bigger answer is not built out of smaller
> answers, the table holds numbers that cannot be combined into the answer you want.

## Two Approaches

| Approach | Direction | Technique |
|----------|-----------|----------|
| Top-down | Start from original problem, recurse down | Memoization (cache results) |
| Bottom-up | Start from smallest subproblems, build up | Tabulation (fill a table) |

These two compute exactly the same numbers. The only real difference is who picks the order.
Top-down lets the recursion discover what it needs, so any order works and unreachable
subproblems are never touched. Bottom-up needs *you* to know an order in which every cell is
already filled before it is read, and it pays that price to drop the recursion entirely.


# Fibonacci

The smallest place the waste is visible. Nothing is wrong with the naive recursion except how
often it asks the same thing.

```
fib(5)
├── fib(4)
│   ├── fib(3)        ← computed again below
│   │   ├── fib(2)
│   │   └── fib(1)
│   └── fib(2)        ← computed again
└── fib(3)            ← same subtree as above
    ├── fib(2)
    └── fib(1)
```

The tree has O(2ⁿ) nodes but only n *distinct* values in it - that gap between "calls made"
and "answers that exist" is what DP eliminates. The four versions below are the same
recurrence with progressively less waste:

| Version | Idea | Time | Space |
|---|---|---|---|
| `fib_naive` | recompute everything | O(2ⁿ) | O(n) call stack |
| `fib_memo` | cache each answer the first time it is computed (top-down) | O(n) | O(n) |
| `fib_tab` | fill a table from the base cases upward (bottom-up) | O(n) | O(n) |
| `fib_opt` | keep only the two values the recurrence actually reads | O(n) | O(1) |

`fib_opt` is worth a second look: `dp[i]` only ever depends on `dp[i-1]` and `dp[i-2]`, so
the full table is dead weight and two variables suffice. Recognising that "the recurrence
only looks k rows back" is the standard route from O(n) to O(1) space - or from O(n×m) to
O(m) for the 2-D problems further down.

**Recipe**

Four versions of one function, each removing a cost the previous one paid.

1. **Naive**: base case `n <= 1`, else the sum of two recursive calls. Write this
   first, always. It is the definition, and every later version is a mechanical
   transformation of it.
2. **Memoised**: same code, plus "if the answer is cached return it, otherwise
   compute and cache". **`memo=None` in the signature and a fresh `{}` inside.
   A `memo={}` default is created once at definition time and shared by every
   call, so results leak between unrelated calls.**
3. **Tabulated**: allocate `dp[0..n]`, seed `dp[0]` and `dp[1]`, then fill
   upward. **The loop runs in the order the recursion would have returned, which
   is what lets the recursion disappear.**
4. **Optimised**: the row only ever reads `i - 1` and `i - 2`, so keep two
   variables instead of the array. `a, b = b, a + b` updates both at once;
   sequential assignment would feed the new `a` into `b`.
5. **The path is always the same:** write the honest recursion, cache it, turn
   the cache into a table, then discard the parts of the table nothing reads.
   Steps 3 and 4 are optional; step 1 is not.

```python
def fib_naive(n):
    """O(2^n) time - exponential due to overlapping subproblems."""
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n, memo=None):
    """Top-down with memoization. O(n) time, O(n) space."""
    if memo is None:
        memo = {}  # a fresh cache per top-level call, not a shared default
    if n <= 1:
        return n
    if n not in memo:
        memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


def fib_tab(n):
    """Bottom-up tabulation. O(n) time, O(n) space."""
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


def fib_opt(n):
    """Space-optimized - the recurrence only looks two steps back. O(1) space."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def test_fib():
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    for i, val in enumerate(expected):
        assert fib_naive(i) == val
        assert fib_memo(i) == val
        assert fib_tab(i) == val
        assert fib_opt(i) == val
    # the memo version scales where the naive one cannot
    assert fib_memo(90) == 2880067194370816120
    assert fib_opt(90) == fib_memo(90)


test_fib()
```

# Coin Change (Minimum Coins)

Given coin denominations and a target amount, find the **minimum number of coins** to make
that amount.

> **Mental model.** One row of a single table, where `dp[i]` answers "cheapest way to make
> exactly i". To make i, you must hand over *some* coin last. Try each coin as the last one
> and ask the table what the leftover costs - so every answer is one lookup plus one.
>
> **Load-bearing:** trying every coin. Take only the biggest coin that fits and you get a
> wrong answer, because picking a coin changes which totals are still reachable. `inf` is also
> load-bearing: it is how an unreachable amount refuses to be built on.

**Why not greedy?** With `coins = [1, 5, 6, 9]` and `amount = 11`, taking the largest coin
first gives 9 + 1 + 1 = three coins. The optimum is 6 + 5 = **two**. Greedy fails because
choosing a coin changes which combinations remain reachable, so every option has to be
explored - which is exactly what the recurrence does.

**Recurrence:** `dp[i] = min(dp[i - coin] + 1)` over every coin that fits in `i`.

`dp[0] = 0` is the base case - nothing is needed to make nothing - and `inf` marks amounts no
combination can reach.

```
coins = [1, 5, 6, 9]

amount   0  1  2  3  4  5  6  7  8  9 10 11
dp       0  1  2  3  4  1  1  2  3  1  2  2
                                          ↑
dp[11] = min( dp[10] + 1,     using a 1  → 3
              dp[6]  + 1,     using a 5  → 2   ← best
              dp[5]  + 1,     using a 6  → 2
              dp[2]  + 1 )    using a 9  → 3
```

Notice `dp[9] = 1` - the 9 coin - yet the answer for 11 routes through `dp[6]` instead.
Optimal sub-answers do not have to build on the *largest* coin, only on some coin.

**Time:** O(amount × len(coins)) &nbsp; **Space:** O(amount)

**Recipe**

1. `dp[i]` means **"fewest coins to make exactly `i`"**. Name the cell before
   writing any loop; everything else is forced by it.
2. Fill with `math.inf` for "impossible", and `dp[0] = 0`. **`inf` rather than
   `-1` so the `+ 1` and the `<` comparison work without special cases.**
3. For each amount `i` upward, try each coin: if `coin <= i`, the candidate is
   `dp[i - coin] + 1`.
4. **The subproblem is `i - coin`, and it is always smaller than `i`, so it is
   already final by the time you read it.** That is what makes the single forward
   pass correct.
5. `dp[amount]` still `inf` means no combination exists, so return `-1`.
6. Amount outer, coins inner. **This ordering counts minimum coins correctly for
   any coin set. The greedy "take the biggest coin first" fails on sets like
   `[1, 3, 4]` making 6.**

```python
import math

def coin_change(coins, amount):
    """Bottom-up tabulation."""
    dp = [math.inf] * (amount + 1)
    dp[0] = 0  # 0 coins needed for amount 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1
    return dp[amount] if dp[amount] != math.inf else -1

def test_coin_change():
    assert coin_change([1, 5, 6, 9], 11) == 2   # 6+5
    assert coin_change([1, 5, 10, 25], 30) == 2  # 25+5
    assert coin_change([2], 3) == -1              # impossible
    assert coin_change([1], 0) == 0

test_coin_change()
```

# Longest Common Subsequence (LCS)

Given two strings, find the length of their longest common **subsequence** - characters in
order, but not necessarily adjacent.

**Example:** `"ABCBDAB"` and `"BDCAB"` → LCS is `"BCAB"`, length 4

> **Mental model.** Only ever look at the *last* character of each prefix. If the two match,
> that character can be kept and both strings shrink by one. If they differ, at least one of
> those two characters is useless, so throw away one, then the other, and keep whichever went
> better. Nothing else about the strings matters at that cell.
>
> **Load-bearing:** the extra row and column of zeros. They say "an empty string shares
> nothing with anything", which is the only place the recursion can stop.

Compare the last characters of the two prefixes. There are only two situations:

- **They match.** That character can safely be part of the LCS, so the answer is 1 plus the
  LCS of both prefixes with that character removed → `dp[i-1][j-1] + 1`
- **They differ.** At least one of the two characters is not in the LCS, so try dropping
  each and keep the better outcome → `max(dp[i-1][j], dp[i][j-1])`

`dp[i][j]` is the LCS length of the first i characters of `s1` and the first j of `s2`. The
table is `(m+1) × (n+1)` so that row 0 and column 0 exist to hold the empty-string case.

```
lcs("ABC", "AC")

            ""   A   C
      ""     0   0   0
      A      0   1   1      A == A → dp[0][0] + 1 = 1
      B      0   1   1      B vs A, B vs C → carry the best neighbour
      C      0   1   2      C == C → dp[2][1] + 1 = 2

answer: dp[3][2] = 2   ("AC")
```

Each cell reads only the row above and the cell to the left, which is why the table can be
filled in a single pass - and why O(n) space is possible by keeping just one row.

**Time:** O(m × n) &nbsp; **Space:** O(m × n)

**Recipe**

1. `dp[i][j]` means **"the LCS length of the first `i` characters of `s1` and the
   first `j` of `s2`"**. Prefix lengths, not indices.
2. Allocate `(m + 1) x (n + 1)`. **The extra row and column are the empty-prefix
   cases, and they are already `0`, which removes every boundary check from the
   loops.**
3. **`s1[i - 1]` and `s2[j - 1]` inside the loops.** Row `i` is about the first
   `i` characters, so the character it just added is at index `i - 1`. This
   off-by-one is the usual bug and it produces plausible wrong answers.
4. Characters match: `dp[i-1][j-1] + 1`. Both prefixes shrink by one, and the
   matched pair is safely counted because no longer subsequence could use either
   character better.
5. No match: `max(dp[i-1][j], dp[i][j-1])`. Drop one character from either string
   and take the better outcome.
6. Answer is `dp[m][n]`. Every cell reads only up and left, so filling row by row
   left to right always has what it needs.

```python
def lcs(s1, s2):
    """Bottom-up tabulation."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

def test_lcs():
    assert lcs('ABCBDAB', 'BDCAB') == 4  # BCAB
    assert lcs('ABC', 'AC') == 2          # AC
    assert lcs('ABC', 'DEF') == 0
    assert lcs('', 'ABC') == 0

test_lcs()
```

# 0/1 Knapsack

Given items with weights and values, and a capacity, find the **maximum value** that fits.
Each item may be taken at most once - hence "0/1".

> **Mental model.** Walk the items one at a time and ask a single yes/no question about each:
> take it or skip it. Skipping keeps the best answer the earlier items already had. Taking it
> adds its value to the best answer the earlier items had for the capacity that is left over.
> A row of the table means "best value reachable using only the items I have seen so far".
>
> **Load-bearing:** both lookups read row `i-1`, the row *before* this item existed. That is
> the entire reason an item cannot be used twice. Read `dp[i][...]` instead and you have
> silently solved a different problem, the unbounded knapsack, where items may repeat.

For each item there are only two choices, so the recurrence is a two-way max:

- **Skip it:** the value is whatever the previous items achieved at this capacity →
  `dp[i-1][w]`
- **Take it** (only if it fits): its value plus the best achievable with the *remaining*
  capacity and the *previous* items → `val[i-1] + dp[i-1][w - wt[i-1]]`

`dp[i][w]` = best value using the first i items within capacity w.

```
wt  = [1, 3, 4, 5]     val = [1, 4, 5, 7]     capacity 7

                w=0  1  2  3  4  5  6  7
  no items       0   0  0  0  0  0  0  0
  + item 1       0   1  1  1  1  1  1  1
  + item 2       0   1  1  4  5  5  5  5
  + item 3       0   1  1  4  5  6  6  9   ← 4 + 5, weights 3 + 4 = 7
  + item 4       0   1  1  4  5  7  8  9

answer: dp[4][7] = 9   (items 2 and 3)
```

Item 4 is the most valuable single item (7) and still is not part of the answer - the pair
2+3 fills the capacity better. That is the greedy trap again, and the reason for the table.

**Time:** O(n × W) &nbsp; **Space:** O(n × W), reducible to O(W) with a single row

**Recipe**

1. `dp[i][w]` means **"best value using the first `i` items with capacity `w`"**.
2. Same `+ 1` padding for the empty cases, all zeros.
3. Start each cell with `dp[i-1][w]`, the **skip** case. That is always legal, so
   it makes a safe default.
4. If the item fits (`wt[i-1] <= w`), compare against **taking** it: `val[i-1] +
   dp[i-1][w - wt[i-1]]`.
5. **Both terms of the take case read row `i - 1`, not row `i`.** That is what
   makes it 0/1 rather than unbounded: reading `dp[i][...]` would allow the same
   item to be taken again, which is a different problem with a one-index fix.
6. **Each item asks one yes/no question, and the answer is the better of two
   fully-solved subproblems.** Capacity has to drop by the item's weight in the
   take branch, because that space is now spent.

```python
def knapsack(wt, val, capacity):
    """Bottom-up tabulation."""
    n = len(wt)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            dp[i][w] = dp[i - 1][w]  # don't take item i
            if wt[i - 1] <= w:
                dp[i][w] = max(dp[i][w], val[i - 1] + dp[i - 1][w - wt[i - 1]])
    return dp[n][capacity]

def test_knapsack():
    assert knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9  # items 2+3 (4+5 val, 3+4 wt)
    assert knapsack([2, 3, 4], [3, 4, 5], 5) == 7        # items 1+2
    assert knapsack([10], [100], 5) == 0                  # item too heavy

test_knapsack()
```

# Python Built-in: `functools.lru_cache`

Python provides automatic memoization via `@lru_cache` decorator.
This turns any recursive function into a top-down DP solution with one line.

It is worth noticing what that proves. The recurrence below is unchanged from the naive
version - only the bookkeeping was added, and a library could add it. The thinking in DP is
finding the recurrence; the cache is clerical work.

```python
from functools import lru_cache

# naive recursive fib becomes O(n) with one decorator
@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(50))  # 12586269025 - instant, would be impossible without memoization

# cache info shows hits vs misses
print(fib.cache_info())  # CacheInfo(hits=48, misses=51, ...)

# Python 3.9+ also has @cache (unlimited, simpler)
# from functools import cache
```
