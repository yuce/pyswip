.PHONY: build clean coverage upload-coverage test upload

build:
	hatch build

clean:coveralls
	rm -rf dist build pyswip.egg-info

coverage:
	hatch run test:coverage

upload-coverage:
	hatch run upload-coverage:run-coveralls

test:
	hatch run test:all

upload:
	twine upload dist/*

check:
	ruff format --check
	ruff check
