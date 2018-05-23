.PHONY: build_posix build_win cover test

build_posix:
	python setup.py sdist
	python setup.py bdist_wheel --universal

build_win:
	python setup.py bdist_msi

cover:
	py.test --cov=pyswip tests

test:
	py.test tests --verbose

