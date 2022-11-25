import pytest

from fastgraphql import FastGraphQL
from fastgraphql.exceptions import GraphQLFactoryException
from fastgraphql.factory import GraphQLFunctionFactory, GraphQLTypeFactory, _DateFormats
from fastgraphql.schema import GraphQLSchema


@pytest.fixture(scope="function")
def type_factory() -> GraphQLTypeFactory:
    return GraphQLTypeFactory(
        schema=GraphQLSchema(),
        date_formats=_DateFormats("", "", ""),
        default_names=None,
    )


@pytest.fixture(scope="function")
def function_factory(type_factory: GraphQLTypeFactory) -> GraphQLFunctionFactory:
    return GraphQLFunctionFactory(
        schema=GraphQLSchema(),
        type_factory=type_factory,
        input_factory=type_factory,
        default_names=None,
    )


class TestFactoryFunctionParsing:
    def test_incomplete_input_type(
        self, function_factory: GraphQLFunctionFactory
    ) -> None:
        fast_graphql = FastGraphQL()

        def func(input=fast_graphql.parameter()) -> str:  # type: ignore # pragma: no cover # noqa
            ...

        with pytest.raises(GraphQLFactoryException):
            _ = function_factory.create_function(func=func)

    def test_incomplete_return_type(
        self, function_factory: GraphQLFunctionFactory
    ) -> None:
        fast_graphql = FastGraphQL()

        def func(input: str = fast_graphql.parameter()):  # type: ignore # pragma: no cover # noqa
            ...

        with pytest.raises(GraphQLFactoryException):
            _ = function_factory.create_function(func=func)
