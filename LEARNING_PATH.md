# Learning Path

A guided checklist through the notebooks in recommended order. Each phase builds on the previous one.

## Phase 1: Foundations

Understand how to measure algorithm performance before diving into data structures.

- [ ] [Analysis of Algorithms -- Notation](notebooks/analysis/01-notation.ipynb) -- Big O, Ω, Θ
- [ ] [Common Loop Analysis](notebooks/analysis/02-common-loops.ipynb) -- linear, log, loglog patterns
- [ ] [Recursion Analysis](notebooks/analysis/03-recursion.ipynb) -- recurrences, recursion tree method
- [ ] [Space Complexity](notebooks/analysis/04-space-complexity.ipynb) -- auxiliary space, call stack
- [ ] [Stacks and Queues](notebooks/stacks-and-queues/stacks-and-queues.ipynb) -- stack, circular queue, balanced parentheses, `deque`

## Phase 2: Linear Data Structures

Core linked structures and their operations.

- [ ] [Singly Linked List](notebooks/linked-lists/singly-linked-list.ipynb) -- insert, delete, search, reverse
- [ ] [Doubly Linked List](notebooks/linked-lists/doubly-linked-list.ipynb) -- insert, delete, reverse, `deque`
- [ ] [Circular Linked List](notebooks/linked-lists/circular-linked-list.ipynb) -- O(1) insert tricks

## Phase 3: Searching & Sorting

Fundamental algorithms you'll use everywhere.

- [ ] [Binary Search](notebooks/searching/binary-search.ipynb) -- iterative, recursive, lower/upper bound, rotated array, `bisect`
- [ ] [Basic Sorts](notebooks/sorting/basic-sorts.ipynb) -- bubble, selection, insertion, `sorted()`/Timsort
- [ ] [Merge Sort](notebooks/sorting/merge-sort.ipynb) -- divide and conquer, stable O(n log n)
- [ ] [Quick Sort](notebooks/sorting/quick-sort.ipynb) -- Lomuto, Hoare partitions
- [ ] [Counting & Radix Sort](notebooks/sorting/counting-radix-sort.ipynb) -- non-comparison sorts, O(n) possible

## Phase 4: Hashing

- [ ] [Hash Tables](notebooks/hashing/hash-tables.ipynb) -- chaining, open addressing, `dict`/`Counter`/`defaultdict`

## Phase 5: Trees & Heaps

Hierarchical data structures.

- [ ] [Binary Tree](notebooks/trees/binary-tree.ipynb) -- traversals (in/pre/post/level order), size, height
- [ ] [Binary Search Tree](notebooks/trees/binary-search-tree.ipynb) -- search, insert, delete, floor, ceil, `bisect`
- [ ] [Binary Heap](notebooks/misc/heap.ipynb) -- min heap, heap sort, build heap O(n) proof, `heapq`
- [ ] [Trie (Prefix Tree)](notebooks/trees/trie.ipynb) -- insert, search, prefix search, autocomplete, delete

## Phase 6: Graphs

- [ ] [Graph Basics](notebooks/graphs/graph-basics.ipynb) -- representations, BFS, DFS, connected components
- [ ] [Cycle Detection](notebooks/graphs/graph-basics.ipynb) -- undirected (parent tracking), directed (3-color)
- [ ] [Topological Sort](notebooks/graphs/graph-basics.ipynb) -- DFS-based, Kahn's algorithm
- [ ] [Dijkstra's Algorithm](notebooks/graphs/graph-basics.ipynb) -- shortest path with min-heap
- [ ] [Union-Find](notebooks/graphs/union-find.ipynb) -- disjoint sets, cycle detection, connected components

## Phase 7: Techniques & Patterns

Algorithmic techniques that appear across many problems.

- [ ] [Two Pointers & Sliding Window](notebooks/techniques/two-pointers-sliding-window.ipynb) -- pair sum, remove duplicates, max subarray, longest unique substring
- [ ] [Monotonic Stack](notebooks/stacks-and-queues/monotonic-stack.ipynb) -- next greater/smaller element, daily temperatures, largest rectangle
- [ ] [Dynamic Programming](notebooks/dynamic-programming/dp-intro.ipynb) -- fibonacci, coin change, LCS, knapsack, `lru_cache`
