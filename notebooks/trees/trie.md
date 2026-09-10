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

# Trie (Prefix Tree)

A tree where each node represents a character. Paths from root to marked nodes form words.

**Why not a hash set of words?** A trie supports **prefix search** in O(prefix length) - try doing that efficiently with a set.

| Operation | Time | Hash Set |
|-----------|------|----------|
| Insert word | O(L) | O(L) |
| Search word | O(L) | O(L) |
| Prefix search | O(P) | O(N × L) |
| Autocomplete | O(P + matches) | O(N × L) |

L = word length, P = prefix length, N = number of words

**Applications:** Autocomplete, spell checkers, IP routing, word games.

> **Mental model.** The key *is* the path. No node stores a word - a word is just the sequence
> of edges you walked to reach a node, one character per edge. That is why prefix queries come
> for free: a prefix is a path you have already walked, and everything hanging below where it
> ends is a word starting with it. Cost depends on the length of the query, never on how many
> words are stored.
>
> **Load-bearing:** the end-of-word marker (`'$'` here). Reaching a node proves the path
> exists, not that the path is a word. Without the marker you cannot tell a word you stored
> from the front of a longer one - `'app'` sits on the way to `'apple'`, and only the marker
> says which of the two was actually inserted.

> **Procedural vs class-based:** The functions below operate on a simple dict-of-dicts trie structure - no wrapper class needed. Each node is just a dict where keys are characters and a special `'$'` key marks end of word.

![Trie Structure](images/trie.png)


## Core Operations

A node is just a dict mapping a character to a child node, so the trie is a dict of dicts.

```
insert 'app', 'apple', 'bat'

{
  'a': {'p': {'p': {'$': True,
                    'l': {'e': {'$': True}}}}},
  'b': {'a': {'t': {'$': True}}}
}
```

Shared prefixes are stored once - `'app'` and `'apple'` walk the same three nodes, which is
where the space saving and the prefix queries both come from.

Every operation begins the same way, and not by choice. Nothing here stores a string, so the
only question a node can answer about a string is "is there an edge for the next character?".
Answering it repeatedly *is* the descent: standing at `node` with character `ch`, `ch in node`
decides whether the prefix read so far, extended by `ch`, is reachable. If it is,
`node = node[ch]` and the question repeats one character later; if it is not, no stored word
has that prefix and the query can stop right there with a miss. That is why cost is the
query's length and never the number of words.

Running out of characters leaves you at a node, and reaching a node is where the descent's
knowledge ends. It proves the path exists. It says nothing about whether that path is a word,
because words and paths are different things - `'app'` is a path inside `'apple'` whether or
not anyone inserted it. Only `'$'` distinguishes them, so the two queries split exactly there:

| Function | Question at the end of the walk | Answer |
|---|---|---|
| `search` | is this path a stored word? | `'$' in node` |
| `starts_with` | does any word continue from here? | `True` - arriving is the proof |

The degenerate case makes the split concrete. On an empty trie the walk for `''` ends
immediately at the root, so `starts_with(t, '')` is `True` - the empty path is trivially
reachable - while `search(t, '')` is `False`, because nobody marked the root.

`insert` is the same descent with one change: a missing character is created rather than
being a miss (`node[ch] = {}`), and the node you land on gets `node['$'] = True`. `'$'` can
serve as that marker only because it cannot occur inside a word - any sentinel outside the
alphabet does, and one that is a real character would be read as an edge.

**Time:** O(L) insert and search, O(P) prefix check &nbsp; **Space:** O(total characters)

**Recipe**

1. `insert`: for each `ch` in `word`, `if ch not in node: node[ch] = {}`, then
   `node = node[ch]`. After the loop, `node['$'] = True`.
2. `search`: same loop, but `if ch not in node: return False`. After the loop
   return **`'$' in node`, never `True`** - `True` there makes every prefix report
   as a stored word.
3. `starts_with`: byte-for-byte `search`, ending in plain `True`. **The only
   difference between the two functions is that last line**, so writing one and
   copying it is the reliable way to get both.

```python
def create_trie():
    """A trie node is just a dict. Keys = child characters, '$' = end of word."""
    return {}

def insert(root, word):
    """Insert word into trie. Time: O(L)"""
    node = root
    for ch in word:
        if ch not in node:
            node[ch] = {}
        node = node[ch]
    node['$'] = True  # mark end of word

def search(root, word):
    """Return True if word was inserted as a whole word. Time: O(L)"""
    node = root
    for ch in word:
        if ch not in node:
            return False  # path breaks, so no stored word has this prefix
        node = node[ch]
    return '$' in node  # path exists; '$' is what makes it a word

def starts_with(root, prefix):
    """Return True if any word starts with prefix. Time: O(P)"""
    node = root
    for ch in prefix:
        if ch not in node:
            return False
        node = node[ch]
    return True  # the whole prefix path exists, including the empty path at root

def test_core():
    t = create_trie()
    insert(t, 'apple')
    insert(t, 'app')
    insert(t, 'bat')
    assert search(t, 'apple')
    assert search(t, 'app')
    assert not (search(t, 'ap'))          # reachable path, never marked a word
    assert not (search(t, 'appl'))        # ditto, one character further in
    assert not (search(t, 'applesauce'))  # path breaks partway
    assert starts_with(t, 'ap')
    assert starts_with(t, 'apple')        # a word is a prefix of itself
    assert not (starts_with(t, 'bx'))

    # single-character word, and the degenerate empty query
    one = create_trie()
    insert(one, 'a')
    assert search(one, 'a')
    empty = create_trie()
    assert starts_with(empty, '')      # the empty path is trivially reachable
    assert not (search(empty, ''))     # but the root carries no '$'

test_core()
```

## Autocomplete (Words with Prefix)

The output is every stored word that begins with the prefix, and producing it needs the two
questions the core operations already separated, in that order. Reachability first: walk the
prefix, and if the path breaks then nothing has it, so the answer is `[]`. Landing on a node
means every path hanging below it is reachable through the prefix - which is the whole reason
a trie answers this without touching the rest of the dictionary. End-of-word status second:
among all those paths, the words are the ones whose node carries `'$'`.

So the collecting walk needs to know where it is and what it has spelled. `dfs(node, path)`
carries exactly that: `path` is the characters walked *below* the prefix, so the word standing
at `node` is `prefix + ''.join(path)`. It returns nothing - `results` is appended to - and
`path` is un-appended after each branch (`path.pop()`) so the one list serves every branch,
which is the standard backtracking pattern.

```
trie holds: app, apple, application, bat, ball

autocomplete('app'):
  walk a → p → p                      lands on the shared 'app' node
  DFS from there, path starts empty:
    '$' present            → 'app'
    l → e → '$'            → 'apple'
    l → i → c → …→ '$'     → 'application'
```

Cost is O(P + total characters in the matches), i.e. proportional to the answer rather than
to the dictionary. A hash set would have to test all N words.

**Time:** O(P + output size) &nbsp; **Space:** O(output size)

**Recipe**

1. Walk the prefix with the `if ch not in node: return []` guard, exactly as
   `starts_with` does.
2. In the DFS, `if '$' in node: results.append(prefix + ''.join(path))`. **Not an
   early return** - a node can end one word and continue into others, which is how
   `app` is emitted and the walk still reaches `apple`.
3. Iterate `node.items()` under `if ch != '$'`. **Skipping that check recurses into
   `True`**, which raises, because `'$'` maps to a bool and not to a child dict.
4. `path.append(ch)` before the recursive call, `path.pop()` after. **Drop the pop
   and every sibling branch inherits the characters of the one before it** - on the
   trie below, `autocomplete('ba')` returns `['bat', 'batll']` instead of
   `['bat', 'ball']`.
5. `return results` from the outer function after `dfs(node, [])`; the DFS itself
   returns nothing.

```python
def autocomplete(root, prefix):
    """
    Return all words that start with prefix.
    Time: O(P + total characters in matching words)
    """
    node = root
    for ch in prefix:
        if ch not in node:
            return []
        node = node[ch]
    # DFS to collect all words from this node
    results = []
    def dfs(node, path):
        # path holds the characters below the prefix, so the word here is
        # prefix + path. Returns nothing; results is appended to.
        if '$' in node:
            results.append(prefix + ''.join(path))
        for ch, child in node.items():
            if ch != '$':  # '$' maps to True, not to a child node
                path.append(ch)
                dfs(child, path)
                path.pop()
    dfs(node, [])
    return results

def test_autocomplete():
    t = create_trie()
    for w in ['apple', 'app', 'application', 'bat', 'ball']:
        insert(t, w)
    res = sorted(autocomplete(t, 'app'))
    assert res == ['app', 'apple', 'application']  # 'app' both ends and continues
    assert sorted(autocomplete(t, 'ba')) == ['ball', 'bat']  # pop keeps these apart
    assert autocomplete(t, 'bat') == ['bat']       # a whole word, nothing below it
    assert autocomplete(t, 'xyz') == []            # path breaks at 'x'
    assert len(autocomplete(t, '')) == 5           # empty prefix reaches everything
    assert autocomplete(create_trie(), 'a') == []

test_autocomplete()
```

## Delete Word

Two things have to be true when this returns: the word is no longer a word, and no node is
left that nothing needs. The first is one key deletion at the node the word ends on. The
second cannot be decided on the way down, because whether a node is still needed depends on
what is left *below* it after the deletion - so it has to be decided coming back up, one
level at a time. That is what the recursion returns.

Name that return precisely, because it is the whole difficulty: `_delete(node, i)` returns
**"I am now useless, my parent may unlink me"**. Each caller unlinks its child only if it got
a `True`, then works out its own verdict. A node is useless only when it has no children left
*and* it is not itself the end of another word - the same path-versus-word split as before,
now deciding what may be freed rather than what may be reported.

The split also decides what counts as a hit. Reaching the end of `word` proves the path
exists; only `'$'` proves the word was stored. Deleting `'app'` from a trie holding just
`'apple'` walks the path cleanly and must still change nothing.

```
trie: app, apple      a → p → p($) → l → e($)

delete('apple')
  descend to the 'e' node, remove its '$'   → node is empty → return True
  at 'l': delete child 'e', 'l' now empty and not a word → return True
  at the second 'p': delete child 'l' - but this node has '$' (it is 'app')
                     → stop pruning, return False

result: a → p → p($)     'app' survives

delete('app')
  remove '$' from the second 'p' - no children left → return True
  every ancestor is then childless and unmarked → the whole branch is pruned
```

That last `False` is not a failure report, and reading it as one is the bug this function
invites: the word was removed, the node just could not be. Hence a separate `found` flag.

**Time:** O(L) &nbsp; **Space:** O(L) recursion

**Recipe**

1. `_delete(node, i)` returns a bool the parent reads as **"you may unlink the child
   I just handled"**.
2. `if i == len(word)`: `if '$' not in node: return False` - the path exists but was
   never a word. Otherwise `del node['$']`, set `found = True`, and
   `return len(node) == 0`.
3. Otherwise `ch = word[i]`, and `if ch not in node: return False` - the path breaks,
   so there is nothing to unlink and nothing to report.
4. `if _delete(node[ch], i + 1):` then `del node[ch]` and
   `return len(node) == 0 and '$' not in node`; otherwise `return False`.
5. **Both halves of that condition are load-bearing.** Drop `'$' not in node` and
   unlinking a childless node silently deletes the shorter word that ended there.
6. `found` is a `nonlocal` flag set at the one place `'$'` is removed. The outer
   function discards `_delete`'s return value and does `return found`. **Return the
   recursion's bool instead and deleting `'app'` out of `{app, apple}` reports
   `False` on a word it did remove.**

```python
def delete(root, word):
    """
    Delete word from trie. Only removes nodes that aren't shared with other words.
    Returns True if the word was found and deleted, False if it was never there.
    Time: O(L)
    """
    found = False

    def _delete(node, i):
        """True if node is now safe for its parent to unlink."""
        nonlocal found
        if i == len(word):
            if '$' not in node:
                return False  # path exists, but it was never a word
            del node['$']
            found = True
            return len(node) == 0  # can delete this node if no children
        ch = word[i]
        if ch not in node:
            return False
        if _delete(node[ch], i + 1):
            del node[ch]
            return len(node) == 0 and '$' not in node
        return False

    _delete(root, 0)
    return found

def test_delete():
    t = create_trie()
    insert(t, 'apple')
    insert(t, 'app')
    assert delete(t, 'apple')
    assert not (search(t, 'apple'))
    assert search(t, 'app')  # 'app' still exists
    assert delete(t, 'app')
    assert not (search(t, 'app'))
    assert not (starts_with(t, 'a'))  # trie is empty

    # the other order: 'app' goes while its node must stay, because 'apple' needs it.
    # _delete returns False all the way up, and the found flag is what reports True.
    t = create_trie()
    insert(t, 'apple')
    insert(t, 'app')
    assert delete(t, 'app')
    assert not (search(t, 'app'))
    assert search(t, 'apple')      # untouched
    assert starts_with(t, 'app')   # its path is still there, it is just not a word

    # a word that was never inserted reports False and prunes nothing
    t = create_trie()
    insert(t, 'apple')
    assert not (delete(t, 'nope'))
    assert not (delete(t, 'app'))         # a prefix of a word is not a word
    assert not (delete(t, 'applesauce'))  # runs off the end of the path
    assert search(t, 'apple')             # nothing was disturbed
    assert delete(t, 'apple')             # deleting it once works
    assert not (delete(t, 'apple'))       # deleting it twice reports False
    assert not (starts_with(t, 'a'))      # and the branch is gone

test_delete()
```
