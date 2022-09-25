
export SRC_PATH=./fastql
export TEST_PATH=./tests

test:
	@poetry run pytest --cov=fastql --cov=tests --cov-report=term-missing:skip-covered --cov-report=xml:build/coverage.xml

lint:
	@poetry run black --check $(SRC_PATH) $(TEST_PATH)

static-analysis:
	@poetry run pyflakes $(SRC_PATH) $(TEST_PATH)

type-check:
	@poetry run mypy $(SRC_PATH) $(TEST_PATH)
