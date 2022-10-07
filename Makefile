
export SRC_PATH=./fastgraphql
export TEST_PATH=./tests

test:
	@export FAST_GRAPHQL_DEBUG=true
	@poetry run pytest --cov=fastgraphql --cov=tests --cov-report=term-missing:skip-covered --cov-report=xml:build/coverage.xml --junitxml=build/junit.xml

lint:
	@poetry run black --check $(SRC_PATH) $(TEST_PATH)

static-analysis:
	@poetry run pyflakes $(SRC_PATH) $(TEST_PATH)

type-check:
	@poetry run mypy $(SRC_PATH) $(TEST_PATH)

clean-imports:
	@autoflake --recursive --in-place --remove-all-unused-imports $(SRC_PATH) $(TEST_PATH) && black .

all: lint static-analysis type-check test
