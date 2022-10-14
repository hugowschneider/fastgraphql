
export SRC_PATH=./fastgraphql
export TEST_PATH=./tests
export ALL_SRC=$(SRC_PATH) $(TEST_PATH)

test:
	@export FAST_GRAPHQL_DEBUG=true
	@poetry run pytest --cov=fastgraphql --cov=tests --cov-report=term-missing:skip-covered --cov-report=xml:build/coverage.xml --junitxml=build/junit.xml

lint:
	@poetry run black --check $(ALL_SRC)

static-analysis:
	@poetry run pyflakes $(ALL_SRC)

check-imports:
	@poetry run isort --check $(ALL_SRC)

type-check:
	@poetry run mypy $(ALL_SRC)

clean-imports:
	@poetry run autoflake --recursive --in-place --remove-all-unused-imports $(ALL_SRC) && poetry run isort $(ALL_SRC) && poetry run black $(ALL_SRC)

all: lint static-analysis type-check check-imports test
