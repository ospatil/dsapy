# Recall

Every mental-model card from the notebooks, with the answers hidden.

Cold, after months away, this is the cheapest way back in. Read a topic, say the
idea out loud or sketch the loop, *then* expand the card and compare. The gap
between what you produced and what is written is the only part worth re-reading,
and it tells you which notebook to open.

Generated from the notebooks by `make recall` - edit the cards there, not here.

## [01-notation](notebooks/analysis/01-notation.md)

<details>
<summary><strong>Analysis of algorithms</strong></summary>

> **Mental model.** Throw away everything a faster machine could change, and keep what it
> cannot. Constants and lower-order terms shift with the CPU, the language and the compiler;
> the growth rate survives all three, so the growth rate is the only part that describes the
> *algorithm* rather than the machine it ran on. The two shortcuts - drop lower-order terms,
> drop leading constants - are not conventions to memorise, they are exactly what the limit
> $\lim_{n \to \infty} g(n)/f(n)$ leaves standing. Keep one further pair apart: a **case**
> (best, average, worst) picks which *input* you feed the algorithm, while a **notation** (O,
> Ω, Θ) picks how *tightly* you bound the function that input produced. They are independent
> choices, so any case can be stated in any notation.
>
> **Load-bearing:** the crossover always exists. No values of $c_1, c_2, c_3$ can keep
> $c_2n + c_3$ ahead of $c_1$ forever - that guarantee is the entire licence to discard
> constants, and every simplification here rests on it. It also marks the limit of the whole
> method: the crossover between two real programs can sit at an $n$ larger than any input you
> will ever run, and for those inputs the faster-growing algorithm is the one to ship.

</details>

## [02-common-loops](notebooks/analysis/02-common-loops.md)

<details>
<summary><strong>Analysis of Common Loops</strong></summary>

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
> [01](notebooks/analysis/01-notation.md) came from. Both land on $\Theta(n^2)$ here, which is the trap: multiply
> a bound that secretly depends on $i$ and you are right by luck, then wrong the moment the
> inner loop is logarithmic or the outer range is not $n$.

</details>

## [03-recursion](notebooks/analysis/03-recursion.md)

<details>
<summary><strong>Analysis of Recursion</strong></summary>

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

</details>

## [04-space-complexity](notebooks/analysis/04-space-complexity.md)

<details>
<summary><strong>Space Complexity</strong></summary>

> **Mental model.** Split the total from the extra. Space for the input and the output is
> forced on you - taking an array of $n$ items costs $\Theta(n)$ no matter how cleverly you
> write the function - so the only figure that reflects a decision *you* made is the
> **auxiliary** space stacked on top. For a recursive function that extra is the call stack,
> and the stack only ever holds one path from the root down to the call executing right now.
> Siblings are never on it at the same time. So auxiliary space is the recursion tree's
> **height**, not its number of nodes.
>
> **Load-bearing:** height rather than node count, and the gap between them is enormous.
> `fib(n)` makes about $2^n$ calls yet never has more than $n$ frames alive, because
> `fib(n-2)` does not begin until `fib(n-1)` has finished and left the stack entirely. Miss
> that and you price this at $\Theta(2^n)$ memory instead of $\Theta(n)$. The same rule shows
> where space goes when the shape changes: filling a table keeps every value alive at once for
> $\Theta(n)$ auxiliary space, while carrying only the last two values needs $\Theta(1)$.

</details>

## [05-amortized-analysis](notebooks/analysis/05-amortized-analysis.md)

<details>
<summary><strong>Amortized Analysis</strong></summary>

> **Mental model.** Stop pricing one call and price the whole sequence. A rare expensive
> operation is paid for by the many cheap operations around it, because the expensive one can
> only happen *after* enough cheap ones have piled up work for it. The cheap calls pre-pay.
>
> **Load-bearing:** the guarantee is worst-case over *any* sequence, not an average over
> lucky inputs. Nothing here assumes anything about the input. That is also where it breaks:
> the argument only holds while the expensive step stays rare. Grow the array by a fixed 1
> slot instead of doubling and every append copies everything, so there is nothing cheap left
> to pay the bill and the cost really is O(n) each.

</details>

## [stacks-and-queues](notebooks/stacks-and-queues/stacks-and-queues.md)

<details>
<summary><strong>Stacks and Queues</strong></summary>

> **Mental model.** One question separates the two: which end do you take from? Take from the
> same end you added to and the newest item leaves first - that is a stack, LIFO. Take from the
> other end and the oldest leaves first - that is a queue, FIFO. Every use case follows from
> that one choice. Undo, bracket matching and DFS all need the most recent thing back;
> scheduling, buffering and BFS all need the one that has waited longest.
>
> **Load-bearing:** where those ends sit in memory. For a Python `list`, push and pop must both
> happen at the *end*, because inserting or removing at index 0 shifts every remaining element
> and quietly turns O(1) into O(n). A queue needs two opposite ends, so it either walks indices
> through a fixed array (the circular queue below) or uses `deque`, which exists precisely to
> be O(1) at both ends.

</details>

## [singly-linked-list](notebooks/linked-lists/singly-linked-list.md)

<details>
<summary><strong>Singly Linked List</strong></summary>

> **Mental model.** A chain you can only walk forwards, one node at a time. Every
> operation comes down to parking a pointer on the node *before* the spot you want to
> change, then rewiring - which is the whole reason for the dummy head: it guarantees
> that "node before" always exists, even in an empty list, so no operation needs a
> special case for the front.
>
> **Load-bearing:** you cannot step backwards. Anything that needs the node before the
> target pays a walk to find it - that alone is why `delete_last` is O(n) while
> `delete_first` is O(1) - and any pointer you are about to overwrite must be saved
> first, or the rest of the list becomes unreachable.

</details>

## [doubly-linked-list](notebooks/linked-lists/doubly-linked-list.md)

<details>
<summary><strong>Doubly Linked List</strong></summary>

> **Mental model.** A [singly linked list](notebooks/linked-lists/singly-linked-list.md) can only look forwards.
> Every change there needs the node *before* the target, and finding it costs a walk -
> that one limit is where its whole cost model comes from. The `prev` pointer buys exactly
> one thing back: hand it a node and it can unlink that node without knowing what came
> before. So deleting a node you already hold drops from O(n) to O(1), and the reversal
> that needed a temporary variable no longer needs one, because the rest of the list stays
> reachable from the node just moved. The price is one more pointer per node than a singly
> linked list carries.
>
> **Load-bearing:** every operation now has to fix *two* directions, and it has to fix
> them as a pair. Repair only the `next` links and the list still walks correctly
> forwards. It lies only when walked backwards - so half the tests keep passing, which is
> the worst kind of bug to be handed.

</details>

## [circular-linked-list](notebooks/linked-lists/circular-linked-list.md)

<details>
<summary><strong>Circular Linked List</strong></summary>

> **Mental model.** A ring with a label on it. `head.next` is the label, and all it
> says is which node counts as first - which also fixes the last node, since the
> last node is whichever one points at the first. Nothing in the pointers marks
> either end, so moving the label is enough to turn an insert at the front into an
> insert at the back.
>
> **Load-bearing:** the stopping rule of every loop. `while curr` never becomes
> false here, because `next` is never `None`. A walk has to stop when it arrives
> back where it started, so the *first* node is the boundary instead of a `None` at
> the end. The empty list is the case that needs care, because there is no node to
> come back to - that is what every `if not first` guard is for.

</details>

## [binary-search](notebooks/searching/binary-search.md)

<details>
<summary><strong>Binary Search</strong></summary>

> **Mental model.** The loop is not really hunting for a value. It maintains a window
> `[lo, hi]` that is guaranteed to contain the answer, if the answer exists at all. Each step
> looks at the middle and throws away the half that cannot hold it. Sortedness is what makes
> that discard safe - one comparison rules out everything on one side at once.
>
> **Load-bearing:** what the window means at its edges. Is `hi` inside the window or one past
> it? Does a match stop the search or stay a candidate while you keep looking left? Those two
> choices are the entire difference between plain search, `lower_bound` and `upper_bound` -
> and they are why every off-by-one bug here lives in the `lo` and `hi` update lines, never in
> the comparison.

</details>

## [basic-sorts](notebooks/sorting/basic-sorts.md)

<details>
<summary><strong>Basic Sorting Algorithms</strong></summary>

> **Mental model.** All three cost O(n²) for the same reason: each element ends up compared
> against many others, and n elements times roughly n comparisons each is n². What separates
> them is what they *do* with a comparison. Bubble sort swaps the pair on the spot, so a
> value crawls towards its place one slot at a time. Selection sort refuses to move anything
> until it has scanned the whole unsorted remainder and knows the true minimum, then puts it
> straight where it belongs. Insertion sort compares only until it meets something smaller,
> and stops there.
>
> **Load-bearing:** that "stops there". Insertion sort is the only one of the three that is
> genuinely fast on nearly-sorted input, because a value that is already close to its place
> stops after one or two comparisons - Θ(n) for the whole array. Bubble sort's `swapped` flag
> only spots an array that is *already* sorted and does nothing for one that is merely close,
> and selection sort has no fast case at all, since the scan always covers the entire
> remainder. That is why real library sorts, Timsort included, fall back to insertion sort on
> short runs rather than to either of the other two.

</details>

## [merge-sort](notebooks/sorting/merge-sort.md)

<details>
<summary><strong>Merge Sort</strong></summary>

> **Mental model.** Splitting is free and the merge is the whole algorithm. Two sorted runs
> can be combined in a single pass, because the smallest element left has to be at the front
> of one of them. The recursion exists only to guarantee you are never asked to do anything
> harder than that: keep halving until a run holds one element, which is sorted by
> definition, and from then on every merge is handed two runs that are already sorted.
>
> **Load-bearing:** the merge needs somewhere to write. It cannot write into the same slots
> it is still reading from, so it copies the two runs out first. That copy is the O(n) extra
> space, and the reason merge sort is not in place. The second piece is the tie rule: when
> two elements are equal, taking the one from the left run is the only thing keeping the sort
> stable. Change `<=` to `<` and equal elements come out in the wrong order.

</details>

## [quick-sort](notebooks/sorting/quick-sort.md)

<details>
<summary><strong>Quick Sort</strong></summary>

> **Mental model.** Quick sort is merge sort held up to a mirror. Merge sort splits cheaply
> and pays for it in the merge. Quick sort pays up front in the split and then has nothing
> left to do, because partitioning already puts the pivot in the slot it will occupy in the
> finished array - forever. Everything smaller is somewhere on its left, everything larger
> somewhere on its right, so the two sides never have to look at each other again. Sort both
> sides and the array is sorted. There is no combine step at all.
>
> **Load-bearing:** which element you pick as the pivot. The pivot decides how evenly the
> range splits, and only an even split gives log n levels of recursion. A pivot that turns
> out to be the smallest or largest value peels off one element and leaves n-1 behind, so the
> recursion runs n levels deep and the cost climbs to O(n²). The case worth remembering: both
> schemes below take the pivot from a fixed end of the range, so already-sorted input hits
> that worst case every single time.

</details>

## [counting-radix-sort](notebooks/sorting/counting-radix-sort.md)

<details>
<summary><strong>Non-Comparison Sorts</strong></summary>

> **Mental model.** Neither of these sorts ever compares two elements. They use the value
> itself as an index - the value 3 goes to slot 3 of a counting array - so the order falls out
> of arithmetic instead of out of comparisons. That is how they get under the O(n log n) floor.
> The floor was never a law about sorting; it only ever applied to algorithms that decide
> everything by asking "is a bigger than b?".
>
> **Load-bearing:** the values have to be integers in a known and small range. The cost
> carries a k term, the size of that range, because a slot is reserved and walked for every
> possible value whether or not anything lands in it. Sort three numbers near a million and
> counting sort allocates a million slots, which is far worse than just comparing the three.
> Radix sort is the repair for exactly that: chop each number into digits so the range one
> pass has to cover is always 10.

</details>

## [hash-tables](notebooks/hashing/hash-tables.md)

<details>
<summary><strong>Hash Tables</strong></summary>

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

</details>

## [binary-tree](notebooks/trees/binary-tree.md)

<details>
<summary><strong>Binary Trees</strong></summary>

> **Mental model.** Almost everything in this notebook is one recursive shape: do the
> left subtree, do the right subtree, combine. Traversals combine by appending to a
> list, `size` combines with `+`, `get_max` with `max`, `search` with `or`. Preorder,
> inorder and postorder are not three algorithms, they are that one walk with the
> "record this node" line in three different places. Level order is the exception,
> because it has to cross from one subtree to another and the walk never crosses.
>
> **Load-bearing:** the recursion copies the shape of the tree, so the deepest the call
> stack ever gets is the height of the tree. That is where every `Θ(h)` below comes
> from - about `log n` frames when the tree is bushy, but `n` frames when it is a single
> long chain. Shape, not node count, is what costs you, and a skewed tree makes every
> operation worse at the same time.

</details>

## [binary-search-tree](notebooks/trees/binary-search-tree.md)

<details>
<summary><strong>Binary search tree</strong></summary>

> **Mental model.** Every key has exactly one legal place in the tree, and a single
> comparison tells you which way that place lies. So every function below is the same
> descent: compare with the node you are standing on, commit to one side, and throw the
> other side away forever. Search, insert, delete, floor and ceil differ only in what
> they do when the descent ends.
>
> **Load-bearing:** the ordering rule covers whole subtrees, not just a node's two
> children - that is what the word *invariant* is doing here. Weaken it to "the left
> child is smaller" and discarding a side stops being safe, because the key you want
> could be sitting anywhere in the half you just dropped. The invariant also sets the
> price: the work is one root-to-leaf path, so a skewed tree costs O(n) and every
> operation degrades together.

</details>

## [avl-tree](notebooks/trees/avl-tree.md)

<details>
<summary><strong>AVL Tree (Self-Balancing BST)</strong></summary>

> **Mental model.** A BST's `O(h)` is only useful while `h` stays small, and nothing in a plain
> BST enforces that. AVL adds exactly one rule - no node's two sides may differ in height by
> more than 1 - and rotations are how that rule is restored after an insert or delete.
> Everything else behaves like an ordinary BST, because a rotation never changes the ordering.
>
> **Load-bearing:** heights are *cached* on the node, so any change of shape must recompute
> them from the bottom up. Skip that and every balance factor above the change is reading a
> stale number. And fixing the *lowest* unbalanced node is enough: that rotation gives the
> subtree back the height it had before, so nothing further up ever sees a difference.

</details>

## [heap](notebooks/trees/heap.md)

<details>
<summary><strong>Binary Heap</strong></summary>

> **Mental model.** Half sorted, deliberately. The root is the minimum, everything
> else is a mess, and that trade is what makes insert and extract cheap. Every
> operation is then the same two steps: put the value in the one slot the **shape**
> allows, which is always the end of the array, then let it walk until the **order**
> allows it as well - up towards the root, or down towards the leaves.
>
> **Load-bearing:** completeness. Index arithmetic is the only thing linking a node to
> its parent and children, and it is only correct while the tree has no gaps. Break
> that and there are no pointers to fall back on. It is also why nothing is ever
> pulled out of the middle: extract min overwrites the root with the last element and
> pops the end, and delete first sifts its victim up to the root, because the end is
> the only slot that can be given up without tearing a hole in the shape.

</details>

## [trie](notebooks/trees/trie.md)

<details>
<summary><strong>Trie (Prefix Tree)</strong></summary>

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

</details>

## [graph-basics](notebooks/graphs/graph-basics.md)

<details>
<summary><strong>Graph Basics</strong></summary>

> **Mental model.** A graph is a record of what is next to what. The vertices and edges are
> handed to you; the only real decision you make is how to store that record. An adjacency
> list answers "who are u's neighbours?" cheaply, because it hands you the list already
> built. An adjacency matrix answers "is there an edge from u to v?" cheaply, because that
> is one lookup. Every graph algorithm sits on top of one of those two answers.
>
> **Load-bearing:** the question your algorithm asks most often is what picks the
> representation. Traversals walk neighbours, so they want the list - that is why
> [Graph Traversal](notebooks/graphs/graph-traversal.md) and everything built on it use one. And the matrix
> costs V² cells whether the graph is dense or nearly empty, so a graph with a million
> vertices and three edges still pays for a million-by-million grid.

</details>

## [graph-traversal](notebooks/graphs/graph-traversal.md)

<details>
<summary><strong>Breadth-First Search (BFS)</strong></summary>

> **Mental model.** The queue holds vertices you have found but not yet looked at, and
> because it is first in, first out, it stays sorted by distance from the source.
> Everything one edge away leaves the queue before anything two edges away. The order
> vertices come out *is* order of increasing distance, and that is the whole reason BFS
> gives shortest paths when every edge costs the same.
>
> **Load-bearing:** a vertex is marked visited when it is **enqueued**, not
> when it is dequeued. `visited` does not mean "already looked at", it means "already
> claimed". The diagram below shows what a late mark costs.

</details>

<details>
<summary><strong>Depth-First Search (DFS)</strong></summary>

> **Mental model.** The same loop as BFS with one substitution: the frontier is a stack,
> so the vertex that comes out next is the one found most recently. That single change
> makes the walk dive. It always carries on from where it just was, and backs up only
> when there is nowhere new to go. Recursion hides the stack rather than removing it -
> the call stack *is* the frontier, and `dfs_rec` never mentions a stack because Python
> is keeping it.
>
> **Load-bearing:** DFS says nothing about distance. The first route it finds to
> a vertex can be the longest one in the graph, because it commits to a branch before
> looking at the alternatives. Only BFS earns the shortest-path guarantee.

</details>

## [cycle-detection](notebooks/graphs/cycle-detection.md)

<details>
<summary><strong>Cycle Detection</strong></summary>

> **Mental model.** Undirected and directed graphs need different algorithms here, and that
> difference is the notebook. In an undirected graph, bumping into a visited neighbour is
> normal, because it is usually just the edge you walked in on - so you ignore the vertex
> you came from, and any *other* visited neighbour proves there is a second way in. In a
> directed graph, bumping into a visited vertex is also normal: the diamond
> `0→1, 0→2, 1→3, 2→3` reaches 3 twice and has no cycle. So "visited" is too blunt a
> question to ask. The three colours ask a sharper one - is this vertex still on the path
> I am standing on right now?
>
> **Load-bearing:** colour 1 means "on the recursion stack at this very moment", not
> "seen before". That is the only state that proves a cycle. Leave a vertex at colour 1
> after it finishes and every diamond looks like a cycle; drop the parent check in the
> undirected version and every single edge does.

</details>

## [topological-sort](notebooks/graphs/topological-sort.md)

<details>
<summary><strong>Topological Sort</strong></summary>

> **Mental model.** An ordering exists only because the graph has no cycles, so "sort this
> DAG" and "does this graph have a cycle?" are one question asked twice. Kahn's algorithm
> makes that literal. It emits a vertex the moment nothing points at it any more, and
> vertices trapped in a cycle keep each other pointed at forever, so fewer than V vertices
> come out. The short answer *is* the cycle report.
>
> **Load-bearing:** the DFS version works because a vertex is appended only once
> everything reachable below it has finished. That builds the order backwards, so
> reversing the finish order is what makes every edge point forwards. Append on entry
> instead of on exit and the guarantee is gone.

</details>

## [dijkstra](notebooks/graphs/dijkstra.md)

<details>
<summary><strong>Dijkstra's Algorithm</strong></summary>

> **Mental model.** [BFS](notebooks/graphs/graph-traversal.md) is the same loop with a different frontier.
> BFS comes out in ring order, everything one edge away before anything two edges away,
> which is only shortest when every edge costs the same. Swap the queue for a **min-heap
> keyed on distance** and the vertex that comes out next is the cheapest one found so far
> rather than the earliest one found. Nothing else in the loop changes, and now weights
> work.
>
> **Load-bearing:** a popped vertex is **final** only because weights cannot be negative.
> Any other route into it would have to run through a vertex that is already further away,
> and a longer prefix can never turn out shorter when every edge adds something. Allow one
> negative edge and that argument collapses, the first pop can be wrong, and you need
> Bellman-Ford instead.

</details>

## [union-find](notebooks/graphs/union-find.md)

<details>
<summary><strong>Union-Find (Disjoint Set Union)</strong></summary>

> **Mental model.** Each set is represented by one of its own members - the root of a tree
> of parent pointers. Nothing anywhere stores which set an element belongs to. You find out
> by walking up the parent pointers until you reach a node that is its own parent, so "are x
> and y in the same set?" becomes "do they climb to the same root?".
>
> **Load-bearing:** which member ends up being the root is arbitrary and carries no meaning.
> The only question ever asked of a root is whether it equals another root. That is exactly
> why both optimizations are free to rearrange the tree however they like - re-pointing a
> node at the root, or hanging one root under another, changes the shape and changes nothing
> about the answers.

> **Procedural style:** The data structure is just two arrays (`parent` and `rank`). Functions operate on them directly - no wrapper class needed.

</details>

## [two-pointers-sliding-window](notebooks/techniques/two-pointers-sliding-window.md)

<details>
<summary><strong>Two Pointers & Sliding Window</strong></summary>

> **Mental model.** Both patterns are the same trick: never move a pointer backwards. Two
> indices sweep the array, each one only ever going forward, so the total work is linear even
> though the two ends move independently of each other. That is what replaces the nested loop.
> A step does not just test one candidate, it retires a whole family of candidates for good.
>
> **Load-bearing:** the condition you test has to move in one direction only. Growing the
> window can push it one way but never back, so once you shrink you never have to reconsider.
> The word for that is *monotonic*. Positive values make a sum monotonic in the window size;
> allow one negative value and shrinking could raise the sum, and the argument collapses.

</details>

## [monotonic-stack](notebooks/stacks-and-queues/monotonic-stack.md)

<details>
<summary><strong>Monotonic Stack</strong></summary>

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

</details>

## [dp-intro](notebooks/dynamic-programming/dp-intro.md)

<details>
<summary><strong>Dynamic Programming</strong></summary>

> **Mental model.** Write the honest recursion first. Its call tree asks the same small
> question over and over, so the tree is huge while the number of *different* questions in it
> is tiny. Everything called "DP" is only bookkeeping that makes sure each different question
> is answered once. The cache or the table is not the idea - it is the receipt.
>
> **Load-bearing:** both properties, together. If the subproblems never repeat there is
> nothing to save, and caching only adds cost. If a bigger answer is not built out of smaller
> answers, the table holds numbers that cannot be combined into the answer you want.

</details>

<details>
<summary><strong>Coin Change (Minimum Coins)</strong></summary>

> **Mental model.** One row of a single table, where `dp[i]` answers "cheapest way to make
> exactly i". To make i, you must hand over *some* coin last. Try each coin as the last one
> and ask the table what the leftover costs - so every answer is one lookup plus one.
>
> **Load-bearing:** trying every coin. Take only the biggest coin that fits and you get a
> wrong answer, because picking a coin changes which totals are still reachable. `inf` is also
> load-bearing: it is how an unreachable amount refuses to be built on.

</details>

<details>
<summary><strong>Longest Common Subsequence (LCS)</strong></summary>

> **Mental model.** Only ever look at the *last* character of each prefix. If the two match,
> that character can be kept and both strings shrink by one. If they differ, at least one of
> those two characters is useless, so throw away one, then the other, and keep whichever went
> better. Nothing else about the strings matters at that cell.
>
> **Load-bearing:** the extra row and column of zeros. They say "an empty string shares
> nothing with anything", which is the only place the recursion can stop.

</details>

<details>
<summary><strong>0/1 Knapsack</strong></summary>

> **Mental model.** Walk the items one at a time and ask a single yes/no question about each:
> take it or skip it. Skipping keeps the best answer the earlier items already had. Taking it
> adds its value to the best answer the earlier items had for the capacity that is left over.
> A row of the table means "best value reachable using only the items I have seen so far".
>
> **Load-bearing:** both lookups read row `i-1`, the row *before* this item existed. That is
> the entire reason an item cannot be used twice. Read `dp[i][...]` instead and you have
> silently solved a different problem, the unbounded knapsack, where items may repeat.

</details>
