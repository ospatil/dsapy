#!/usr/bin/env bash
# Converts all .drawio files in docs/diagrams/ to PNGs in the appropriate notebooks/*/images/ folders.
# Requires draw.io desktop app installed.

set -euo pipefail

DRAWIO="/Applications/draw.io.app/Contents/MacOS/draw.io"
DIAGRAMS_DIR="docs/diagrams"
SCALE=2

if [ ! -x "$DRAWIO" ]; then
  echo "Error: draw.io not found at $DRAWIO"
  exit 1
fi

declare -A OUTPUT_MAP
OUTPUT_MAP=(
  ["sll-insert-delete"]="notebooks/linked-lists/images"
  ["circular-linked-list"]="notebooks/linked-lists/images"
  ["bst-delete"]="notebooks/trees/images"
  ["heap-array-tree"]="notebooks/misc/images"
  ["hash-chaining-vs-open"]="notebooks/hashing/images"
  ["bfs-vs-dfs"]="notebooks/graphs/images"
  ["stack-vs-queue"]="notebooks/stacks-and-queues/images"
  ["binary-search-narrowing"]="notebooks/searching/images"
  ["merge-sort-divide-merge"]="notebooks/sorting/images"
  ["counting-sort-steps"]="notebooks/sorting/images"
  ["sliding-window"]="notebooks/techniques/images"
  ["trie"]="notebooks/trees/images"
  ["union-find-path-compression"]="notebooks/graphs/images"
)

for name in "${!OUTPUT_MAP[@]}"; do
  src="$DIAGRAMS_DIR/$name.drawio"
  dest_dir="${OUTPUT_MAP[$name]}"
  dest="$dest_dir/$name.png"

  if [ ! -f "$src" ]; then
    echo "SKIP  $src (not found)"
    continue
  fi

  mkdir -p "$dest_dir"
  echo "BUILD $src -> $dest"
  "$DRAWIO" --export --format png --scale "$SCALE" --border 10 --output "$dest" "$src"
done

echo "Done."
