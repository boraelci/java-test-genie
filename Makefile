PYTHON = python3

#########
# BUILD #
#########
develop:  ## install dependencies and build library
	$(PYTHON) -m pip install -e .[develop]

build:  ## build the library
	$(PYTHON) setup.py build build_ext --inplace

install:  ## install library
	$(PYTHON) -m pip install .

#########
# LINTS #
#########
lint:  ## run static analysis with flake8
	$(PYTHON) -m black --check epispread setup.py
	$(PYTHON) -m flake8 epispread setup.py

# Alias
lints: lint

format:  ## run autoformatting with black
	$(PYTHON) -m black epispread/ setup.py

# alias
fix: format

check:  ## check assets for packaging
	check-manifest -v

# Alias
checks: check

annotate:  ## run type checking
	$(PYTHON) -m mypy ./genie

#########
# TESTS #
#########
test: ## clean and run unit tests
	$(PYTHON) -m pytest -v genie/tests

coverage:  ## clean and run unit tests with coverage
	$(PYTHON) -m pytest -v genie/tests --cov=genie --cov-branch --cov-fail-under=75 --cov-report term-missing

# Alias
tests: test

###########
# VERSION #
###########
show-version:
	bump2version --dry-run --allow-dirty setup.py --list | grep current | awk -F= '{print $2}'

patch:
	bump2version patch

minor:
	bump2version minor

major:
	bump2version major

########
# DIST #
########
dist-build:  # Build dist
	$(PYTHON) setup.py sdist bdist_wheel

dist-check:
	$(PYTHON) -m twine check dist/*

dist: clean build dist-build dist-check  ## Build dists

publish:  # Upload assets
	echo "would usually run $(PYTHON) -m twine upload dist/* --skip-existing"

#########
# CLEAN #
#########
deep-clean: ## clean everything from the repository
	git clean -fdx

clean: ## clean the repository
	rm -rf .coverage coverage cover htmlcov logs build dist *.egg-info .pytest_cache

############################################################################################

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'

.PHONY: develop build install lint lints format fix check checks annotate test coverage show-coverage tests show-version patch minor major dist-build dist-check dist publish deep-clean clean help

#########
# PAGES #
#########

TMPREPO=/tmp/docs/genie
pages: 
	rm -rf $(TMPREPO)
	git clone -b gh-pages https://github.com/boraelci/java-test-genie.git $(TMPREPO)
	rm -rf $(TMPREPO)/*
	cp -r docs/_build/html/* $(TMPREPO)
	cd $(TMPREPO);\
	git add -A ;\
	git commit -a -m 'auto-updating docs' ;\
	git push