from typing import Dict, List, Optional, Type, cast

import pytest
from pydantic import BaseModel

from fastgraphql.exceptions import GraphQLFactoryException
from fastgraphql.factory import GraphQLTypeFactory, _DateFormats
from fastgraphql.schema import GraphQLSchema
from fastgraphql.types import GraphQLArray, GraphQLReference


@pytest.fixture(scope="function")
def factory() -> GraphQLTypeFactory:
    return GraphQLTypeFactory(
        schema=GraphQLSchema(), date_formats=_DateFormats("", "", "")
    )


class TestFactoryGenericTypeParsing:
    def test_array_non_nullable(self, factory: GraphQLTypeFactory) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=List[bool], exclude_model_attrs=[], name=""
        )

        assert not nullable
        assert isinstance(graphql_type, GraphQLArray)
        assert isinstance(graphql_type.item_type, GraphQLReference)
        assert graphql_type.item_type.nullable is False
        assert graphql_type.item_type.referenced_type.name == "Boolean"

    def test_array_non_nullable_nullable_item(
        self, factory: GraphQLTypeFactory
    ) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=List[Optional[bool]], exclude_model_attrs=[], name=""
        )

        assert not nullable
        assert isinstance(graphql_type, GraphQLArray)
        assert isinstance(graphql_type.item_type, GraphQLReference)
        assert graphql_type.item_type.nullable
        assert graphql_type.item_type.referenced_type.name == "Boolean"

    def test_array_nullable_non_nullable_item(
        self, factory: GraphQLTypeFactory
    ) -> None:
        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[List[bool]]], Optional[List[bool]]),
            exclude_model_attrs=[],
            name="",
        )

        assert nullable
        assert isinstance(graphql_type, GraphQLArray)
        assert isinstance(graphql_type.item_type, GraphQLReference)
        assert graphql_type.item_type.nullable is False
        assert graphql_type.item_type.referenced_type.name == "Boolean"

    def test_model_array_non_nullable(self, factory: GraphQLTypeFactory) -> None:
        class Model(BaseModel):
            ...

        graphql_type, nullable = factory.create_graphql_type(
            python_type=List[Model], exclude_model_attrs=[], name=""
        )

        assert not nullable
        assert isinstance(graphql_type, GraphQLArray)
        assert isinstance(graphql_type.item_type, GraphQLReference)
        assert graphql_type.item_type.nullable is False
        assert graphql_type.item_type.referenced_type.name == "Model"

    def test_model_array_non_nullable_nullable_item(
        self, factory: GraphQLTypeFactory
    ) -> None:
        class Model(BaseModel):
            ...

        graphql_type, nullable = factory.create_graphql_type(
            python_type=List[Optional[Model]],
            exclude_model_attrs=[],
            name="",
        )

        assert not nullable
        assert isinstance(graphql_type, GraphQLArray)
        assert isinstance(graphql_type.item_type, GraphQLReference)
        assert graphql_type.item_type.nullable
        assert graphql_type.item_type.referenced_type.name == "Model"

    def test_model_array_nullable_non_nullable_item(
        self, factory: GraphQLTypeFactory
    ) -> None:
        class Model(BaseModel):
            ...

        graphql_type, nullable = factory.create_graphql_type(
            python_type=cast(Type[Optional[List[Model]]], Optional[List[Model]]),
            exclude_model_attrs=[],
            name="",
        )

        assert nullable
        assert isinstance(graphql_type, GraphQLArray)
        assert isinstance(graphql_type.item_type, GraphQLReference)
        assert graphql_type.item_type.nullable is False
        assert graphql_type.item_type.referenced_type.name == "Model"

    def test_unsupported_generic(self, factory: GraphQLTypeFactory) -> None:

        with pytest.raises(GraphQLFactoryException):
            factory.handle_generic_types(Dict[str, int])
