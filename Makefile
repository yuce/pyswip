.PHONY: build clean coverage upload-coverage test upload

build:
	build

clean:
	rm -rf dist build pyswip.egg-info

coverage:
	PYTHONPATH=src py.test tests --verbose --cov=pyswip

upload-coverage: coverage
	coveralls

test:
	PYTHONPATH=src py.test tests --verbose -m "not slow"

upload:
	twine upload dist/*

check:
	ruff format --check
	ruff check

reformat:
	ruff format
