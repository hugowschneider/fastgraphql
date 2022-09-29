import pytest

from fastgraphql import FastGraphQL
from fastgraphql.exceptions import GraphQLFactoryException
from fastgraphql.factory import GraphQLTypeFactory, _DateFormats, GraphQLFunctionFactory
from fastgraphql.schema import GraphQLSchema


@pytest.fixture(scope="function")
def type_factory() -> GraphQLTypeFactory:
    return GraphQLTypeFactory(
        schema=GraphQLSchema(), date_formats=_DateFormats("", "", "")
    )


@pytest.fixture(scope="function")
def function_factory(type_factory: GraphQLTypeFactory) -> GraphQLFunctionFactory:
    return GraphQLFunctionFactory(
        schema=GraphQLSchema(), type_factory=type_factory, input_factory=type_factory
    )


class TestFactoryFunctionParsing:
    def test_incomplete_input_type(
        self, function_factory: GraphQLFunctionFactory
    ) -> None:
        fast_graphql = FastGraphQL()

        def func(input=fast_graphql.graphql_query_field()) -> str:  # type: ignore # pragma: no cover
            ...

        with pytest.raises(GraphQLFactoryException):
            _ = function_factory.create_function(func=func)

    def test_incomplete_return_type(
        self, function_factory: GraphQLFunctionFactory
    ) -> None:
        fast_graphql = FastGraphQL()

        def func(input: str = fast_graphql.graphql_query_field()):  # type: ignore # pragma: no cover
            ...

        with pytest.raises(GraphQLFactoryException):
            _ = function_factory.create_function(func=func)
