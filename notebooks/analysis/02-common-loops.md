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

<!-- #region -->
# Analysis of Common Loops

> **Mental model.** The body does not set the cost; what the loop does to its *counter* does.
> Every case below answers one question: how many times can this step be applied before the
> counter reaches $n$? That is just the step run backwards. Adding $c$ each time needs $n/c$
> steps, so linear. Multiplying by $c$ needs $\log_c n$, because undoing a multiplication is a
> logarithm. Raising to the power $c$ needs $\log \log n$, because you undo it twice. The base
> of the log never matters, since changing base only multiplies by a constant.
>
> **Load-bearing:** you may multiply the costs of nested loops only when the inner count does
> not depend on the outer counter. `for j in range(n)` inside `for i in range(n)` really is
> $n \times n$, but `for j in range(i)` is not - the inner count changes on every pass, so the
> levels have to be *added*, and $1 + 2 + \dots + n$ is where the $n^2/2$ triangle in
> [01](01-notation.md) came from. Both land on $\Theta(n^2)$ here, which is the trap: multiply
> a bound that secretly depends on $i$ and you are right by luck, then wrong the moment the
> inner loop is logarithmic or the outer range is not $n$.

## Increasing counter

**Python**

```python
for i in range(0, n, c):
    # some constant work
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
for (let i = 0; i < n; i += c) {
  // some constant work
}
```
</details>

- Example: for `n = 10` and `c = 2`, it will run `5` times `(0, 2, 4, 6, 8)`.
- The counter takes the values $0, c, 2c, \dots$ while staying below $n$, so the loop runs
  $\lceil \frac{n}{c} \rceil$ times - ceiling, not floor: `n = 11, c = 2` runs `6` times, the last
  pass being `i = 10`. Ignoring constants, it's $\Theta(n)$.

## Decreasing counter

**Python**

```python
for i in range(n, 0, -c):   # c is a positive constant; the step is -c
    # some constant work
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
for (let i = n; i > 0; i -= c) {
  // some constant work
}
```
</details>

- Example: for `n = 10` and `c = 2`, it will run `5` times `(10, 8, 6, 4, 2)`.
- Same count as the increasing case, $\lceil \frac{n}{c} \rceil$ - the counter covers the same
  distance, only from the other end. Ignoring constants, it's $\Theta(n)$.

## Counter getting multiplied in each iteration

**Python**

```python
i = 1
while i < n:
    # some constant work
    i *= c
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
for (let i = 1; i < n; i *= c) {
  // some constant work
}
```
</details>

- Example: \
  For `n = 32` and `c = 2`, it will be executed `5` times `1, 2, 4, 8, 16`. \
  For `n = 33` and `c = 2`, it will be executed `6` times `1, 2, 4, 8, 16, 32`. \
  Generalizing, the counter takes the values $1, c, c^2, c^3, ..., c^{k-1}$, so if the loop runs $k$
  times the last pass is the one entered with $i = c^{k-1}$.

  The condition for that last pass to happen at all is:

  $$
  \begin{align}
  c^{k-1} < n \\
  \end{align}
  $$

  Taking log base c of both sides (valid because log is a monotonically increasing function for c > 1):

  $$
  \begin{align}
  k-1 < \log_c n \\
  k < \log_c n + 1 \\
  \end{align}
  $$

  What that derives is a strict **bound** on the count, $k < \log_c n + 1$, and not the count
  itself. Reading the expression $\log_c n + 1$ off as the count is the trap, and it misfires
  exactly on the powers of $c$: for `n = 32, c = 2` it reads off $6$ where the loop runs $5$ times.
  The exact count is $\lceil \log_c n \rceil$, which is $5$ for `n = 32` and $6$ for `n = 33`,
  matching the two examples above.
- Time complexity for this loop is $\Theta(\log n)$ - the slack between $\lceil \log_c n \rceil$ and
  $\log_c n + 1$ is under one iteration, so it cannot change the growth rate.
- Note that base of the log doesn't matter, since bases can be  converted by simple multiplication or division operations and in asymptotic analysis constants are ignored.

## Counter getting divided in each iteration

**Python**

```python
i = n
while i > 1:
    # some constant work
    i //= c # // is integer division
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
for (let i = n; i > 1; i /= c) {
  // some constant work
}
```
</details>

- Example: \
  For `n = 32` and `c = 2`, it will be executed `5` times `32, 16, 8, 4, 2`. \
  For `n = 33` and `c = 2`, it will be executed `5` times `33, 16, 8, 4, 2`.
  Unlike the multiplying loop, 32 and 33 cost the same here: dividing 33 lands on 16 straight
  away, so the extra element buys no extra step.
- Time complexity for this loop is $\Theta(\log n)$.

## Counter raised to some power in each iteration

**Python**

```python
i = 2
while i < n:
    # some constant work
    i = pow(i, c)
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
for (let i = 2; i < n; i = Math.pow(i, c)) {
  // some constant work
}
```
</details>

- Example: For `c = 2` and `n = 32` it's going to run for $2, 2^2, {(2^2)}^2$ i.e. `2, 4, 16`.

  Let's find out the number of times the loop runs. Writing the counter as a power of 2 keeps the
  pattern visible - each pass raises the exponent to the power $c$:

  $$
  \begin{align}
  2, 2^c, {(2^c)}^c \\
  2, 2^c, 2^{c^2}, ...2^{c^{k-1}} \text{\small k is the number of times it runs} \\
  2^{c^{k-1}} < n \\
  \end{align}
  $$

  Taking log base 2 of both sides (base 2 > 1, so $\log_2$ is increasing and preserves the
  inequality):

  $$
  \begin{align}
  c^{k-1} < \log_2 n \\
  \end{align}
  $$

  Taking log base 2 of both sides again:

  $$
  \begin{align}
  k - 1 < \log_2 \log_2 n \\
  k < \log_2 \log_2 n + 1
  \end{align}
  $$

  As with the multiplying loop this is a bound rather than the count; for `c = 2` the loop runs
  exactly $\lceil \log_2 \log_2 n \rceil$ times, which is $3$ for `n = 32`, matching the example.
- Time complexity of this loop is $\Theta(\log\log n)$.

## Sequential loops

**Python**

```python
def fun(n):
    for i in range(n):          # 𝛳(n)
        # some constant work
    i = 1
    while i < n:                # 𝛳(log n)
        # some constant work
        i *= 2
    for i in range(1, 100):     # 𝛳(1)
        # some constant work
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
function fun(n) {
  for (let i = 0; i < n; i++) {
    // some constant work
  }
  let i = 1;
  while(i < n) {
    i *= 2;
  }
  for (i = 0; i < 100; i++) {
    // some constant work
  }
}
```
</details>

- Since the work is sequential, we add the values $\Theta(n) + \Theta(\log n) + \Theta(1)$.\
  Ignoring lower order terms, the complexity of this function is $\Theta(n)$.

## Nested loops

**Python**

```python
def fun(n):
    for i in range(n):            # 𝛳(n)
        j = 1
        while j < n:              # 𝛳(log n)
            # some constant work
            j *= 2
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
function fun(n) {
  for(let i = 0; i < n; i++) {
    let j = 1;
    while(j < n) {
      j *= 2;
    }
  }
}
```
</details>

- Since it's a nested loop,we multiply the values $\Theta(n) * \Theta(\log n)$.\
  Therefore the complexity is $\Theta(n \log n)$.

## Nested loops 2

**Python**

```python
def fun(n):
    for i in range(n):          # 𝛳(n)
        for j in range(n):      # 𝛳(n)
            # some constant work
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
function fun(n) {
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      // some constant work
    }
  }
}
```
</details>

- The time complexity is $\Theta(n^2)$.

## When multiplying is allowed

Both nested sections above multiply the two loops, and both are right to - but only because the
inner count does not depend on the outer counter. `while j < n` and `for j in range(n)` run the
same number of times whichever pass of `i` we are on, so "outer $\times$ inner" is just adding
the same number $n$ times.

Make the inner bound depend on `i` and the multiplication stops being valid:

```python
for i in range(n):
    for j in range(i):        # not n - it grows with i
        # some constant work
```

The passes now cost $0, 1, 2, \dots, n-1$, so the total is $\frac{n(n-1)}{2}$. That is still
$\Theta(n^2)$, and *that* is the trap: multiplying gives $n \times n = n^2$ and lands on the
right answer by luck, so the mistake goes unnoticed. Make the inner loop logarithmic in `i`, or
the outer range something other than $n$, and the two methods part company.

They can also disagree outright. Let `i` set the inner loop's *step* instead of its
bound, and the passes shrink as `i` grows:

```python
for i in range(1, n + 1):
    for j in range(0, n, i):    # step i, so about n/i passes
        # some constant work
```

For `n = 6` the outer passes cost `6, 3, 2, 2, 2, 1`, which is $16$ - not the $36$
that $n \times n$ predicts. The exact total is
$\sum_{i=1}^{n}\lceil n/i\rceil$. Its main part is
$n(1 + \frac{1}{2} + \frac{1}{3} + \dots + \frac{1}{n})$; rounding each pass up
adds at most another $n$. The bracketed *harmonic* sum grows like $\log n$, so
the loop is $\Theta(n \log n)$. Multiplying $n$ by $n$ is not merely lucky here,
it is wrong.

The rule: **add the passes** whenever the inner count moves, and multiply only when it is
genuinely fixed.
<!-- #endregion -->
