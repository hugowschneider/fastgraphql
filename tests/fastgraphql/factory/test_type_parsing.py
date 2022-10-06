from datetime import date, datetime, time
from typing import Optional, Type, cast

import pytest
from pydantic import BaseModel

from fastgraphql.exceptions import GraphQLFactoryException
from fastgraphql.factory import GraphQLTypeFactory, _DateFormats
from fastgraphql.scalars import (
    GraphQLInteger,
    GraphQLString,
    GraphQLFloat,
    GraphQLDate,
    GraphQLDateTime,
    GraphQLTime,
    GraphQLBoolean,
)
from fastgraphql.schema import GraphQLSchema
from fastgraphql.types import GraphQLType


@pytest.fixture(scope="function")
def factory() -> GraphQLTypeFactory:
    return GraphQLTypeFactory(
        schema=GraphQLSchema(),
        date_formats=_DateFormats("", "", ""),
        default_names=None,
    )


class TestFactoryTypeParsing:
    def test_int_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=int, exclude_model_attrs=[], name=""
        )
        assert not nullable
        assert isinstance(graphql_type, GraphQLInteger)

    def test_str_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=str, exclude_model_attrs=[], name=""
        )
        assert not nullable
        assert isinstance(graphql_type, GraphQLString)

    def test_float_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=float, exclude_model_attrs=[], name=""
        )
        assert not nullable
        assert isinstance(graphql_type, GraphQLFloat)

    def test_date_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=date, exclude_model_attrs=[], name=""
        )
        assert not nullable
        assert isinstance(graphql_type, GraphQLDate)

    def test_datetime_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=datetime, exclude_model_attrs=[], name=""
        )
        assert not nullable
        assert isinstance(graphql_type, GraphQLDateTime)

    def test_time_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=time, exclude_model_attrs=[], name=""
        )
        assert not nullable
        assert isinstance(graphql_type, GraphQLTime)

    def test_boolean_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=bool, exclude_model_attrs=[], name=""
        )
        assert not nullable
        assert isinstance(graphql_type, GraphQLBoolean)

    def test_nullable_int_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[int]], Optional[int]),
            exclude_model_attrs=[],
            name="",
        )
        assert nullable
        assert isinstance(graphql_type, GraphQLInteger)

    def test_nullable_str_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[str]], Optional[str]),
            exclude_model_attrs=[],
            name="",
        )
        assert nullable
        assert isinstance(graphql_type, GraphQLString)

    def test_nullable_float_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[float]], Optional[float]),
            exclude_model_attrs=[],
            name="",
        )
        assert nullable
        assert isinstance(graphql_type, GraphQLFloat)

    def test_nullable_date_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[date]], Optional[date]),
            exclude_model_attrs=[],
            name="",
        )
        assert nullable
        assert isinstance(graphql_type, GraphQLDate)

    def test_nullable_datetime_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[datetime]], Optional[datetime]),
            exclude_model_attrs=[],
            name="",
        )
        assert nullable
        assert isinstance(graphql_type, GraphQLDateTime)

    def test_nullable_time_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[time]], Optional[time]),
            exclude_model_attrs=[],
            name="",
        )
        assert nullable
        assert isinstance(graphql_type, GraphQLTime)

    def test_nullable_boolean_type(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[bool]], Optional[bool]),
            exclude_model_attrs=[],
            name="",
        )
        assert nullable
        assert isinstance(graphql_type, GraphQLBoolean)

    def test_model_type(self, factory: GraphQLTypeFactory) -> None:
        class Model(BaseModel):
            ...

        graphql_type, nullable = factory.create_graphql_type(
            python_type=Model, exclude_model_attrs=[], name=""
        )
        assert not nullable
        assert isinstance(graphql_type, GraphQLType)

    def test_nullable_model_type(self, factory: GraphQLTypeFactory) -> None:
        class Model(BaseModel):
            ...

        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[Model]], Optional[Model]),
            exclude_model_attrs=[],
            name="",
        )
        assert nullable
        assert isinstance(graphql_type, GraphQLType)

    def test_unsupported_type(self, factory: GraphQLTypeFactory) -> None:
        class Model:
            ...

        with pytest.raises(GraphQLFactoryException):
            _ = factory.create_graphql_type(
                python_type=Model, exclude_model_attrs=[], name=""
            )
