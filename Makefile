# Python version is managed by mise (see .mise.toml); run `uv sync` first.
start:
	uv run jupyter lab --config ./config/jupyter_notebook_config.py

diagrams:
	bash scripts/build-diagrams.sh

# Execute every notebook end-to-end; inline asserts raise on failure.
test:
	@fail=0; \
	for nb in $$(find notebooks -name '*.ipynb' | sort); do \
		if uv run jupyter execute "$$nb" >/dev/null 2>&1; then \
			echo "PASS  $$nb"; \
		else \
			echo "FAIL  $$nb"; fail=1; \
		fi; \
	done; \
	exit $$fail

.PHONY: start diagrams test
