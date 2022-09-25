
export SRC_PATH=./fastql
export TEST_PATH=./tests

test:
	@pytest --cov=fastql --cov=tests --cov-report=term-missing:skip-covered --cov-report=xml:build/coverage.xml

lint:
	@black --check $(SRC_PATH) $(TEST_PATH)

type-check:
	@mypy $(SRC_PATH) $(TEST_PATH)
