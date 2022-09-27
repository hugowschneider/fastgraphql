from typing import Any

import pytest


from fastapi import FastAPI
from fastapi.testclient import TestClient

from pydantic import BaseModel

from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

fast_graphql = FastGraphQL()


@fast_graphql.graphql_type()
class Model(BaseModel):
    t_int: int


@fast_graphql.graphql_query()
def simple_query() -> str:
    setattr(simple_query, "__called__", True)
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

        response = self.test_client.get("/graphql")
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
        response = self.test_client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        query = """
query {
    simple_query 
}
""".strip()
        response = self.test_client.post("/graphql", json={"query": query})
        assert response.status_code == 200, response.json()
        assert response.json()["data"]["simple_query"] == "result"
        assert hasattr(simple_query, "__called__") and getattr(
            simple_query, "__called__"
        )
