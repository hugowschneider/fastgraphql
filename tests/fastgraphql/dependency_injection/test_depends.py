from typing import Any, Generator
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient


from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

GRAPHQL_URL = "/graphql"

fast_graphql = FastGraphQL()


class DummyScopeObject:
    def __init__(self) -> None:
        self.open = True

    def close(self) -> None:
        self.open = False


obj = DummyScopeObject()


def function() -> DummyScopeObject:
    return DummyScopeObject()


def generator_function() -> Generator[DummyScopeObject, None, None]:
    global obj
    try:
        yield obj
    finally:
        obj.close()


@fast_graphql.query()
def query_function(
    depends: DummyScopeObject = fast_graphql.depends_on(function),
) -> str:
    setattr(query_function, "__called__", True)
    setattr(
        query_function,
        "__parameters__",
        {
            "depends": depends,
        },
    )
    return "result"


@fast_graphql.query()
def query_generator(
    depends: DummyScopeObject = fast_graphql.depends_on(generator_function),
) -> str:
    setattr(query_generator, "__called__", True)
    setattr(
        query_generator,
        "__parameters__",
        {
            "depends": depends,
        },
    )
    return "result"


def nested_depends_function_child() -> str:
    setattr(nested_depends_function_child, "__called__", True)
    return "abc"


def nested_depends_function(
    depends: str = fast_graphql.depends_on(nested_depends_function_child),
) -> int:
    setattr(nested_depends_function, "__called__", True)
    return len(depends)


@fast_graphql.query()
def query_nested_injection(
    depends: DummyScopeObject = fast_graphql.depends_on(nested_depends_function),
) -> str:
    setattr(query_nested_injection, "__called__", True)
    setattr(
        query_nested_injection,
        "__parameters__",
        {
            "depends": depends,
        },
    )
    return "result"


@pytest.fixture(scope="class", autouse=True)
def fastapi_test(request: Any) -> None:

    request.cls.app = FastAPI()
    request.cls.app.include_router(
        make_ariadne_fastapi_router(fast_graphql=fast_graphql)
    )
    request.cls.test_client = TestClient(request.cls.app)


@pytest.mark.usefixtures("fastapi_test")
class TestDependencyInjection:
    app: FastAPI
    test_client: TestClient

    def test_query_depends_on_func(self) -> None:
        query = """
query {
    query_function
}
        """.strip()

        response = self.test_client.post(
            GRAPHQL_URL,
            json={"query": query},
        )

        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "query_function" in response.json()["data"]
        assert hasattr(query_function, "__called__") and getattr(
            query_function, "__called__"
        )
        parameters = getattr(query_function, "__parameters__")
        assert parameters
        assert isinstance(parameters["depends"], DummyScopeObject)

    def test_query_depends_on_nested_func(self) -> None:
        query = """
query {
    query_nested_injection
}
        """.strip()

        response = self.test_client.post(
            GRAPHQL_URL,
            json={"query": query},
        )
        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "query_nested_injection" in response.json()["data"]
        assert hasattr(query_nested_injection, "__called__") and getattr(
            query_nested_injection, "__called__"
        )
        assert hasattr(nested_depends_function, "__called__") and getattr(
            nested_depends_function, "__called__"
        )
        assert hasattr(nested_depends_function_child, "__called__") and getattr(
            nested_depends_function_child, "__called__"
        )
        parameters = getattr(query_nested_injection, "__parameters__")
        assert parameters
        assert parameters["depends"] == 3

    def test_query_depends_on_generator(self) -> None:
        query = """
query {
    query_generator
}
        """.strip()

        response = self.test_client.post(
            GRAPHQL_URL,
            json={"query": query},
        )
        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "query_generator" in response.json()["data"]
        assert hasattr(query_generator, "__called__") and getattr(
            query_generator, "__called__"
        )
        parameters = getattr(query_generator, "__parameters__")
        assert parameters
        assert isinstance(parameters["depends"], DummyScopeObject)
        assert not obj.open
