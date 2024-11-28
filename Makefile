.PHONY: virtual_env_set
virtual_env_set:
ifndef VIRTUAL_ENV
	$(error VIRTUAL_ENV not set)
endif

### DEPENDENCIES ###
.PHONY: install
install: requirements/local.hash virtual_env_set
	pip install -r requirements/local.hash
	pip install -e . --no-deps

.PHONY: sync
sync: requirements/local.hash virtual_env_set
	pip-sync requirements/local.hash
	pip install -e . --no-deps

.PHONY: %-docker
%-docker:  ## Could be lock-docker or upgrade-docker
	docker run --rm -it -v $(PWD):/pcm $$(docker build -q .) /usr/bin/make $*-ubuntu

.PHONY: %-ubuntu
%-ubuntu: .venv39
	.venv39/bin/python3 -m pip install tox
	.venv39/bin/python3 -m tox -e $*

.venv39:
	python3.9 -m venv .venv39

.PHONY: lock
lock: virtual_env_set
	tox -e lock

.PHONY: upgrade
upgrade: virtual_env_set
	tox -e upgrade

### CI ###
.PHONY: test
test:
	tox

.PHONY: clean
clean:
	rm -rf build dist pip-compile-multi.egg-info docs/_build
	rm -rf .venv39
	find . -name "*.pyc" -delete
	find * -type d -name '__pycache__' | xargs rm -rf

.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: release
release: build
	twine upload dist/*

### MISC ###
.PHONY: docs
docs: virtual_env_set
	make -C docs html
