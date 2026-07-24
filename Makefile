.PHONY: install build paper site validate release test lint check

install:
	python -m pip install -e '.[dev]'

build:
	python -m paperkit.cli build

paper: build
	python -m paperkit.cli build-paper

site: build
	npm run build --prefix site

validate:
	python -m paperkit.cli validate

release:
	python -m paperkit.cli release

test:
	python -m pytest

lint:
	python -m ruff check .

check: lint test validate build
