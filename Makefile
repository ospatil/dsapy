# Python version is managed by mise (see .mise.toml); run `uv sync` first.
start:
	uv run jupyter lab --config ./config/jupyter_notebook_config.py

# Regenerate the paired .ipynb beside every .md (needed once after a fresh clone).
sync:
	@uv run jupytext --sync $$(find notebooks -name '*.md' -not -path '*checkpoint*')

# Rebuild RECALL.md from the mental-model cards in the notebooks.
recall:
	@python3 scripts/build-recall.py

diagrams:
	bash scripts/build-diagrams.sh

# Execute every notebook end-to-end from its Markdown source; inline asserts
# raise on failure. The paired .ipynb is a build artifact and is not tested.
test:
	@fail=0; tmp=$$(mktemp -d); \
	for nb in $$(find notebooks -name '*.md' -not -path '*checkpoint*' | sort); do \
		if uv run jupytext --to ipynb --execute "$$nb" -o "$$tmp/out.ipynb" >/dev/null 2>&1; then \
			echo "PASS  $$nb"; \
		else \
			echo "FAIL  $$nb"; fail=1; \
		fi; \
	done; \
	rm -rf "$$tmp"; \
	python3 scripts/build-recall.py --check || fail=1; \
	exit $$fail

.PHONY: start sync recall diagrams test
