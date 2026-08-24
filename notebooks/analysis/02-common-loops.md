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
- Time complexity for this loop is $\Theta(\lfloor \frac{n}{c} \rfloor)$. Ignoring constants, it's $\Theta(n)$.

## Decreasing counter

**Python**

```python
for i in range(n, 0, c) # where c is negative value
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
- Time complexity for this loop is $\Theta(\lceil \frac{n}{c} \rceil)$.
  Ignoring constants, it's $\Theta(n)$.

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
  Generalizing, it runs for $1, c, c^2, c^3, ..., c^{k-1}$ i.e. it runs $k$ times from $1$ to $k-1$.

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

  So, the loop is going to run $\log_c n + 1$ times.
- Time complexity for this loop is $\Theta(\log n)$.
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
  For `n = 33` and `c = 2`, it will be executed `6` times `33, 16, 8, 4, 2`.
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

  Let's find out the number of times the loop runs:

  $$
  \begin{align}
  2, 2^c, {(2^c)}^c \\
  2, 2^c, 2^{c^2}, ...2^{c^{k-1}} \text{\small k is the number of times it runs} \\
  2^{c^{k-1}} < n \\
  \end{align}
  $$

  Taking log base 2 of both sides (valid because log is a monotonically increasing function for c > 1):

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
<!-- #endregion -->
