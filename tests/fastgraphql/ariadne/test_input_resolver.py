import json

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router
from fastgraphql.utils import DefaultToCamelCase

GRAPHQL_URL = "/graphql"
JSON_CONTENT_TYPE_HEADER = {"Content-Type": "application/json"}

fast_graphql = FastGraphQL()


@fast_graphql.type()
@fast_graphql.input(name="ModelInput")
class Model(BaseModel):
    t_int: int
    t_date: datetime


@fast_graphql.type()
@fast_graphql.input(name="NestedModelInput")
class NestedModel(BaseModel):
    model: Model


@fast_graphql.type()
@fast_graphql.input(name="ModelCustomFieldInput")
class ModelCustomField(BaseModel):
    t_int: int = Field(graphql_name="typeInt")
    t_date: datetime = Field(graphql_name="typeDateTime")


@fast_graphql.type()
@fast_graphql.input(name="NestedModelCustomFieldInput")
class NestedModelCustomField(BaseModel):
    t_int: int = Field(graphql_name="typeInt")
    model_custom_field: ModelCustomField = Field(graphql_name="modelCustomField")
    t_str: str


@fast_graphql.query()
def std_type_query(
    t_int: int = fast_graphql.parameter(),
    t_opt_int: Optional[int] = fast_graphql.parameter(),
    t_str: str = fast_graphql.parameter(),
    t_opt_str: Optional[str] = fast_graphql.parameter(),
    t_float: float = fast_graphql.parameter(),
    t_opt_float: Optional[float] = fast_graphql.parameter(),
    t_datatime: datetime = fast_graphql.parameter(),
    t_opt_datatime: Optional[datetime] = fast_graphql.parameter(),
    t_boolean: bool = fast_graphql.parameter(),
    t_opt_boolean: Optional[bool] = fast_graphql.parameter(),
) -> str:
    setattr(std_type_query, "__called__", True)
    setattr(
        std_type_query,
        "__parameters__",
        {
            "t_int": t_int,
            "t_opt_int": t_opt_int,
            "t_str": t_str,
            "t_opt_str": t_opt_str,
            "t_float": t_float,
            "t_opt_float": t_opt_float,
            "t_datatime": t_datatime,
            "t_opt_datatime": t_opt_datatime,
            "t_boolean": t_boolean,
            "t_opt_boolean": t_opt_boolean,
        },
    )
    return "result"


@fast_graphql.query()
def model_query(model: Model = fast_graphql.parameter()) -> Model:
    setattr(model_query, "__called__", True)
    setattr(model_query, "__parameters__", {"model": model})
    return model


@fast_graphql.query()
def nested_model_query(model: NestedModel = fast_graphql.parameter()) -> NestedModel:
    setattr(nested_model_query, "__called__", True)
    setattr(nested_model_query, "__parameters__", {"model": model})
    return model


@fast_graphql.query()
def model_custom_field_query(
    model: ModelCustomField = fast_graphql.parameter(),
) -> ModelCustomField:
    setattr(model_custom_field_query, "__called__", True)
    setattr(model_custom_field_query, "__parameters__", {"model": model})
    return model


@fast_graphql.query()
def nested_model_custom_field_query(
    model: NestedModelCustomField = fast_graphql.parameter(),
) -> NestedModelCustomField:
    setattr(nested_model_custom_field_query, "__called__", True)
    setattr(nested_model_custom_field_query, "__parameters__", {"model": model})
    return model


@fast_graphql.query()
def query_custom_param_name(t_int: int = fast_graphql.parameter(name="typeInt")) -> int:
    setattr(query_custom_param_name, "__called__", True)
    setattr(query_custom_param_name, "__parameters__", {"t_int": t_int})
    return t_int


@fast_graphql.query(default_names=DefaultToCamelCase())
def query_camel_case(t_int: int = fast_graphql.parameter()) -> int:
    setattr(query_camel_case, "__called__", True)
    setattr(query_camel_case, "__parameters__", {"t_int": t_int})
    return t_int


@pytest.fixture(scope="class", autouse=True)
def fastapi_test(request: Any) -> None:

    request.cls.app = FastAPI()
    request.cls.app.include_router(
        make_ariadne_fastapi_router(fast_graphql=fast_graphql)
    )
    request.cls.test_client = TestClient(request.cls.app)


@pytest.mark.usefixtures("fastapi_test")
class TestInputResolversWithAriadneFastAPIIntegration:
    app: FastAPI
    test_client: TestClient

    def test_graphql_simple_input_resolver_with_nones(self) -> None:
        query = """
query Query(
            $t_int: Int!,
            $t_opt_int: Int,
            $t_str: String!,
            $t_opt_str: String,
            $t_float: Float!,
            $t_opt_float: Float,
            $t_datatime: DateTime!,
            $t_opt_datatime: DateTime,
            $t_boolean: Boolean!,
            $t_opt_boolean: Boolean,
){
    std_type_query(
            t_int: $t_int,
            t_opt_int: $t_opt_int,
            t_str: $t_str,
            t_opt_str: $t_opt_str,
            t_float: $t_float,
            t_opt_float: $t_opt_float,
            t_datatime: $t_datatime,
            t_opt_datatime: $t_opt_datatime,
            t_boolean: $t_boolean,
            t_opt_boolean: $t_opt_boolean,
    )
}
        """.strip()
        date_value = datetime(
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
            "t_int": 911,
            "t_opt_int": None,
            "t_str": "string",
            "t_opt_str": None,
            "t_float": 9.11,
            "t_opt_float": None,
            "t_datatime": date_value,
            "t_opt_datatime": None,
            "t_boolean": True,
            "t_opt_boolean": None,
        }
        response = self.test_client.post(
            GRAPHQL_URL,
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers=JSON_CONTENT_TYPE_HEADER,
        )

        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "std_type_query" in response.json()["data"]
        assert hasattr(std_type_query, "__called__") and getattr(
            std_type_query, "__called__"
        )
        parameters = getattr(std_type_query, "__parameters__")
        assert parameters
        assert isinstance(parameters["t_int"], int)
        assert parameters["t_opt_int"] is None
        assert isinstance(parameters["t_str"], str)
        assert parameters["t_opt_str"] is None
        assert isinstance(parameters["t_float"], float)
        assert parameters["t_opt_float"] is None
        assert isinstance(parameters["t_datatime"], datetime)
        assert parameters["t_opt_datatime"] is None
        assert isinstance(parameters["t_boolean"], bool)
        assert parameters["t_opt_boolean"] is None
        assert parameters == variables

    def test_graphql_simple_input_resolver_without_nones(self) -> None:
        query = """
query Query(
            $t_int: Int!,
            $t_opt_int: Int,
            $t_str: String!,
            $t_opt_str: String,
            $t_float: Float!,
            $t_opt_float: Float,
            $t_datatime: DateTime!,
            $t_opt_datatime: DateTime,
            $t_boolean: Boolean!,
            $t_opt_boolean: Boolean,
){
    std_type_query(
            t_int: $t_int,
            t_opt_int: $t_opt_int,
            t_str: $t_str,
            t_opt_str: $t_opt_str,
            t_float: $t_float,
            t_opt_float: $t_opt_float,
            t_datatime: $t_datatime,
            t_opt_datatime: $t_opt_datatime,
            t_boolean: $t_boolean,
            t_opt_boolean: $t_opt_boolean,
    )
}
        """.strip()
        date_value = datetime(
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
            "t_int": 911,
            "t_opt_int": 119,
            "t_str": "string",
            "t_opt_str": "gnirts",
            "t_float": 9.11,
            "t_opt_float": 11.9,
            "t_datatime": date_value,
            "t_opt_datatime": date_value,
            "t_boolean": True,
            "t_opt_boolean": False,
        }
        response = self.test_client.post(
            GRAPHQL_URL,
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers=JSON_CONTENT_TYPE_HEADER,
        )
        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "std_type_query" in response.json()["data"]
        assert hasattr(std_type_query, "__called__") and getattr(
            std_type_query, "__called__"
        )
        parameters = getattr(std_type_query, "__parameters__")
        assert parameters
        assert isinstance(parameters["t_int"], int)
        assert isinstance(parameters["t_opt_int"], int)
        assert isinstance(parameters["t_str"], str)
        assert isinstance(parameters["t_opt_str"], str)
        assert isinstance(parameters["t_float"], float)
        assert isinstance(parameters["t_opt_float"], float)
        assert isinstance(parameters["t_datatime"], datetime)
        assert isinstance(parameters["t_opt_datatime"], datetime)
        assert isinstance(parameters["t_boolean"], bool)
        assert isinstance(parameters["t_opt_boolean"], bool)
        assert parameters == variables

    def test_graphql_model_input_resolver(self) -> None:
        query = """
      query Query(
                  $model: ModelInput!
      ){
          model_query(
                  model: $model,
          ) {
              t_int
              t_date
          }
      }
              """.strip()
        model = Model(
            t_int=1,
            t_date=datetime(
                year=2022,
                month=10,
                day=1,
                hour=8,
                minute=25,
                second=11,
                microsecond=0,
                tzinfo=timezone(timedelta(hours=-2)),
            ),
        )
        variables = {"model": model.dict()}
        response = self.test_client.post(
            GRAPHQL_URL,
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers=JSON_CONTENT_TYPE_HEADER,
        )

        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "model_query" in response.json()["data"], response.json()
        assert hasattr(model_query, "__called__") and getattr(model_query, "__called__")
        parameters = getattr(model_query, "__parameters__")
        assert parameters
        assert isinstance(parameters["model"], Model)
        assert parameters == variables

    def test_graphql_nested_model_input_resolver(self) -> None:
        query = """
query Query(
            $model: NestedModelInput!
){
    nested_model_query(
            model: $model,
    ) {
        model {
            t_int
            t_date
        }
    }
}
        """.strip()
        model = NestedModel(
            model=Model(
                t_int=1,
                t_date=datetime(
                    year=2022,
                    month=10,
                    day=1,
                    hour=8,
                    minute=25,
                    second=11,
                    microsecond=0,
                    tzinfo=timezone(timedelta(hours=-2)),
                ),
            )
        )
        variables = {"model": model.dict()}
        response = self.test_client.post(
            GRAPHQL_URL,
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers=JSON_CONTENT_TYPE_HEADER,
        )

        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "nested_model_query" in response.json()["data"], response.json()
        assert hasattr(nested_model_query, "__called__") and getattr(
            nested_model_query, "__called__"
        )
        parameters = getattr(nested_model_query, "__parameters__")
        assert parameters
        assert isinstance(parameters["model"], NestedModel)
        assert isinstance(parameters["model"].model, Model)
        assert parameters == variables

    def test_graphql_model_with_custom_field_name(self) -> None:
        query = """
query Query(
            $model: ModelCustomFieldInput!
){
    model_custom_field_query(
            model: $model,
    ) {
        typeInt
        typeDateTime
    }
}
        """.strip()

        variables = {
            "model": {
                "typeInt": 1,
                "typeDateTime": datetime(
                    year=2022,
                    month=10,
                    day=1,
                    hour=8,
                    minute=25,
                    second=11,
                    microsecond=0,
                    tzinfo=timezone(timedelta(hours=-2)),
                ),
            }
        }
        response = self.test_client.post(
            GRAPHQL_URL,
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers=JSON_CONTENT_TYPE_HEADER,
        )

        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "model_custom_field_query" in response.json()["data"], response.json()
        assert hasattr(model_custom_field_query, "__called__") and getattr(
            model_custom_field_query, "__called__"
        )
        parameters = getattr(model_custom_field_query, "__parameters__")
        assert parameters
        assert isinstance(parameters["model"], ModelCustomField)
        assert parameters["model"].t_int == variables["model"]["typeInt"]
        assert parameters["model"].t_date == variables["model"]["typeDateTime"]

    def test_graphql_nested_model_with_custom_field_name(self) -> None:

        query = """
query Query(
            $model: NestedModelCustomFieldInput!
){
    nested_model_custom_field_query(
            model: $model,
    ) {
        typeInt
        modelCustomField {
            typeInt
        }
        t_str
    }
}
        """.strip()

        variables = {
            "model": {
                "typeInt": 1,
                "t_str": "asd",
                "modelCustomField": {
                    "typeInt": 1,
                    "typeDateTime": datetime(
                        year=2022,
                        month=10,
                        day=1,
                        hour=8,
                        minute=25,
                        second=11,
                        microsecond=0,
                        tzinfo=timezone(timedelta(hours=-2)),
                    ),
                },
            }
        }
        response = self.test_client.post(
            GRAPHQL_URL,
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers=JSON_CONTENT_TYPE_HEADER,
        )

        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert (
            "nested_model_custom_field_query" in response.json()["data"]
        ), response.json()
        assert hasattr(nested_model_custom_field_query, "__called__") and getattr(
            nested_model_custom_field_query, "__called__"
        )
        parameters = getattr(nested_model_custom_field_query, "__parameters__")
        assert parameters
        assert isinstance(parameters["model"], NestedModelCustomField)
        assert isinstance(parameters["model"].model_custom_field, ModelCustomField)
        assert parameters["model"].t_int == variables["model"]["typeInt"]

    def test_query_custom_param_name(self) -> None:
        query = """
query Query(
            $typeInt: Int!,
){
    query_custom_param_name(
            typeInt: $typeInt,
    )
}
        """.strip()

        variables = {
            "typeInt": 911,
        }
        response = self.test_client.post(
            GRAPHQL_URL,
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers=JSON_CONTENT_TYPE_HEADER,
        )
        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "query_custom_param_name" in response.json()["data"]
        assert hasattr(query_custom_param_name, "__called__") and getattr(
            query_custom_param_name, "__called__"
        )
        parameters = getattr(query_custom_param_name, "__parameters__")
        assert parameters
        assert isinstance(parameters["t_int"], int)
        assert parameters["t_int"] == variables["typeInt"]

    def test_query_camel_case(self) -> None:
        query = """
query Query(
            $tInt: Int!,
){
    queryCamelCase(
            tInt: $tInt,
    )
}
        """.strip()

        variables = {
            "tInt": 911,
        }
        response = self.test_client.post(
            GRAPHQL_URL,
            data=json.dumps(
                {"query": query, "variables": variables},
                default=lambda x: x.isoformat(),
            ),
            headers=JSON_CONTENT_TYPE_HEADER,
        )
        assert response.status_code == 200, response.json()
        assert "errors" not in response.json(), response.json()
        assert "data" in response.json(), response.json()
        assert "queryCamelCase" in response.json()["data"]
        assert hasattr(query_camel_case, "__called__") and getattr(
            query_camel_case, "__called__"
        )
        parameters = getattr(query_camel_case, "__parameters__")
        assert parameters
        assert isinstance(parameters["t_int"], int)
        assert parameters["t_int"] == variables["tInt"]
