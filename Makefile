.PHONY: build_posix build_win clean cover test

build_posix:
	python setup.py sdist
	python setup.py bdist_wheel --universal

build_win:
	python setup.py bdist_msi

cover:
	py.test --cov=pyswip tests

clean:
	rm -rf dist build pyswip.egg-info

test:
	py.test tests --verbose

upload:
	twine upload dist/*
