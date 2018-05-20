.PHONY: cover test test-all

cover:
	py.test --cov=pyswip tests integration_tests

test:
	py.test tests --verbose

test-all:
	py.test tests integration_tests --verbose