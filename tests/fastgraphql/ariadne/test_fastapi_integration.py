from typing import Any, cast

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from graphql import GraphQLResolveInfo
from pydantic import BaseModel
from starlette.requests import Request

from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

GRAPHQL_URL = "/graphql"

fast_graphql = FastGraphQL()


@fast_graphql.type()
class Model(BaseModel):
    t_int: int


@fast_graphql.query()
def sample_query() -> str:
    setattr(sample_query, "__called__", True)
    return "result"


def request_provider(
    info: GraphQLResolveInfo = fast_graphql.resolver_into(),
    info2: GraphQLResolveInfo = fast_graphql.depends_on_type(GraphQLResolveInfo),
) -> Request:
    assert info2 == info
    return cast(Request, info.context["request"])


@fast_graphql.query()
def request_context_query(
    request: Request = fast_graphql.depends_on(request_provider),
    input_dependency: int = fast_graphql.depends_on_type(int),
    input: int = fast_graphql.parameter(),
) -> str:
    assert input_dependency == input
    setattr(request_context_query, "__called__", True)
    setattr(
        request_context_query,
        "__parameters__",
        {"request": request, "input": input, "input_dependency": input_dependency},
    )
    return "result"


@fast_graphql.mutation()
def sample_mutation() -> str:
    setattr(sample_mutation, "__called__", True)
    return "result"


@fast_graphql.mutation()
def dependency_does_not_exist(
    does_not_exist: str = fast_graphql.depends_on_type(FastGraphQL),
) -> str:
    setattr(dependency_does_not_exist, "__called__", True)
    setattr(
        dependency_does_not_exist, "__parameters__", {"does_not_exist": does_not_exist}
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
class TestAriadneFastAPIIntegration:
    app: FastAPI
    test_client: TestClient

    def test_graphql_api_rendering(self) -> None:

        response = self.test_client.get(GRAPHQL_URL)
        assert response.status_code == 200
        query = """
query IntrospectionQuery {
    __schema {
        types {
            kind
            name
            description
        }
    }
}
        """.strip()
        response = self.test_client.post(GRAPHQL_URL, json={"query": query})
        assert response.status_code == 200

        query = """
query {
    sample_query 
}
""".strip()
        response = self.test_client.post(GRAPHQL_URL, json={"query": query})
        assert response.status_code == 200, response.json()
        assert response.json()["data"]["sample_query"] == "result"
        assert hasattr(sample_query, "__called__") and getattr(
            sample_query, "__called__"
        )

        query = """
mutation {
    sample_mutation 
}
""".strip()
        response = self.test_client.post(GRAPHQL_URL, json={"query": query})
        assert response.status_code == 200, response.json()
        assert response.json()["data"]["sample_mutation"] == "result"
        assert hasattr(sample_mutation, "__called__") and getattr(
            sample_mutation, "__called__"
        )

    def test_injected_request_context(self) -> None:
        query = """
        query {
            request_context_query(input: 1)
        }
        """.strip()
        response = self.test_client.post(
            GRAPHQL_URL,
            json={"query": query},
            headers={"test-header": "test-value"},
        )
        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "request_context_query" in response.json()["data"]

        assert response.json()["data"]["request_context_query"] == "result"
        assert hasattr(request_context_query, "__called__") and getattr(
            request_context_query, "__called__"
        )
        parameters = getattr(request_context_query, "__parameters__")
        assert parameters
        assert isinstance(parameters["request"], Request)

    def test_injected_does_not_exists(self) -> None:

        query = """
        mutation {
            dependency_does_not_exist 
        }
        """.strip()
        response = self.test_client.post(
            GRAPHQL_URL,
            json={"query": query},
        )
        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "dependency_does_not_exist" in response.json()["data"]

        assert response.json()["data"]["dependency_does_not_exist"] == "result"
        assert hasattr(dependency_does_not_exist, "__called__") and getattr(
            dependency_does_not_exist, "__called__"
        )
        parameters = getattr(dependency_does_not_exist, "__parameters__")
        assert parameters
        assert parameters["does_not_exist"] is None
