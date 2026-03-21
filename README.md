# Data Structures and Algorithms in Python

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ospatil/dsapy/HEAD)

## Prerequisites

* **mise** - manages Python version and activates the virtual environment automatically
* **uv** - package manager

## Setup

```bash
uv sync
```

mise will activate the correct Python version and `.venv` automatically when you `cd` into the repo.

## Run

```bash
make start
```

## Upgrading

### Python version

1. Install and pin the new version: `mise use python@<version>` (updates `.mise.toml` automatically)
2. Update `requires-python` in `pyproject.toml` if changing minor version
3. Recreate the venv:

   ```bash
   rm -rf .venv
   uv sync
   ```

### Dependencies

```bash
uv lock --upgrade   # upgrade all packages
uv sync             # install upgraded packages into .venv
```

To upgrade a single package: `uv lock --upgrade-package <package> && uv sync`
