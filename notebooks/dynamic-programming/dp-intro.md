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

> **Mental model.** The one problem where the subproblem is handed to you: the question is
> about a number `n`, and the definition already names the two smaller questions it needs, so
> `dp[i]` can only mean "the i-th Fibonacci number". Nothing is being chosen and nothing has
> to be designed, which leaves the bookkeeping alone on show - one recurrence written four
> times, each version throwing away work the one above it repeated.
>
> **Load-bearing:** two seeds, because the recurrence reads two cells back. `fib(0) = 0` and
> `fib(1) = 1` are the only values it cannot produce for itself; seed just `dp[0]` and every
> later cell is a sum of zeros, so the whole table stays 0 and nothing complains.

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
and "answers that exist" is what DP eliminates. The exact call count is `2·fib(n+1) - 1`, so
the true growth is φⁿ ≈ 1.618ⁿ; O(2ⁿ) is the loose bound usually quoted.

**The state.** The question carries its own subproblem. "The n-th number" takes one number
and returns one number, and the definition hands you smaller copies of the same question, so
there is nothing to design: the state is `n`, and `dp[i]` means the i-th Fibonacci number,
nothing more. Every other problem in this notebook has to invent what a subproblem even is.
Here that step is free, which is what makes it the honest place to look at the bookkeeping on
its own.

**The recurrence and its bases.** `fib(n) = fib(n-1) + fib(n-2)` offers no choice - no min,
no max, no options to compare. Both smaller answers are used, every time. That leaves the
base cases as the only values the recurrence cannot produce. It reads two cells back, so it
needs two seeds, and they have to sit below index 2: `fib(0) = 0` and `fib(1) = 1`, which
collapse into `if n <= 1: return n` because at 0 and 1 the answer is the index. Seed only
`dp[0]` and the whole table stays 0, because a sum of zeros has nothing to disagree with it.

**Fill order.** `dp[i]` reads `dp[i-1]` and `dp[i-2]`, both strictly smaller, so ascending
`i` guarantees every cell is final before anything reads it: one forward pass, nothing
revisited. Top-down needs no order at all - the recursion asks for `n-1` and `n-2`, the cache
answers, and a valid order is discovered on the way down.

**Reuse.** `fib(n-2)` is wanted by both `fib(n)` and `fib(n-1)`, so one stored answer serves
two parents, and it could serve a thousand: reading a cached answer neither consumes nor
changes it, so there is no limit on how often a cell may be read. What Fibonacci has no
notion of is reusing a *choice*, because it never makes one. The problems below each pick
things, and each has to say how often the same thing may be picked; here the cache is pure
bookkeeping with nothing to restrict.

The four versions below are the same recurrence with progressively less waste, each a
mechanical transformation of the one above it:

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

1. **Naive**: `if n <= 1: return n`, else `return fib(n - 1) + fib(n - 2)`.
2. **Memoised**: signature `fib(n, memo=None)`, and `if memo is None: memo = {}`
   as the first line. **Never `memo={}` in the signature** - that dict is built
   once at definition time and shared by every later call. Base case before the
   lookup, then `if n not in memo: memo[n] = fib(n - 1, memo) + fib(n - 2,
   memo)`, return `memo[n]`.
3. **Tabulated**: return early for `n <= 1`, *then* allocate
   `dp = [0] * (n + 1)` and set `dp[1] = 1`. **The early return is what makes
   `dp[1]` legal** - at `n = 0` the list has one cell. Loop
   `for i in range(2, n + 1)`, assign `dp[i] = dp[i - 1] + dp[i - 2]`, return
   `dp[n]`.
4. **Optimised**: `a, b = 0, 1` is `fib(0), fib(1)`; loop `range(2, n + 1)`,
   which is n - 1 steps; `a, b = b, a + b`. **One tuple assignment, reading the
   old pair** - on two separate lines the new `a` feeds into `b`. Return `b`,
   not `a`.

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

**The state.** The denominations are fixed and the question asks about one amount, so the
only thing that changes as you work is how much is still owed. Coins are unlimited and the
order you hand them over is irrelevant, so nothing about the past has to travel: two
different routes to "4 left to pay" are interchangeable from that point on. One number is
therefore a complete description of what remains, and the table is a single row where `dp[i]`
is the fewest coins that make exactly `i`.

**The recurrence and its choice.** Every way of paying `i` hands over some coin last. Call it
`c`; strip it off and what is left is a way of paying `i - c`, and it had better be the
cheapest such way, or you could swap the cheaper one in and beat yourself. So the options at
cell `i` are exactly the coins that fit, each option costs `dp[i - c] + 1`, and the cell
keeps the smallest. The only decision is *which coin is last* - the rest of the bill is
already priced.

**Recurrence:** `dp[i] = min(dp[i - coin] + 1)` over every coin that fits in `i`.

**Why not greedy?** With `coins = [1, 5, 6, 9]` and `amount = 11`, taking the largest coin
first gives 9 + 1 + 1 = three coins. The optimum is 6 + 5 = **two**. Greedy fails because
choosing a coin changes which combinations remain reachable, so every option has to be
explored - which is exactly what the `min` does.

**The base and the sentinel.** `dp[0] = 0` says making nothing takes no coins. It is the one
cell the recurrence cannot produce, and the only cell that starts out finite, so every finite
number in the table traces back to it through a chain of real coins - that is what makes a
finite answer a construction rather than an artefact. `math.inf` everywhere else means "no
combination of these coins makes exactly this amount", and it is a *value*, not a flag:
`inf + 1` is `inf` and `inf < inf` is false, so an unreachable leftover loses every
comparison it enters and never has to be tested for.

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

**Fill order.** Every read is `dp[i - c]`, and since the coins are positive that cell sits
strictly below `i`: ascending `i` means each cell is final before anything reads it, in one
forward pass. Positivity is the part doing the work - a coin of 0 would have the cell read
itself.

**Reuse.** `dp[i - c]` is a cell of the same row this pass is filling, and the cheapest way
to pay `i - c` may well hand over another `c` of its own. Nothing prevents it, and nothing
should: the problem supplies unlimited coins, so a denomination may appear any number of
times in one answer. That is the difference between reusing an option and spending it, and
the code states which one it means purely by *where it reads* - a cell of the row being
built, rather than a copy of the row from before this coin was on offer. The single row is
not a space trick, it is the claim that coins are unlimited.

**Time:** O(amount × len(coins)) &nbsp; **Space:** O(amount)

`amount` is a magnitude, not a length, so this is not polynomial in the size of the input:
writing one more digit on the target multiplies the work tenfold.

**Recipe**

1. `dp = [math.inf] * (amount + 1)`, one cell per amount from 0 to `amount`,
   then `dp[0] = 0`.
2. **The sentinel is `math.inf`, not `-1`**: `dp[i - coin] + 1 < dp[i]` then
   needs no special case in either direction.
3. Amounts outer, `for i in range(1, amount + 1)`; coins inner,
   `for coin in coins`. **No `break` in the inner loop**, and the coins need no
   sorting.
4. Body: `if coin <= i and dp[i - coin] + 1 < dp[i]: dp[i] = dp[i - coin] + 1`.
5. Return conversion: `dp[amount] if dp[amount] != math.inf else -1`.

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
    assert coin_change([1, 5, 6, 9], 11) == 2   # 6+5, not the greedy 9+1+1
    assert coin_change([1, 5, 10, 25], 30) == 2  # 25+5
    assert coin_change([2], 3) == -1              # impossible
    assert coin_change([1], 0) == 0
    assert coin_change([7], 3) == -1              # no coin ever fits
    assert coin_change([], 7) == -1               # no coins at all
    assert coin_change([3, 3, 4], 6) == 2         # duplicates change nothing
    assert coin_change([2, 5], 6) == 3            # 2+2+2: a coin may repeat

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

**The state.** The question compares two whole strings. A common subsequence is built by
walking both strings left to right, and at each step the two characters in front of you are
either paired off or one of them is discarded for good. So the only thing that changes is how
far into each string you have got: two numbers. `dp[i][j]` is the same question asked of the
first `i` characters of `s1` and the first `j` of `s2`, which makes the indices prefix
*lengths* rather than positions. The table is `(m+1) × (n+1)` so that the length 0 prefix,
the empty string, gets a row and a column of its own.

**The recurrence and its choice.** Only the last character of each prefix matters. If
`s1[i-1] == s2[j-1]`, pair them and take `dp[i-1][j-1] + 1`, with nothing to compare against:
any longest common subsequence can be rewritten to end with that pair without getting
shorter, so pairing equal ends is never a mistake. If they differ, they cannot both be the
final pair, so at least one is dead weight - drop `s1`'s and read `dp[i-1][j]`, drop `s2`'s
and read `dp[i][j-1]`, keep the larger. Two options, not four: dropping both at once is
covered by dropping one and then the other.

**Recurrence:** `dp[i][j] = dp[i-1][j-1] + 1` when the last two characters match, else
`max(dp[i-1][j], dp[i][j-1])`.

**The base.** Row 0 and column 0 are zero because an empty string shares nothing with
anything. They are not padding bolted on to keep the arithmetic in range, they are the honest
answer to a real question, which is why the loops can read them like any other cell and why
no cell needs a boundary check.

```
lcs("ABC", "AC")

            ""   A   C
      ""     0   0   0
      A      0   1   1      A == A → dp[0][0] + 1 = 1
      B      0   1   1      B vs A, B vs C → carry the best neighbour
      C      0   1   2      C == C → dp[2][1] + 1 = 2

answer: dp[3][2] = 2   ("AC")
```

**Fill order.** A cell reads `dp[i-1][j-1]`, `dp[i-1][j]` and `dp[i][j-1]` - the row above
and the cell immediately to its left, never below and never to the right. Row by row, left to
right, has all three final before they are read. Only two rows are ever live, which brings
the space down to O(n): one row, plus a temporary holding the diagonal, since `dp[i-1][j-1]`
is overwritten the moment `dp[i][j-1]` is stored.

**Reuse and one-time use.** On a pair, *both* indices drop. That is the whole statement that
a character is spent by the match that consumed it and cannot join a second pair. Read
`dp[i-1][j] + 1` on a match instead and `s2`'s character is never spent, so the single `A` in
`lcs("AAA", "A")` pairs with all three and the answer comes out 3 - a number that is no
longer the length of any subsequence of either string. The diagonal step is what forbids it.

**Time:** O(m × n) &nbsp; **Space:** O(m × n)

**Recipe**

1. `m, n = len(s1), len(s2)`, then
   `dp = [[0] * (n + 1) for _ in range(m + 1)]`. **A comprehension per row** -
   `[[0] * (n + 1)] * (m + 1)` aliases one row `m + 1` times.
2. Offsets: row `i` is about the first `i` characters, so the character it just
   added is **`s1[i - 1]`**, and column `j`'s is **`s2[j - 1]`**. This
   off-by-one returns plausible wrong answers rather than raising.
3. `i` from 1 to `m` outer, `j` from 1 to `n` inner. Row 0 and column 0 are
   never written.
4. Match: `dp[i][j] = dp[i-1][j-1] + 1`, and **nothing else** - no `max` against
   the neighbours. Otherwise `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`.
5. Return `dp[m][n]`, no conversion.

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
    assert lcs('', '') == 0
    assert lcs('A', 'A') == 1
    assert lcs('ABC', 'ABC') == 3         # whole string
    assert lcs('AAA', 'A') == 1           # one character pairs once, not thrice

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

**The state.** The item list and the capacity are fixed; what changes as you work is which
items are still undecided and how much room is left. Decisions can be made in any order, so
"which items remain" collapses to a single number, how far down the list you have got, and
the second number is the free capacity. Hence `dp[i][w]`: the best value reachable using only
the first `i` items in a sack of capacity `w`. Each dimension is sized one larger than its
input, so that "no items" and "no room" each get a line of their own.

**The recurrence and its choice.** Item `i` gets one yes/no question. Skip it and the answer
is whatever the earlier items already managed at the same capacity, `dp[i-1][w]`. Take it,
legal only when `wt[i-1] <= w`, and the answer is `val[i-1]` plus whatever the earlier items
managed in the room that is left, `dp[i-1][w - wt[i-1]]`. The cell keeps the larger. Skipping
is always available, so no cell can be impossible and no sentinel is needed anywhere: the
question is the best value fitting *within* `w`, and taking nothing always fits.

**Recurrence:** `dp[i][w] = max(dp[i-1][w], val[i-1] + dp[i-1][w - wt[i-1]])` - skip the
item, or take it if it fits.

**The base.** Row 0 is "no items offered" and column 0 is "no room", both 0 for the same
reason: the empty selection is the only selection available and it is worth nothing. Because
those are genuine answers and not placeholders, allocating the table as zeros *is* seeding
the bases, and the loops can start at `i = 1`, `w = 1`.

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

**Fill order.** Both reads sit in row `i - 1`, at column `w` or lower, so any order that
finishes row `i-1` before starting row `i` works, and *within* a row the columns are
independent: `w` may ascend, descend, or be shuffled. That freedom is a property of keeping
the previous row separate, and it disappears the moment the table is collapsed onto one row,
where `w` must run downward.

**Reuse and one-time use.** Both lookups read row `i - 1`, the row as it stood before item
`i` was offered, so the item cannot appear inside its own subproblem: offered once, answered
once. Point either lookup at row `i` and the item can be taken again out of the capacity it
has already eaten, which is the unbounded knapsack, a different problem with different
answers. With one item of weight 2 and value 3 in a sack of 5, this code says 3, and that one
says 6. The whole distinction is one index.

**Time:** O(n × W) &nbsp; **Space:** O(n × W), reducible to O(W) with a single row

`W` is a capacity rather than a length, so the cost tracks the *value* written in the input
rather than the amount of input.

**Recipe**

1. `n = len(wt)`, then `dp = [[0] * (capacity + 1) for _ in range(n + 1)]` -
   `n + 1` rows, `capacity + 1` columns, all zeros, which is both bases already
   seeded. **A comprehension per row**, or every row is the same list.
2. `i` from 1 to `n` outer, `w` from 1 to `capacity` inner. Column 0 keeps its
   zeros.
3. Assign the skip case unconditionally first: `dp[i][w] = dp[i - 1][w]`.
4. Then `if wt[i - 1] <= w:` overwrite with
   `max(dp[i][w], val[i - 1] + dp[i - 1][w - wt[i - 1]])`. Item `i` lives at
   **index `i - 1`** in both `wt` and `val`.
5. **Both lookups are `dp[i - 1][...]`, never `dp[i][...]`.** In the one-row
   version this becomes `for w in range(capacity, wt[i - 1] - 1, -1)`.
6. Return `dp[n][capacity]`, no conversion.

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
    assert knapsack([], [], 5) == 0                       # no items
    assert knapsack([1, 2], [1, 2], 0) == 0               # no capacity
    assert knapsack([1, 2], [1, 2], 9) == 3               # everything fits
    assert knapsack([2], [3], 5) == 3   # once only: unbounded would give 6

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
