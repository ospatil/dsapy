# make sure you have pyenv installed and have run: pyenv install 3.12.4
start:
	uv run jupyter lab --config ./config/jupyter_notebook_config.py

.PHONY: start
