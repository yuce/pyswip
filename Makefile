.PHONY: build clean cover test upload

build:
	python setup.py sdist
	python setup.py bdist_wheel --universal

clean:
	rm -rf dist build pyswip.egg-info

cover:
	py.test tests --verbose --cov=pyswip

test:
	py.test tests --verbose

upload:
	twine upload dist/*

check:
	black --check .