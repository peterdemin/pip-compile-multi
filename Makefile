.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: virtual_env_set
virtual_env_set:
ifndef VIRTUAL_ENV
	$(error VIRTUAL_ENV not set)
endif

### DEPENDENCIES ###
.PHONY: install
install: requirements/local.hash virtual_env_set
	pip install -Ue . -r requirements/local.hash

.PHONY: sync
sync: requirements/local.hash virtual_env_set
	pip-sync requirements/local.hash
	pip install -e . --no-deps

.PHONY: upgrade
upgrade: virtual_env_set
	tox -e upgrade3

### CI ###
.PHONY: test
test:
	tox

### MISC ###
.PHONY: clean
clean:
	rm -rf build dist pip-compile-multi.egg-info docs/_build
	find . -name "*.pyc" -delete
	find * -type d -name '__pycache__' | xargs rm -rf

.PHONY: docs
docs: virtual_env_set
	make -C docs html
