import json
from datetime import datetime, date, time, timezone, timedelta
from typing import Any

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

fast_graphql = FastGraphQL()


@fast_graphql.query()
def date_query(
    t_datetime: datetime = fast_graphql.parameter(),
    t_date: date = fast_graphql.parameter(),
    t_time: time = fast_graphql.parameter(),
) -> str:
    setattr(date_query, "__called__", True)
    setattr(
        date_query,
        "__parameters__",
        {"t_datetime": t_datetime, "t_date": t_date, "t_time": t_time},
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
class TestDateTypes:

    test_client: TestClient

    def test_date_type(self) -> None:
        query = """
query StdTypeQuery(
            $t_datetime: DateTime!
            $t_date: Date!
            $t_time: Time!
){
    date_query(
            t_datetime: $t_datetime,
            t_date: $t_date,
            t_time: $t_time
    )
}""".strip()

        date_obj = datetime(
            year=2022,
            month=10,
            day=1,
            hour=8,
            minute=25,
            second=11,
            microsecond=0,
            tzinfo=timezone(timedelta(hours=-2)),
        )
        variables = {
            "t_datetime": date_obj,
            "t_date": date_obj.replace(tzinfo=None).date(),
            "t_time": date_obj.replace(tzinfo=None).time(),
        }
        response = self.test_client.post(
            "/graphql",
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "date_query" in response.json()["data"], response.json()
        assert hasattr(date_query, "__called__") and getattr(date_query, "__called__")
        parameters = getattr(date_query, "__parameters__")
        assert parameters
        assert isinstance(parameters["t_datetime"], datetime)
        assert isinstance(parameters["t_time"], time)
        assert isinstance(parameters["t_date"], date)
        assert parameters == variables
