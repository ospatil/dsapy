#!/usr/bin/env bash
# Run once after cloning or on a new machine.
set -euo pipefail

echo "Installing nbstripout git filter..."
uv run nbstripout --install
git config --local filter.nbstripout.required false

echo "Done. Notebook outputs will be auto-stripped on commit."
