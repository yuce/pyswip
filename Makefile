.PHONY: cover test

cover:
	py.test --cov=pyswip tests

test:
	py.test tests --verbose
