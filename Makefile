# Shortcuts. The real logic lives in Python so it works the same on Windows.
PYTHON ?= python

.PHONY: setup test check

setup:  ## Build the whole local lakehouse (needs: pip install -r requirements.txt)
	$(PYTHON) tools/setup.py

test:  ## Run the test suite
	$(PYTHON) -m pytest

check:  ## Run the repository checks
	$(PYTHON) tools/check_leaks.py
	$(PYTHON) tools/check_skills.py
	$(PYTHON) tools/check_context.py
	$(PYTHON) tools/build_catalog.py --check
	$(PYTHON) tools/check_evals.py
	$(PYTHON) tools/check_connectors.py
	$(PYTHON) tools/check_context_ab.py
