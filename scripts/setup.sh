#!/usr/bin/env bash
# Run once after cloning or on a new machine.
set -euo pipefail

# Notebooks are stored as Markdown (see jupytext.toml). JupyterLab needs the
# paired .ipynb to exist, so generate one beside every .md. Both stay in sync
# from then on, and the .ipynb is gitignored.
echo "Generating paired .ipynb for each Markdown notebook..."
uv run jupytext --sync $(find notebooks -name '*.md' -not -path '*checkpoint*')

echo "Done. Edit either file; Jupytext syncs the pair on save."
