#!/usr/bin/env bash
# Exports the .drawio sources in docs/diagrams/ to PNGs under notebooks/*/images/.
# Requires the draw.io desktop app (override its path with DRAWIO=...).
#
# Single-page sources export to <name>.png. Multi-page sources export one PNG
# per page, named <name>-<page name>.png -- e.g. page "recursion1" of
# recursion.drawio becomes recursion-recursion1.png.
#
# docs/diagrams/legacy/ holds the older .excalidraw sources. They predate this
# script and are exported by hand from excalidraw.com.

set -euo pipefail

DRAWIO="${DRAWIO:-/Applications/draw.io.app/Contents/MacOS/draw.io}"
DIAGRAMS_DIR="docs/diagrams"
SCALE=2

if ! command -v "$DRAWIO" >/dev/null 2>&1; then
  echo "Error: draw.io not found at $DRAWIO"
  exit 1
fi

declare -A OUTPUT_MAP
OUTPUT_MAP=(
  ["sll-insert-delete"]="notebooks/linked-lists/images"
  ["circular-linked-list"]="notebooks/linked-lists/images"
  ["bst-delete"]="notebooks/trees/images"
  ["heap-array-tree"]="notebooks/trees/images"
  ["trie"]="notebooks/trees/images"
  ["hash-chaining-vs-open"]="notebooks/hashing/images"
  ["bfs-vs-dfs"]="notebooks/graphs/images"
  ["union-find-path-compression"]="notebooks/graphs/images"
  ["stack-vs-queue"]="notebooks/stacks-and-queues/images"
  ["binary-search-narrowing"]="notebooks/searching/images"
  ["merge-sort-divide-merge"]="notebooks/sorting/images"
  ["counting-sort-steps"]="notebooks/sorting/images"
  ["sliding-window"]="notebooks/techniques/images"
  ["recursion"]="notebooks/analysis/images"
  ["space-complexity"]="notebooks/analysis/images"
)

export_page() {
  local src="$1" dest="$2" page_index="${3:-}"
  local args=(--export --format png --scale "$SCALE" --border 10)
  if [ -n "$page_index" ]; then
    args+=(--page-index "$page_index")
  fi
  "$DRAWIO" "${args[@]}" --output "$dest" "$src"
}

for name in "${!OUTPUT_MAP[@]}"; do
  src="$DIAGRAMS_DIR/$name.drawio"
  dest_dir="${OUTPUT_MAP[$name]}"

  if [ ! -f "$src" ]; then
    echo "SKIP  $src (not found)"
    continue
  fi

  mkdir -p "$dest_dir"

  # page names in document order
  pages=()
  while IFS= read -r page; do
    pages+=("$page")
  done < <(grep -o '<diagram[^>]*name="[^"]*"' "$src" | sed 's/.*name="//;s/"$//')

  if [ "${#pages[@]}" -le 1 ]; then
    dest="$dest_dir/$name.png"
    echo "BUILD $src -> $dest"
    export_page "$src" "$dest"
  else
    for i in "${!pages[@]}"; do
      dest="$dest_dir/$name-${pages[$i]}.png"
      echo "BUILD $src [page ${pages[$i]}] -> $dest"
      export_page "$src" "$dest" "$i"
    done
  fi
done

echo "Done."
