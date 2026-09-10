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

# Hash Tables

A structure that maps keys to values - an *associative array*. It computes an array
index straight from the key, so finding a key is arithmetic instead of searching.

| Operation | Average | Worst case |
|---|---|---|
| Insert | O(1) | O(n) |
| Lookup | O(1) | O(n) |
| Delete | O(1) | O(n) |
| Min, max | O(n) | O(n) |
| Sorted order | O(n log n) | O(n log n) |

**Use it when** the only questions are "is this key here?" and "what is stored under
this key?". Anything about order - smallest, next largest, everything between a and b -
belongs in a tree instead.

> **Mental model.** A hash table trades away order to buy a shortcut. The hash turns a
> key into an array index, so you jump straight to the right slot rather than looking
> for it. Giving up order is not a side effect, it is the price: the hash deliberately
> scatters keys, so keys that are near each other in value end up nowhere near each
> other in the array.
>
> **Load-bearing:** the O(1) is an *average*, and only two things hold it up - the load
> factor (how full the table is) and a hash that spreads keys evenly. Two keys landing
> on the same index is not a rare accident, it is the normal state, and it has a name:
> a *collision*. Every design decision below is about absorbing collisions, and every
> one of them decays to O(n) once the table gets too full or the hash stops spreading.

## The hash function

The hash has one job: turn a key into a slot number. Two properties make it useful,
and both are easiest to see through what breaks without them.

**Same key, same slot, every time.** The slot number is recomputed on every lookup and
never stored. If the answer could change, you could put a key in and never find it
again. That is what *deterministic* buys.

**Different keys, different slots, as often as possible.** Keys that clump onto a few
slots turn the array into a handful of long lists, and lookup becomes a scan. Spreading
is not a nicety, it is the entire source of the speed.

Two more requirements are practical. The result must land in `0` to `m-1` so it can
index the array. And it must be cheap to compute - O(1) for an integer, O(len) for a
string - or the hash costs more than the search it replaced.

**Common hash functions:**
- **Integers:** `h(key) = key % m` - m should be a prime (fewer common factors → better distribution)
- **Strings:** Weighted sum `(str[0] × x⁰ + str[1] × x¹ + ...) % m` where x is a constant (e.g., 33)
- **Universal hashing:** Pick a hash function randomly from a family of functions

Why a prime `m`: `% m` only sees the remainder, so any pattern the keys share with `m`
survives the hash. With `m = 100` and keys that are all round hundreds, every key lands
on slot 0. A prime shares a factor with far fewer key patterns, so patterned keys still
spread. And why pick the function at random: any fixed hash can be beaten by a set of
keys chosen to collide, but if the function is drawn from a family at random, no key set
is bad in advance - that is *universal hashing*.

> **Birthday Paradox:** With 23 people in a room, the chance two share a birthday is
> already 50%; with 70 it is 99.9%. It is the same counting problem as keys into slots -
> 23 keys in 365 slots is a table 6% full, and a collision is already a coin flip. So
> collisions are not what happens when a table gets crowded. They start immediately.

## Collision handling

Two keys hash to the same slot, and the second value still has to be stored. There are
only two places it can go: in with the first value, or in a different slot. Those two
answers are the two families of hash table.

Both families are costed in one number, so it needs a definition before it gets
used: the **load factor** is α = n/m, for n keys stored in m slots. It is
fullness as a fraction, so α = 0.5 is a half-full table and α = 1 is as many keys
as slots. Every cost below is quoted in α rather than in n, because what a table
costs depends on how full it is and not on how much it holds.

![Chaining vs Open Addressing](images/hash-chaining-vs-open.png)

### 1. Chaining

Every slot holds a list, so colliding keys pile up together and nothing has to move.
The table can never fill up, because a list has no fixed size, and deleting is just
removing an item from a list.

The cost is where the records live. Each one sits in its own list node somewhere else
in memory, so walking a chain means jumping to addresses the CPU has not already
loaded - that is what "not cache friendly" means, and it is why a chain of 3 can be
slower than 3 slots read side by side.

- **Time complexity:** O(l) where l is length of chain
- **Space:** Extra space for pointers/references

### 2. Open Addressing

One flat array, values stored directly in it, and a colliding key gets sent to a
different slot. Nothing is scattered, so reading a few neighbouring slots is nearly
free - the CPU loads them together anyway.

Two things get harder in exchange. The table has a real capacity, so it needs at least
as many slots as keys and must be rebuilt bigger when it runs out. And deleting stops
being simple, for the reason worked out in the tombstone section further down.

## Probing: three rules, each repairing the last

Open addressing needs a rule for "where next?". The three below are not alternatives
picked from a menu; each one exists because of the specific damage the previous one
does.

### 1. Linear Probing

- **Formula:** `hash(key, i) = (h(key) + i) % m`
- **Problem:** Primary clustering near occupied slots
- **Delete:** Mark slot as "DELETED" instead of empty

Try the next slot, then the next. It is the simplest rule, and the fastest to walk,
because the slots it visits sit next to each other in memory.

Its flaw feeds itself. A run of occupied slots captures every key that hashes anywhere
inside it, and each captured key is placed at the far end - so the run grows by one.
Longer runs capture more keys, so they grow faster than short ones. These runs are
*primary clusters*, and once one forms, a lookup that should have touched a single slot
walks the whole thing.

### 2. Quadratic Probing

- **Formula:** `h(key, i) = (h(key) + i²) % m`
- **Problem:** Secondary clustering
- **Requirements:** α < 0.5 and m is prime

Jump further on each attempt instead of stepping by one. The point is to stop keys from
being deposited right next to the cluster that deflected them, which is how a cluster
absorbs its neighbours and grows.

What it does not fix: the jump distance depends only on the attempt number `i`, so two
keys with the *same* home slot follow the exact same path and collide again at every
step. That is *secondary clustering*.

The jumps also do not reach every slot. With `m` prime and the table under half full,
a free slot is guaranteed to be found. Outside that, probing can cycle over a subset of
slots forever while empty ones sit unvisited - which is why the load factor is a
requirement here, not just a performance tip.

A table of 8 shows how little the probe can reach. Each column is one attempt `i`, and
the row below it is the slot that attempt lands on for a key whose home slot is 0:

```
i           0  1  2  3  4  5  6  7  8  ...
(0 + i²)%8  0  1  4  1  0  1  4  1  0  ...
```

The path only ever touches slots 0, 1 and 4, then repeats forever. Fill those three and
the table is 3/8 full - comfortably under the α < 0.5 line - yet a fourth key with home
slot 0 can never be placed, while slots 2, 3, 5, 6 and 7 sit empty. The squares collapse
onto three values because 8 is not prime.

Prime `m` is what widens that set: for an odd prime, the first (m+1)/2 attempts land on
(m+1)/2 *distinct* slots. That is the entire guarantee, and it is why both requirements
are listed together - the distinct slots are just over half the table, so only a table
under half full is certain to have a free one among them. Neither half stands alone: a
prime `m` past half full can still fail to place a key, and the trace above is α < 0.5
failing on an `m` that is not prime.

### 3. Double Hashing

- **Formula:** `h(key, i) = (h1(key) + i*h2(key)) % m`
- **Second hash:** `h2(key) = PRIME - (key % PRIME)`
- **Requirement:** h2(key) must be relatively prime to m and ≠ 0

Make the step size depend on the key. Now two keys sharing a home slot part company on
the very first jump, because they step by different amounts - secondary clustering gone,
the one repair quadratic probing could not make.

Both conditions on the step size are about not getting trapped. A step of 0 never moves,
so the probe spins on one slot. And a step that shares a factor with `m` walks a cycle
that covers only part of the table, so it can miss the free slots entirely - sharing no
factor is what *relatively prime* means. `PRIME - (key % PRIME)` is a standard choice
because it can never come out as 0.

## Why the load factor decides everything

α, not the number of keys, is what sets the cost of an operation. A table with a
million keys in two million slots is fast. A table with ten keys in ten slots is not.

A failed search is the honest measure, because it is the one that cannot stop early on
a match.

**Chaining is 1 + α.** One hash to reach the bucket, then a walk of the whole chain.
Chains are n/m = α long on average, so the walk costs α.

**Open addressing is 1/(1 - α).** A probe has an α chance of landing on an occupied slot
and needing another one, so the expected count is 1 + α + α² + ... , and that sum is
1/(1 - α).

| α | Chaining | Open addressing |
|---|---|---|
| 0.5 | 1.5 | 2 |
| 0.9 | 1.9 | 10 |
| 0.99 | 1.99 | 100 |

Chaining gets worse in a straight line. Open addressing has `1 - α` on the bottom, so
its cost climbs without limit as the table approaches full. This is the exact spot where
"O(1)" stops being true - it was always an average taken over a table kept loosely
packed, and nothing keeps it that way by itself. So a real implementation watches α and
rebuilds into a larger array before it gets near 1, which is the one piece of upkeep
neither collision strategy can skip.

## Chaining vs Open Addressing

1. **Capacity:** Chaining never fills up; OA requires resizing when full
2. **Hash sensitivity:** Chaining less sensitive; OA has clustering issues
3. **Cache performance:** Chaining not cache-friendly; OA is cache-friendly
4. **Space:** Chaining needs extra space for pointers; OA may need larger table for same performance

That list is one trade stated four ways. Open addressing is faster when the table is
kept loose and the hash is good, which is why CPython's `dict` uses it. Chaining is the
safer default when neither can be promised, because it gets worse gradually instead of
falling off a cliff.


### Chaining: the table

Each bucket holds a **list** of `(key, value)` records, so collisions simply pile up
in the same list instead of needing anywhere else to go.

`hash(key) % size` maps a key to a bucket. Two different keys can land in the same
bucket - that is expected, not an error - so every operation below has the same
shape: find the bucket in O(1), then scan that one short list.

That shape comes from one invariant, and the three operations are just readings
of it: **a key that is in the table is in bucket `hash(key) % size`, exactly
once.** Lookup is therefore "scan that bucket and report the record's value",
update is "scan that bucket and overwrite the record", delete is "scan that
bucket and drop the record". None of them has anywhere else it could look.

Collisions cannot hide a key from that scan, because a record is identified by
comparing keys and not by where it sits in the list. `append` puts a colliding
record after the ones already there without disturbing them, and `pop` shifts
later records down one, which changes nobody's identity. Position carries no
information here, which is what makes deletion trivial, and it is exactly what
open addressing gives up.

A prime `size` (7 here) spreads keys more evenly when hash values share factors with
the table size.

**Recipe**

1. Keep `size` and a list of `size` buckets, each an empty list.
2. **`[[] for _ in range(size)]`, never `[[]] * size`.** The multiplication makes
   one list and stores that same object `size` times, so appending to any bucket
   appends to all of them. It looks right until the first collision.
3. Store `(key, value)` pairs, not bare values - a record has to carry the key
   that proves which of the bucket's occupants it is.

```python
class ChainHash:
    def __init__(self, size=7):
        self.size = size
        self.buckets = [[] for _ in range(size)]
```

### Chaining: get

Hash to the bucket, then linearly scan that bucket comparing keys. The hash narrows
n keys down to one short list; the scan resolves which record in the list is the one
asked for.

Cost is `1 + α`: one hash, plus a walk of a chain that is n/size long on average.
Keep α around 1 and this is O(1); a table that is never resized degrades to O(n)
as chains grow.

Missing keys return `None` rather than raising.

**Time:** O(1) average, O(n) worst case (every key in one bucket)

**Recipe**

1. `bucket = self.buckets[hash(key) % self.size]`. **`% self.size` is what turns
   an arbitrarily large hash into a valid index, and it is repeated in every one
   of these three methods.**
2. `for rec_key, rec_val in bucket:` and `return rec_val` when
   `rec_key == key` - the comparison is on the stored key, not on position.
3. Fell off the end, `return None`. **That cannot distinguish a missing key from
   one stored with the value `None`**, which is why a real dict raises `KeyError`
   instead.

```python
def get_val(self, key):
    bucket = self.buckets[hash(key) % self.size]
    for rec_key, rec_val in bucket:
        if rec_key == key:
            return rec_val
    return None

ChainHash.get_val = get_val

def test_chainhash_get():
    chain_hash = ChainHash()
    assert chain_hash.get_val(2) is None  # empty bucket, nothing to scan
    # 3, 10 and 17 all hash to bucket 3, so only the key comparison can tell
    # them apart, and a hit may sit anywhere in the list.
    chain_hash.buckets[hash(3) % chain_hash.size] = [(3, "three"), (10, "ten")]
    assert chain_hash.get_val(3) == "three"
    assert chain_hash.get_val(10) == "ten"
    assert chain_hash.get_val(17) is None  # same bucket, absent from it

test_chainhash_get()
```

### Chaining: put

Same scan as `get`, with two outcomes: if the key is already in the bucket, replace
its record in place (a dict assigns, it does not accumulate duplicates); otherwise
append a new record.

The invariant is what forces the scan. "Exactly once" is not something the bucket
maintains on its own, it is something `put` has to keep true on every call.

**Time:** O(1) average, O(n) worst case &nbsp; **Space:** O(n) across all buckets

**Recipe**

1. Find the bucket the same way.
2. **Scan for the key before appending** - insert and update are the same call
   here. **Skip the scan and one key ends up with two records; `get_val` then
   returns the older one, because it stops at the first match.**
3. Found: `bucket[i] = (key, val)` and **`return` immediately**, or the append
   below runs too.
4. Not found: `bucket.append((key, val))`.
5. `enumerate(bucket)` to get `i` alongside the record, since the tuple is
   immutable and has to be replaced by index.

```python
def put_val(self, key, val):
    bucket = self.buckets[hash(key) % self.size]
    for i, (rec_key, _) in enumerate(bucket):
        if rec_key == key:
            bucket[i] = (key, val)
            return
    bucket.append((key, val))

ChainHash.put_val = put_val

def test_chainhash_put():
    chain_hash = ChainHash()
    chain_hash.put_val("name", "frodo")
    assert chain_hash.get_val("name") == "frodo"
    chain_hash.put_val("name", "gandalf")  # update, not a second record
    assert chain_hash.get_val("name") == "gandalf"
    chain_hash.put_val("nil", None)
    assert chain_hash.get_val("nil") is None  # same answer as a missing key
    # 3 and 10 collide, so updating one must neither disturb the other nor add
    # a duplicate record to the shared bucket.
    collide = ChainHash()
    collide.put_val(3, "three")
    collide.put_val(10, "ten")
    assert len(collide.buckets[3]) == 2
    collide.put_val(3, "THREE")
    assert len(collide.buckets[3]) == 2
    assert collide.get_val(3) == "THREE"
    assert collide.get_val(10) == "ten"

test_chainhash_put()
```

### Chaining: delete

Find the record in the bucket and pop it out of the list. Every other key is in
the bucket its own hash names, so removing this record cannot make any of them
harder to find - that is the whole of why chaining needs no tombstone, and it is
the point open addressing has to work for (see the tombstone note below).

Deleting a key that isn't present is a silent no-op.

**Time:** O(1) average, O(n) worst case

**Recipe**

1. Same bucket lookup, same linear scan.
2. Found: `bucket.pop(i)` and **`break`**.
3. **The `break` is not an optimisation.** Removing from a list while iterating
   over it makes the loop skip the next element, so continuing after a `pop` walks
   a list that has shifted underneath it.
4. No match, fall out of the loop and do nothing.

```python
def delete_val(self, key):
    bucket = self.buckets[hash(key) % self.size]
    for i, (rec_key, _) in enumerate(bucket):
        if rec_key == key:
            bucket.pop(i)
            break

ChainHash.delete_val = delete_val

def test_chainhash_delete():
    chain_hash = ChainHash()
    chain_hash.put_val("name", "frodo")
    chain_hash.delete_val("name")
    assert chain_hash.get_val("name") is None
    chain_hash.delete_val("name")  # deleting a missing key is a no-op
    assert chain_hash.get_val("name") is None
    # Deleting from the middle of a shared bucket must leave both neighbours
    # reachable: 3, 10 and 17 all live in bucket 3.
    collide = ChainHash()
    for key, val in ((3, "three"), (10, "ten"), (17, "seventeen")):
        collide.put_val(key, val)
    collide.delete_val(10)
    assert len(collide.buckets[3]) == 2
    assert collide.get_val(3) == "three"
    assert collide.get_val(17) == "seventeen"
    assert collide.get_val(10) is None

test_chainhash_delete()
```

### Open addressing: the table

No lists this time - every value lives directly in the array, so a collision has to
be resolved by finding a **different slot**. This implementation uses linear probing:
on collision, try `i + 1`, then `i + 2`, wrapping around with `% cap`.

Two sentinels share the array with real values:

| Marker | Meaning |
|---|---|
| `-1` | never used - a probe may stop here |
| `-2` | deleted (tombstone) - a probe must keep going |

Sharing the array has a price that is easy to miss: `-1` and `-2` are **reserved
values**, so the contract is that this is a set of integers other than those two.
Nothing enforces it, which is exactly why it has to be stated. `insert(-1)`
returns `True`, writes a slot that still reads as empty, and increments `size`, so
the value is unfindable and the count is now wrong; do it `cap` times and the
table rejects every later insert as full while every slot is in fact free.
`insert(-2)` writes a slot indistinguishable from a tombstone, and `search(-2)`
answers `True` for any table carrying a tombstone anywhere in the unbroken run
that starts at -2's own home slot, whether or not -2 was ever inserted. A
production table uses two
distinct marker objects rather than in-band integers, so no stored value can be
mistaken for one.

The probe path is the rest of the design. `insert` walks the path from `hash(x)`
and takes the first slot not already holding a value, which fixes one invariant:

> **If `x` is in the table, every slot from `hash(x)` up to the one holding `x`
> holds something - never `-1`.**

That unbroken run is what "reachable" means here, and it is the only fact the
other two operations need. Insert cannot break it, because it only ever turns a
`-1` or a `-2` into a value and never moves a value already placed: a key
deflected by a collision lands further along its own path, and the run behind it
is the trail that deflection left. Delete is the operation that *could* break it,
by putting a `-1` back in the middle of a run, and that is the entire reason for
the second sentinel.

**Time:** O(1) average, degrading as the load factor approaches 1

**Recipe**

1. `self.buckets = [-1] * cap` and `self.size = 0`. This is a plain list of ints,
   so `[-1] * cap` is safe here in a way `[[]] * cap` was not.
2. `hash(x)` is `x % self.cap`.
3. `insert`: `if self.size == self.cap: return False` first. **Without that guard
   a full table hangs**, because the probe in step 5 stops only on `-1` or `-2`
   and a full table has neither.
4. Then `if self.search(x): return False`. It makes this a set rather than a bag,
   and it is also **what makes the tombstone reuse in step 5 safe**: step 5 stops
   at the first `-1` or `-2`, so skipping the pre-search writes a second copy of
   `x` into a tombstone sitting in front of the copy already there - after which
   one `remove` clears only one of them and `search` still reports `x` present.
5. `i = self.hash(x)`, then `while t[i] not in (-1, -2): i = (i + 1) % self.cap`.
   **Insert treats a tombstone as free and reuses it; search must not.** That
   asymmetry between the two methods is the entire point of having two sentinels
   rather than one, and it is the part to get right cold.
6. `t[i] = x`, `self.size += 1`, `return True`. **Never pass `-1` or `-2` as
   `x`** - both are reserved and neither fails loudly.

```python
class OpenAddressHash:
    def __init__(self, cap):
        self.cap = cap
        self.buckets = [-1] * cap  # -1 = empty, -2 = deleted
        self.size = 0

    def hash(self, x):
        return x % self.cap

    def insert(self, x):
        if self.size == self.cap:
            return False
        if self.search(x):
            return False
        i = self.hash(x)
        t = self.buckets
        while t[i] not in (-1, -2):
            i = (i + 1) % self.cap
        t[i] = x
        self.size += 1
        return True
```

### Open addressing: search

Probe forward from the home slot until one of three things happens: the value turns
up, an **empty** (`-1`) slot appears, or the probe wraps back to where it started.

Stopping on an empty slot is the step that gives up, so it is the one that needs
justifying, and the invariant is the justification. A `-1` here would contradict
"every slot from `hash(x)` up to `x` holds something", so `x` cannot be sitting
further along. A slot that was never written is proof that `x` was never inserted.

A tombstone (`-2`) proves nothing of the kind. It holds something, so the
invariant is still satisfied and the run is still unbroken; all `-2` says is
"something was here and left", and a key that insertion pushed past it is still
further along the path. Treat one as empty and the search declares keys missing
that are sitting one slot away.

The `i == h` guard follows from the loop condition, not from anything about
probing. A `-1` is the loop's only way to finish without a match, so on a table
holding no `-1` at all - every slot either a value or a tombstone - a failed
search never leaves the loop, and the probe circles forever. The guard is also not
giving up early: the step is 1, so the path
visits all `cap` slots before it can arrive back at `h`, and by then every slot has
been compared to `x`. Coming full circle is a complete negative answer rather than
a timeout.

**Time:** O(1) average, O(n) worst case

**Recipe**

1. `h = self.hash(x)`, `t = self.buckets`, `i = h`.
2. `while t[i] != -1:` - an empty slot is the only content that ends the search.
   **Write `-1` on delete instead of `-2` and the search stops in the hole.**
   Insert 10, 17 and 24 into a table of 7 and they land in slots 3, 4 and 5.
   Blank slot 4 by removing 17, and `search(24)` returns `False` with 24 sitting
   untouched in slot 5.
3. `if t[i] == x: return True`. **An `x` of `-2` matches any tombstone on its
   path**, which is the reserved-value contract biting.
4. `i = (i + 1) % self.cap`, then `if i == h: return False`, **because on a table
   with no empty slot the `-1` test never fires** and the probe circles forever.
5. `return False` below the loop, for the empty-slot exit.

```python
def search(self, x):
    h = self.hash(x)
    t = self.buckets
    i = h
    while t[i] != -1:
        if t[i] == x:
            return True
        i = (i + 1) % self.cap
        if i == h:
            return False
    return False

OpenAddressHash.search = search

def test_open_address_search():
    oa_hash = OpenAddressHash(7)
    assert not oa_hash.search(10)  # empty table, the home slot is already -1
    oa_hash.insert(10)
    assert oa_hash.search(10)
    # 17 and 24 share 10's home slot, so they are pushed to 4 and 5 and are only
    # reachable by walking the unbroken run that starts at slot 3.
    assert oa_hash.insert(17)
    assert oa_hash.insert(24)
    assert oa_hash.buckets[3:6] == [10, 17, 24]
    assert oa_hash.search(24)
    assert not oa_hash.search(31)  # same home slot, never inserted
    assert not oa_hash.insert(24)  # already present, so this behaves as a set
    assert oa_hash.size == 3
    # A table with no -1 left can only terminate via the i == h guard.
    full = OpenAddressHash(3)
    for value in (1, 2, 3):
        assert full.insert(value)
    assert -1 not in full.buckets
    assert not full.search(99)
    # Reserved value: inserting -1 "succeeds" but stores an invisible phantom.
    phantom = OpenAddressHash(7)
    assert phantom.insert(-1)
    assert phantom.size == 1
    assert not phantom.search(-1)  # the slot it wrote still reads as empty

test_open_address_search()
```

### Open addressing: remove

Same probe as `search`, but on a match the slot is set to `-2` rather than `-1`.

Writing `-1` would break the invariant directly: it puts a hole back into a run,
and every key further along that run becomes unreachable while still sitting in
the table. `-2` counts as "holds something", so the run stays unbroken, while
`insert` is still free to reuse the slot.

`size` counts live values, not occupied-looking slots. Deletion must decrement it
when the value becomes a tombstone. Otherwise a table that was once full stays
logically full forever, and `insert` rejects the tombstone it is supposed to reuse.

The cost is that tombstones accumulate and lengthen probes over time, so a real
implementation rehashes the table periodically to clear them out.

**Time:** O(1) average, O(n) worst case

**Recipe**

1. `h = self.hash(x)`, `i = h`, `while t[i] != -1`, step `i = (i + 1) % self.cap`,
   `if i == h: return False` - identical probe to `search`, same stop condition
   and same full-circle guard.
2. Found: `t[i] = -2`, **the tombstone, not `-1`**.
3. `self.size -= 1`, because it counts live values. **Leave it unchanged and a
   once-full table can never insert again, even though a tombstone is free.**
4. `return True`; `return False` on both the empty-slot and full-circle exits.

```python
def remove(self, x):
    h = self.hash(x)
    t = self.buckets
    i = h
    while t[i] != -1:
        if t[i] == x:
            t[i] = -2  # mark as deleted without cutting the probe chain
            self.size -= 1
            return True
        i = (i + 1) % self.cap
        if i == h:
            return False
    return False

OpenAddressHash.remove = remove

def test_open_address_remove():
    # All three values collide, so 7 sits beyond 4 in the same probe chain.
    oa_hash = OpenAddressHash(3)
    for value in (1, 4, 7):
        assert oa_hash.insert(value)
    assert oa_hash.size == 3
    assert not oa_hash.insert(10)  # genuinely full

    assert oa_hash.remove(4)
    assert oa_hash.size == 2
    assert not oa_hash.search(4)
    assert oa_hash.search(7)  # search walks through 4's tombstone

    assert oa_hash.insert(10)  # the once-full table reuses that tombstone
    assert oa_hash.size == 3
    assert oa_hash.search(10)

    # Deleting from the middle of a longer cluster: 10, 17, 24 -> slots 3, 4, 5.
    cluster = OpenAddressHash(7)
    for value in (10, 17, 24):
        assert cluster.insert(value)
    assert cluster.remove(17)
    assert cluster.buckets[3:6] == [10, -2, 24]  # hole is a tombstone, not -1
    assert cluster.search(24)  # 24 is still reachable across it
    # insert's pre-search finds 24 across the tombstone, so the tombstone is not
    # reused for a second copy of a key that is already present.
    assert not cluster.insert(24)
    assert cluster.buckets[3:6] == [10, -2, 24]
    assert not cluster.remove(17)  # already gone
    assert not cluster.remove(99)  # never present

    # Reserved value: -2 is answered by any tombstone on its own probe path.
    reserved = OpenAddressHash(7)
    assert reserved.insert(5)
    assert reserved.remove(5)  # leaves -2 in slot 5, which is -2's home slot
    assert reserved.search(-2)  # never inserted, reported present anyway

test_open_address_remove()
```

## Python Built-in Hash Structures

Python's `dict` uses open addressing. Average O(1) for get/set/delete. Since 3.7 iteration
follows insertion order, which comes from records being kept in a separate compact array
that the table stores indexes into - it is a property of that layout, not something a hash
can promise.

| Built-in | Use case |
|----------|----------|
| `dict` | General key-value mapping |
| `set` | Membership testing, deduplication |
| `defaultdict` | Dict with auto-initialized default values |
| `Counter` | Frequency counting |

```python
from collections import defaultdict, Counter

# dict - O(1) average for get, set, delete, 'in'
d = {'a': 1, 'b': 2}
d['c'] = 3
print('a' in d)          # True - O(1) membership test
print(d.get('z', 0))     # 0 - safe access with default

# set - O(1) average for add, remove, 'in'
s = {1, 2, 3}
s.add(4)
print(s & {2, 3, 5})     # {2, 3} - intersection
print(s | {5, 6})        # {1, 2, 3, 4, 5, 6} - union

# defaultdict - auto-creates missing keys with a factory
graph = defaultdict(list)
graph['a'].append('b')   # no KeyError, creates [] first
graph['a'].append('c')
print(dict(graph))       # {'a': ['b', 'c']}

# Counter - frequency counting in one line
freq = Counter('abracadabra')
print(freq)              # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
print(freq.most_common(2))  # [('a', 5), ('b', 2)]
```

## Sets

A set is a hash table that stores only keys (no values). Same O(1) average for add, remove, and membership test.

### Hash Set (`set`)

| Operation | Time | Notes |
|-----------|------|-------|
| `add(x)` | O(1) avg | |
| `remove(x)` | O(1) avg | raises `KeyError` if missing |
| `discard(x)` | O(1) avg | no error if missing |
| `x in s` | O(1) avg | |
| `s \| t` (union) | O(len(s) + len(t)) | |
| `s & t` (intersection) | O(min(len(s), len(t))) | |
| `s - t` (difference) | O(len(s)) | |
| `s ^ t` (symmetric diff) | O(len(s) + len(t)) | elements in either but not both |

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)   # {1, 2, 3, 4, 5, 6} - union
print(a & b)   # {3, 4}             - intersection
print(a - b)   # {1, 2}             - difference
print(a ^ b)   # {1, 2, 5, 6}       - symmetric difference
print(a <= b)  # False              - subset check

# frozenset - immutable, can be used as dict key or set element
fs = frozenset([1, 2, 3])
d = {fs: 'value'}  # works because frozenset is hashable
```

### Sorted Set

Python has no built-in sorted set. Java has `TreeSet` (Red-Black tree) and C++ has `std::set` (also RB tree).

| Operation | Hash Set | Sorted Set (BST) |
|-----------|----------|-------------------|
| Add/Remove/Search | O(1) avg | O(log n) |
| Min/Max | O(n) | O(log n) |
| Ordered iteration | O(n log n) sort | O(n) inorder |
| Range query (a..b) | O(n) | O(log n + k) |
| Floor/Ceiling | O(n) | O(log n) |

**When to use sorted set:** When you need ordered operations (min, max, floor, ceiling, range queries) alongside fast insert/delete.

**Python options:**
- `sortedcontainers.SortedSet` - third-party, B-tree based, excellent performance
- BST (see [Binary Search Tree notebook](../trees/binary-search-tree.md)) - the underlying data structure
- `bisect` + `list` - works for small sets, but insert/delete is O(n) due to shifting
