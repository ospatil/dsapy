# make sure you have pyenv installed and have run: pyenv install 3.12
py-setup:
	pyenv local 3.12; \
	python -m venv .venv; \
	python -m pip install --upgrade pip; \
	python -m pip install pip-tools; \
	echo "\n\nActivate the virtual environment with: source .venv/bin/activate\n\n"
.PHONY: py-setup

py-pip-compile:
	rm requirements*.txt || true; \
	pip-compile --resolver=backtracking requirements.in; \
	pip-compile --resolver=backtracking requirements-dev.in;
.PHONY: py-pip-compile

py-pip-sync:
	pip-sync requirements*.txt
.PHONY: py-pip-sync

py-pip-install:
	python -m pip install -r requirements.txt -r requirements-dev.txt
.PHONY: py-pip-install

py-pip-all: py-pip-compile py-pip-sync py-pip-install
.PHONY: py-pip-all
