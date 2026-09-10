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
# Analysis of Recursion

> **Mental model.** Don't solve the recurrence algebraically - draw the tree and read two
> numbers off it. How many **levels**, which is set by how the argument shrinks ($n/2$ gives
> $\log n$ levels, $n - 1$ gives $n$), and how the work **changes from one level to the next**.
> The total is the sum down the levels, and which level dominates that sum decides the answer.
> Stay flat, $Cn$ at every level, and it is work × height: $\Theta(n \log n)$. Grow by a
> constant factor and the *bottom* level swamps everything above it, so $2T(n/2) + C$ is
> $\Theta(n)$ and $2T(n-1) + C$ is $\Theta(2^n)$. Shrink by a constant factor and the *root*
> dominates instead, so $T(n/4) + T(n/2) + Cn$ collapses to $n$ however many levels follow.
>
> **Load-bearing:** the geometric sum, not the height. $2T(n/2) + Cn$ and $2T(n/2) + C$ have
> the same shape and the same $\log n$ height, and differ only in the root's work, yet one is
> $\Theta(n \log n)$ and the other $\Theta(n)$. Reach for "height × work at the root" instead
> of summing the levels and you cannot tell them apart. The second load-bearing piece is what
> licenses the shortcut on a lopsided tree: you round it up to a full one, which prices work
> that is not actually there, and that is precisely why an incomplete tree yields $O$ and never
> $\Theta$.

Let's go through some examples to get a hang of how to derive time taken $T(n)$ for recursive functions.

## Examples

### Example 1

**Python**

```python
def fun(n):
    if n <= 1:
        return
    for i in range(n):      # 𝛳(n)
        print("something")
    fun(n//2)               # T(n/2)
    fun(n//2)               # T(n/2)
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
function fun(n) {
  if(n <= 1) {
    return;
  }
  for(let i = 0; i < n; i++) {
    console.log('something');
  }
  fun(Math.floor(n/2));
  fun(Math.floor(n/2));
}
```
</details>

Time taken: $T(n) = 2T(n/2) + \Theta(n)$ \
Base case: $T(1) = C$

### Example 2

**Python**

```python
def fun(n):
    if n <= 1:
        return
    print("something")      # 𝛳(1)
    fun(n//2)               # T(n/2)
    fun(n//2)               # T(n/2)
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
function fun(n) {
  if(n <= 1) {
    return;
  }
  console.log('something');
  fun(Math.floor(n/2));
  fun(Math.floor(n/2));
}
```
</details>

Time taken: $T(n) = 2T(n/2) + C$ \
Base case: $T(1) = C$

### Example 3

**Python**

```python
def fun(n):
    if n <= 0:
        return
    print(n)        # 𝛳(1)
    fun(n - 1)      # T(n - 1)
```

**JavaScript**

<details>
<summary>JavaScript equivalent</summary>

```javascript
function fun(n) {
  if(n <= 0) {
    return;
  }
  console.log(n);
  fun(n - 1);
}
```
</details>

Time taken: $T(n) = T(n - 1) + C$ \
Base case: $T(1) = C$

## Recursion Tree Method

Once the value of $T(n)$ is written recursively, we can use **Recursion Tree Method** to find the actual value of $T(n)$. Here are the steps for it:

  1. Write non-recursive part as root of tree and recursive parts as children.
  2. Keep expanding children until a pattern emerges.
  3. Add up the levels.

Step 3 is where the answer actually comes from, and only two numbers matter:

- **How many levels**, set by how the argument shrinks. Halving gives $\log_2 n$ levels;
  subtracting 1 gives $n$.
- **The ratio $r$ between one level's total work and the level above it.**

That ratio decides which level dominates the sum, and therefore the answer:

| Ratio | What dominates | Total |
|-------|----------------|-------|
| $r = 1$ | nothing - every level costs the same | work per level $\times$ number of levels |
| $r > 1$ | the **bottom** level; it alone is a constant fraction of the whole sum | $\Theta(\text{work at the last level})$ |
| $r < 1$ | the **root**; the levels below shrink geometrically to a constant multiple of it | $\Theta(\text{work at the root})$ |

Every example below is one of those three cases, so it is worth spotting $r$ before doing any
algebra. Watch for it: $r$ is not the branching factor on its own. Two children each doing
half the work gives $r = 1$, two children each doing the same work as their parent gives
$r = 2$, and that difference is the whole difference between $\Theta(n \log n)$ and
$\Theta(n)$.

One notation point before the trees: $C$ is the constant cost of the non-recursive part, and the
hand-drawn diagrams label that same constant lowercase $c$. $Cn$ in the text and $cn$ in a picture
are the same quantity.

### Example 1

$$
\begin{align}
T(n) = 2T(n/2) + Cn \\
T(1) = C
\end{align}
$$

![Recursion1](images/recursion-recursion1.png)

$Cn$ work is being done at every level, the bottom one included: its $n$ leaves each cost $C$.\
The *argument* halves at each step, so the base case arrives after $\log_2 n$ halvings, giving
levels $0$ through $\log_2 n$.\
Total work done: $Cn + Cn + Cn + \dots$ once per level i.e. $\approx Cn \log n$.\
Therefore, the time complexity is $\Theta(n \log n)$.

### Example 2

$$
\begin{align}
T(n) = 2T(n-1) + C \\
T(1) = C
\end{align}
$$

![Recursion2](images/recursion-recursion2.png)

We are reducing by 1 in each recursion, therefore the height of tree will be $n$.\
Total work done: $C + 2C + 4C + \dots \text{for} \space n$ times.\
It's a geometric progression: $C(1 + 2 + 4 + \dots + 2^{n-1})$.

> Formula for geometric progression:
> $$
\begin{align}
\frac{a *(r^k-1)}{r-1} \\
\text {\small where r = common ratio, a = first term, k = number of terms}
\end{align}
$$

Applying the formula with $a = 1, r = 2, k = n$:\
$C \cdot \frac{2^n - 1}{2 - 1} = C(2^n - 1)$.\
Therefore, the time complexity is $\Theta(2^n)$.

### Example 3

$$
\begin{align}
T(n) = T(n/2) + C \\
T(1) = C
\end{align}
$$

![Recursion3](images/recursion-recursion3.png)

Total work done: $C + C + \dots$ once per level, for the levels $0$ through $\log_2 n$.\
Therefore, the time complexity is $\Theta(\log n)$.

### Example 4

$$
\begin{align}
T(n) = 2T(n/2) + C \\
T(1) = C
\end{align}
$$

![Recursion4](images/recursion-recursion4.png)

Total work done: $C + 2C + 4C + \dots$ for the levels $0$ through $\log_2 n$. Level $j$ holds $2^j$
nodes, and the bottom level is the base case $T(1) = C$ - it must be counted, because with $r = 2$ it
is the level that decides the answer.

$$
\begin{align}
C(1 + 2 + 4 + \dots + 2^{\log_2 n}) \\
a = 1, r = 2, k = \log_2 n + 1 \text{\small \space terms} \\
\text {\small applying geometric progression formula } \frac{a(r^k - 1)}{r - 1} \\
\frac {2^{\log_2 n + 1} - 1}{2-1} = 2n - 1 \\
\text {\small since } 2^{\log_2 n } = n
\end{align}
$$

So the total is $C(2n - 1)$, of which the bottom level alone contributes $Cn$ - more than every level
above it put together ($C(n-1)$). That is the $r > 1$ row of the table: the leaves dominate.

Therefore, the time complexity is $\Theta(n)$.

## Incomplete trees

We can still use _Recursion Tree_ method for incomplete trees, but instead of exact bound we'll get upper bound.

### Example 1

$$
\begin{align}
T(n) = T(n/4) + T(n/2) + Cn \\
T(1) = C
\end{align}
$$

![Incomplete1](images/recursion-incomplete1.png)

In this example the left child shrinks faster than the right, so the two branches do not bottom out
together: following $n/4$ reaches the base case in $\log_4 n$ steps while following $n/2$ takes
$\log_2 n$. The tree is lopsided, and the deepest level is $\log_2 n$ because the longest path is the
one that only halves.

The level totals themselves are exact while every node still has both children. Each node hands
$\frac{1}{4}$ of its work to one child and $\frac{1}{2}$ to the other, so a level costs
$\frac{3}{4}$ of the level above it:

- Level 0: $Cn$
- Level 1: $\frac{Cn}{4} + \frac{Cn}{2} = \frac{3Cn}{4}$
- Level 2: $\frac{9Cn}{16}$

Ratio between levels: $r = \frac{3Cn/4}{Cn} = \frac{3}{4}$.

The over-estimate enters *after* that. Once the left branch has bottomed out its subtrees stop
contributing, so the real lower levels are smaller than $\frac{3}{4}$ of the one above - yet we
carry on applying the ratio for every level, and in fact sum it all the way to infinity. That prices
work which is not there, which is exactly why this yields an upper bound and not a tight one.

It's a geometric progression with ratio less than 1.

> Formula for the sum of an *infinite* geometric progression with ratio < 1, which therefore bounds
> any finite prefix of the same series from above:
$$
\begin{align}
\frac{a}{1-r} \\
\text {\small where r = common ratio} \\
\text {\small a = first term}
\end{align}
$$


$a = Cn, r = 3/4$\
applying geometric progression formula
$\frac {Cn}{1-3/4} = 4Cn$\
ignoring constants, the complexity is $n$

The time complexity is $O(n)$.

### Example 2

$$
\begin{align}
T(n) = T(n-1) + T(n-2) + C \\
T(1) = C
\end{align}
$$

![Incomplete2](images/recursion-incomplete2.png)

The two children shrink by different amounts, $n-1$ and $n-2$, so the $n-2$ side bottoms out first
and the tree is not full - the level totals fall short of doubling. Round it up to a full binary tree
of height $n$ and every level doubles exactly, which prices calls that were never made, so what comes
out is an upper bound.

Total work done on that rounded-up tree: $C + 2C + 4C + \dots \space \text{for} \space n \space \text{levels}$.\
It's a geometric progression: $C(1 + 2 + 4 + \dots + 2^{n-1})$.\
Applying the formula with $a = 1, r = 2, k = n$: $C \cdot \frac{2^n - 1}{2 - 1} = C(2^n - 1)$.\
Therefore, the time complexity is $O(2^n)$.

How much the rounding up costs is measurable here: the tight bound is $\Theta(\varphi^n)$ with
$\varphi = \frac{1 + \sqrt 5}{2} \approx 1.618$, and the gap between $\varphi^n$ and $2^n$ is
precisely the calls the full tree charged for but never made.

<!-- #endregion -->
