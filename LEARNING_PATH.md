# Learning Path

A guided checklist through the notebooks in recommended order. Each phase builds on the previous one.

Coming back after a long gap? Start with [RECALL.md](RECALL.md) instead - the same topics in the
same order, as questions rather than lessons.

## Phase 1: Foundations

Understand how to measure algorithm performance before diving into data structures.

- [ ] [Complexity Quick Reference](notebooks/analysis/00-quick-reference.md) - field guide: case vs notation, code pattern → complexity, recursion trees, space, amortization
- [ ] [Analysis of Algorithms - Notation](notebooks/analysis/01-notation.md) - Big O, Ω, Θ
- [ ] [Common Loop Analysis](notebooks/analysis/02-common-loops.md) - linear, log, loglog patterns
- [ ] [Recursion Analysis](notebooks/analysis/03-recursion.md) - recurrences, recursion tree method
- [ ] [Space Complexity](notebooks/analysis/04-space-complexity.md) - auxiliary space, call stack
- [ ] [Amortized Analysis](notebooks/analysis/05-amortized-analysis.md) - aggregate method, accounting method, dynamic array
- [ ] [Stacks and Queues](notebooks/stacks-and-queues/stacks-and-queues.md) - stack, circular queue, balanced parentheses, `deque`

## Phase 2: Linear Data Structures

Core linked structures and their operations.

- [ ] [Singly Linked List](notebooks/linked-lists/singly-linked-list.md) - insert, delete, search, reverse
- [ ] [Doubly Linked List](notebooks/linked-lists/doubly-linked-list.md) - insert, delete, reverse, `deque`
- [ ] [Circular Linked List](notebooks/linked-lists/circular-linked-list.md) - O(1) insert tricks

## Phase 3: Searching & Sorting

Fundamental algorithms you'll use everywhere.

- [ ] [Binary Search](notebooks/searching/binary-search.md) - iterative, recursive, lower/upper bound, rotated array, `bisect`
- [ ] [Basic Sorts](notebooks/sorting/basic-sorts.md) - bubble, selection, insertion, `sorted()`/Timsort
- [ ] [Merge Sort](notebooks/sorting/merge-sort.md) - divide and conquer, stable O(n log n)
- [ ] [Quick Sort](notebooks/sorting/quick-sort.md) - Lomuto, Hoare partitions
- [ ] [Counting & Radix Sort](notebooks/sorting/counting-radix-sort.md) - non-comparison sorts, O(n) possible

## Phase 4: Hashing

- [ ] [Hash Tables](notebooks/hashing/hash-tables.md) - chaining, open addressing, `dict`/`Counter`/`defaultdict`

## Phase 5: Trees & Heaps

Hierarchical data structures.

- [ ] [Binary Tree](notebooks/trees/binary-tree.md) - traversals (in/pre/post/level order), size, height
- [ ] [Binary Search Tree](notebooks/trees/binary-search-tree.md) - search, insert, delete, floor, ceil, `bisect`
- [ ] [AVL Tree](notebooks/trees/avl-tree.md) - self-balancing BST, rotations (LL/LR/RR/RL), balanced insert/delete
- [ ] [Binary Heap](notebooks/trees/heap.md) - min heap, heap sort, build heap O(n) proof, `heapq`
- [ ] [Trie (Prefix Tree)](notebooks/trees/trie.md) - insert, search, prefix search, autocomplete, delete

## Phase 6: Graphs

- [ ] [Graph Basics](notebooks/graphs/graph-basics.md) - terminology, adjacency list vs matrix, `defaultdict`
- [ ] [Graph Traversal](notebooks/graphs/graph-traversal.md) - BFS, DFS (recursive and iterative), disconnected graphs, connected components
- [ ] [Cycle Detection](notebooks/graphs/cycle-detection.md) - undirected (parent tracking), directed (3-color)
- [ ] [Topological Sort](notebooks/graphs/topological-sort.md) - DFS-based, Kahn's algorithm
- [ ] [Dijkstra's Algorithm](notebooks/graphs/dijkstra.md) - shortest path with min-heap, path reconstruction
- [ ] [Union-Find](notebooks/graphs/union-find.md) - disjoint sets, cycle detection, connected components

## Phase 7: Techniques & Patterns

Algorithmic techniques that appear across many problems.

- [ ] [Two Pointers & Sliding Window](notebooks/techniques/two-pointers-sliding-window.md) - pair sum, remove duplicates, max subarray, longest unique substring
- [ ] [Monotonic Stack](notebooks/stacks-and-queues/monotonic-stack.md) - next greater/smaller element, daily temperatures, largest rectangle
- [ ] [Dynamic Programming](notebooks/dynamic-programming/dp-intro.md) - fibonacci, coin change, LCS, knapsack, `lru_cache`
