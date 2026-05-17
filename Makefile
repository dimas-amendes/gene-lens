# Gene Lens — common developer tasks. Run `make` for the menu.
#
# This Makefile mirrors what's in CONTRIBUTING.md and the README, so a new
# contributor can clone the repo and discover the workflow without reading
# anything.

VENV ?= .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PORT ?= 5000

.PHONY: help
help:  ## Show this menu
	@awk 'BEGIN {FS = ":.*##"; printf "Targets:\n"} \
	/^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: venv
venv:  ## Create the .venv virtual environment
	@test -d $(VENV) || python3 -m venv $(VENV)
	@echo "Activate with: source $(VENV)/bin/activate"

.PHONY: install
install: venv  ## Install runtime dependencies into .venv
	$(PIP) install -r requirements.txt

.PHONY: install-dev
install-dev: install  ## Install dev extras (pytest, flake8)
	$(PIP) install pytest flake8

.PHONY: databases
databases:  ## One-time download of ClinVar (PharmGKB requires manual step)
	$(PY) download_databases.py

.PHONY: run
run:  ## Start the dashboard at http://127.0.0.1:$(PORT)
	$(PY) run.py

.PHONY: dev
dev:  ## Start the dashboard with auto-reload on .py and template changes
	$(PY) run.py --debug

.PHONY: test
test:  ## Run the pytest suite
	$(PY) -m pytest tests/ -v

.PHONY: test-fast
test-fast:  ## Run pytest with -q
	$(PY) -m pytest tests/ -q

.PHONY: lint
lint:  ## Flake8 — block on syntax errors, warn on style
	$(PY) -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=static,genetics-docs,.venv

.PHONY: privacy-check
privacy-check:  ## Verify NetworkBlocker and related guards
	$(PY) main.py privacy-check

.PHONY: clean
clean:  ## Remove caches and build artifacts (leaves .venv alone)
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	rm -rf build dist *.egg-info

.PHONY: docker-build
docker-build:  ## Build the Gene Lens Docker image
	docker build -t gene-lens .

.PHONY: docker-run
docker-run:  ## Run the dashboard in Docker (uses local volumes for data)
	docker compose up
