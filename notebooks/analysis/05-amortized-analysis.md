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

# Amortized Analysis

Some operations are cheap almost every time and expensive once in a while. Ask "what does one
call cost?" and the answer is the expensive case, which makes the structure look far worse
than it is. So ask a different question: **what do n calls cost, together?** Divide that total
by n and you have the *amortized* cost.

> **Mental model.** Stop pricing one call and price the whole sequence. A rare expensive
> operation is paid for by the many cheap operations around it, because the expensive one can
> only happen *after* enough cheap ones have piled up work for it. The cheap calls pre-pay.
>
> **Load-bearing:** the guarantee is worst-case over *any* sequence, not an average over
> lucky inputs. Nothing here assumes anything about the input. That is also where it breaks:
> the argument only holds while the expensive step stays rare. Grow the array by a fixed 1
> slot instead of doubling and every append copies everything, so there is nothing cheap left
> to pay the bill and the cost really is O(n) each.

| Analysis type | What it measures |
|---------------|------------------|
| Worst-case | Cost of the single most expensive operation |
| Average-case | Expected cost assuming random inputs |
| **Amortized** | Average cost per operation in the worst-case sequence |

## Three Methods

The three methods below are three ways to write down the same argument, not three different
results.

1. **Aggregate method** - compute total cost T(n), divide by n
2. **Accounting method** - assign a "charge" to each operation, bank the surplus
3. **Potential method** - define a potential function on the data structure (more advanced, not covered here)

We'll use the **dynamic array** (Python's `list.append()`) as our running example.


# The Problem: Dynamic Array Append

A dynamic array starts with capacity 1. When an append finds the array already full, it
allocates a new array of **double** the size, copies everything over, and then writes. That
"already full, so grow first" order matters for the bookkeeping below: the copy is charged to
the append that *arrives* at a full array, not to the one that filled it.

| Append # | What happens | Cost |
|----------|--------------|------|
| 1 | room in capacity 1; write | 1 |
| 2 | full at 1 -> copy 1, capacity 2, then write | 1 + 1 = 2 |
| 3 | full at 2 -> copy 2, capacity 4, then write | 1 + 2 = 3 |
| 4 | room in capacity 4; write | 1 |
| 5 | full at 4 -> copy 4, capacity 8, then write | 1 + 4 = 5 |
| 6-8 | room in capacity 8; write | 1 each |
| 9 | full at 8 -> copy 8, capacity 16, then write | 1 + 8 = 9 |

So the expensive appends land at 2, 3, 5, 9, 17 - one past each power of two.

**Worst-case per operation:** O(n) - when we have to copy everything.

**Naive total for n appends:** n x O(n) = O(n^2) - way too pessimistic!

That multiplication quietly assumes every append could be an expensive one. They cannot all
be. A copy only happens when the array is exactly full, which is at capacities 1, 2, 4, 8 and
so on, so the expensive appends are spread further and further apart. Everything else costs 1.


# Method 1: Aggregate

Compute the total cost of n appends, then divide by n.

The whole derivation rests on one fact about doubling: adding up 1 + 2 + 4 + 8 + ... never
reaches twice the last term. So all the copying ever done, added together, costs less than one
final copy done twice - a fixed multiple of n, no matter how many resizes happened. That is
why the total is linear and the per-append price is a constant.

### Step 1: Define the cost of each operation

Let t(i) = cost of the ith append:

- **Case 1:** No reallocation needed. Just assign the element. t(i) = 1
- **Case 2:** Array is full before the insert (i = 2^k for some k >= 0, i.e., size equals capacity). Must allocate new array, copy 2^k elements, then assign. t(i) = 2^k + 1

### Step 2: Compute total cost T(n)

```
T(n) = sum of t(i) for i = 1 to n
```

Every operation pays at least 1 (the assignment), so we can split:

```
T(n) = n  +  (sum of copy costs)
       ^         ^
       |         |
  n assignments   copies only happen when i = 2^k + 1
```

### Step 3: Sum the copy costs

Copies happen at i = 1, 2, 4, 8, 16, ... (i.e., when i = 2^k). At each, we copy 2^k elements.

How many times can this happen? At most floor(log2(n)) + 1 times, since 2^k <= n means k <= log2(n).

Each copy is twice the size of the one before, so the last copy is bigger than everything
before it put together. A sum that keeps doubling like this is called a **geometric series**,
and it stays below twice its final term:

```
Copy costs = 2^0 + 2^1 + 2^2 + ... + 2^floor(log2(n))
```

Using the geometric series formula: sum of 2^j for j = 0 to m = 2^(m+1) - 1

```
Copy costs = 2^(floor(log2(n)) + 1) - 1
           <= 2n - 1          (since 2^floor(log2(n)) <= n)
```

### Step 4: Combine

```
T(n) = n + copy costs
     <= n + (2n - 1)
     = 3n - 1
     <= 3n
```

### Step 5: Amortized cost

```
Amortized cost = T(n) / n <= 3n / n = 3 = O(1)
```

Each append costs **O(1) amortized**, even though individual appends can cost O(n).

The 3 itself does not matter. Grow by any fixed *factor* - 1.5x, 2x, 10x - and the same
argument gives some constant. What matters is that the array grows by a factor at all. Add a
fixed *number* of slots each time, say 100, and resizes stay evenly spaced instead of getting
rarer, the copy costs turn into 100 + 200 + 300 + ... , and the total becomes O(n^2).

```python
# Let's verify empirically
def simulate_appends(n):
    """Simulate n appends to a dynamic array, tracking total cost."""
    capacity = 1
    size = 0
    total_cost = 0
    for i in range(1, n + 1):
        cost = 1  # assignment
        if size == capacity:
            cost += capacity  # copy all elements
            capacity *= 2
        size += 1
        total_cost += cost
    return total_cost


def test_simulate_appends():
    # the aggregate bound: total cost stays under 3n, so amortized cost is O(1)
    for n in [1, 2, 10, 100, 1000, 10000, 100000]:
        assert simulate_appends(n) < 3 * n
    # and it never dips below n - every append costs at least the assignment
    for n in [1, 10, 1000]:
        assert simulate_appends(n) >= n
    # a single append costs exactly 1: capacity 1 is already available
    assert simulate_appends(1) == 1
    # growth is linear, not quadratic: doubling n roughly doubles the cost
    assert simulate_appends(20000) < 2.5 * simulate_appends(10000)


test_simulate_appends()

for n in [100, 1000, 10000, 100000]:
    total = simulate_appends(n)
    print(f"n={n:>6}  total={total:>7}  amortized={total / n:.2f}")
```

# Method 2: Accounting (Banker's Method)

Instead of adding up the real costs, pretend every append is sold at one flat price. Cheap
appends cost less than the price, so the change goes into a savings account. An expensive
append costs more than the price, so it takes the difference out of the account. This flat
price is called the **charge**, and if the account never runs dry then the flat price was
honest: n appends really did cost at most n times the charge.

**Rule:** The bank balance must never go negative.

### Why charge $3?

Between two expensive operations (at i = 2^(k-1) + 1 and i = 2^k + 1), there are 2^(k-1) - 1 cheap operations. Each cheap operation costs $1, so if we charge $3, we bank $2 per cheap operation.

Savings from cheap operations: 2 x (2^(k-1) - 1) = 2^k - 2

Cost of the next expensive operation: 2^k + 1

We pay $3 for the expensive operation itself, plus withdraw 2^k - 2 from the bank:

```
3 + (2^k - 2) = 2^k + 1  ✓  exactly enough!
```

### Watching the balance

The numbers matter less than the shape: the balance climbs while appends are cheap, then a
resize drains almost all of it, and it climbs again.

| Append # | Actual cost | Charge | Bank change | Bank balance |
|----------|-------------|--------|-------------|--------------|
| 1 | 1 | 3 | +2 | 2 |
| 2 | 2 (assign + copy 1) | 3 | +1 | 3 |
| 3 | 3 (assign + copy 2) | 3 | 0 | 3 |
| 4 | 1 | 3 | +2 | 5 |
| 5 | 5 (assign + copy 4) | 3 | -2 | 3 |
| 6 | 1 | 3 | +2 | 5 |
| 7 | 1 | 3 | +2 | 7 |
| 8 | 1 | 3 | +2 | 9 |
| 9 | 9 (assign + copy 8) | 3 | -6 | 3 |

The balance never goes negative, and that is the entire proof. A negative balance would mean
some real cost was paid with money that had never been collected, so the flat price would be a
lie. Staying at or above zero means the real total never exceeded what was charged. Notice the
balance is drained back to a small floor by each resize and built up again by the cheap appends
before the next one, which is the pre-paying made visible.

**Amortized cost = $3 = O(1)**

The accounting method is more flexible than aggregate - it can assign different charges to different operation types (useful when analyzing data structures with multiple operations like push/pop on a stack).

```python
# Verify the bank never goes negative
def verify_accounting(n, charge=3):
    """Verify that charging $charge per append keeps bank >= 0."""
    capacity = 1
    size = 0
    bank = 0
    for i in range(1, n + 1):
        cost = 1
        if size == capacity:
            cost += capacity
            capacity *= 2
        size += 1
        bank += charge - cost
        assert bank >= 0, f'Bank negative at append {i}: {bank}'
    print(f'n={n}, charge=${charge}: bank never negative (final balance: ${bank})')

verify_accounting(1000)
verify_accounting(10000)
```

# Method 3: Potential (Physics Method)

<details>
<summary><strong>Click to expand - more advanced, uses a potential function like energy in physics</strong></summary>

### Intuition

This is the savings account again, with one change: nobody remembers the balance. It is worked
out from the structure itself. Look at a dynamic array and you can already see how much has to
have been saved - a nearly full array has a resize coming, and one that was just resized has
had its savings spent. A number computed from the current state like this is called a
**potential function**, written Phi.

Cheap operations push the array towards full, so Phi rises. The resize empties it out, so Phi
drops and that drop is what pays the copying bill.

### Definition

For each operation i with real cost t(i), the amortized cost is:

```
a(i) = t(i) + Phi(after) - Phi(before)
```

If the operation is expensive, Phi drops (Phi(after) < Phi(before)), reducing the amortized cost.  
If the operation is cheap, Phi rises, "storing energy" for later.

Add these up over a whole sequence and almost everything cancels, because one operation's
"after" is the next one's "before". Only the very first and very last potentials survive. A sum
that collapses like that is said to **telescope**:

```
sum of a(i) = sum of t(i) + Phi(final) - Phi(initial)
```

If Phi(final) >= Phi(initial) (which we ensure by choosing Phi >= 0), then sum of a(i) >= sum of t(i), so the amortized cost is an upper bound on the real cost.

### Applied to Dynamic Array

Define: **Phi = 2 x length - capacity + 1**

This is always >= 0 because we double capacity when full, so after a resize, length = capacity/2 + 1, giving Phi = 2(capacity/2 + 1) - capacity + 1 = 3. Between resizes, length grows from capacity/2 + 1 to capacity, so Phi ranges from 3 to capacity + 1 - always >= 0. At initialization (length=0, capacity=1), Phi = 0.

**Cheap operation** (no resize): length increases by 1, capacity unchanged.

```
a(i) = t(i) + Phi(after) - Phi(before)
     = 1 + (2(length+1) - capacity + 1) - (2*length - capacity + 1)
     = 1 + 2
     = 3
```

**Expensive operation** (resize at i = 2^k): length goes from 2^k to 2^k + 1, capacity goes from 2^k to 2^(k+1).

```
Phi(before) = 2(2^k) - 2^k + 1 = 2^k + 1
Phi(after)  = 2(2^k + 1) - 2^(k+1) + 1 = 3

a(i) = t(i) + Phi(after) - Phi(before)
     = (2^k + 1) + 3 - (2^k + 1)
     = 3
```

Both cases give amortized cost = **3 = O(1)**.

### Potential vs Accounting

They're closely related, but:

- **Accounting:** bank balance depends on the *history* of operations (how much was deposited/withdrawn)
- **Potential:** Phi depends only on the *current state* of the data structure, not how we got there

This makes the potential method more powerful for complex data structures where the same state can be reached via different operation sequences.

</details>


# Where Amortized Analysis Appears

| Data structure / Operation | Worst-case | Amortized | Why |
|---------------------------|-----------|-----------|-----|
| Dynamic array `append` | O(n) | O(1) | Doubling strategy |
| Hash table `insert` | O(n) | O(1) | Resizing when load factor exceeded |
| [Union-Find](../graphs/union-find.md) `find`/`union` | O(log n) | O(α(n)) | Path compression flattens over time |
| Splay tree operations | O(n) | O(log n) | Frequent nodes move to root |
| [Stack with multipop](../stacks-and-queues/monotonic-stack.md) | O(n) | O(1) | Each element pushed/popped at most once |

The last row is the same argument in a different costume. A [monotonic
stack](../stacks-and-queues/monotonic-stack.md) has an inner loop that can pop many elements at
one position, which looks quadratic, but an element can only be popped because some earlier
position pushed it, and it never comes back. One push per element caps the total pops at n. The
pops are pre-paid, exactly as the cheap appends pre-pay for the resize.

## Common Misconception

Amortized != average-case.

- **Average-case** guesses at what the inputs will look like. Guess wrong and the number is
  wrong.
- **Amortized** promises a total for *any* sequence somebody throws at you. It assumes nothing
  about the input, so it cannot be wrong about it.

When someone says Python's `list.append` is O(1), they mean O(1) *amortized* - guaranteed over any sequence of appends.
