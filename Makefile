.PHONY: setup clean install run test lint help

VENV_DIR = venv
PYTHON = $(VENV_DIR)/Scripts/python
POETRY = $(VENV_DIR)/Scripts/poetry.exe

help:
	@echo "Available commands:"
	@echo "  make setup    - Create virtual environment and install Poetry"
	@echo "  make install  - Install project dependencies"
	@echo "  make clean    - Remove virtual environment and cached files"
	@echo "  make run      - Run the sentiment analysis"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linting checks"

setup:
	python -m venv $(VENV_DIR)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install poetry
	$(POETRY) config virtualenvs.create false --local

install:
	$(POETRY) install

clean:
	rm -rf $(VENV_DIR)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf dist
	rm -rf *.egg-info

run:
	$(PYTHON) src/sentiment/reddit_analyzer.py

test:
	$(POETRY) run pytest

lint:
	$(POETRY) run black .
	$(POETRY) run flake8 .
	$(POETRY) run mypy .

init: setup install
	@echo "Project initialized successfully!"