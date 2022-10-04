import pytest
from pydantic import BaseModel, Field

from fastgraphql import FastGraphQL
from fastgraphql.scalars import GraphQLScalar
from fastgraphql.exceptions import GraphQLSchemaException


class TestNameConflict:
    def test_type_conflict(self) -> None:
        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException) as e:

            @fast_graphql.type()
            class Model1(BaseModel):
                t_int: int

            @fast_graphql.type(name="Model1")
            class Model2(BaseModel):
                t_int: int

        assert e

    def test_type_input_conflict(self) -> None:
        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException):

            @fast_graphql.type()
            class Model1(BaseModel):
                t_int: int

            @fast_graphql.input(name="Model1")
            class Model2(BaseModel):
                t_int: int

        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException):

            @fast_graphql.type()
            @fast_graphql.input()
            class Model3(BaseModel):
                t_int: int

    def test_type_scalar_conflict(self) -> None:
        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException):

            @fast_graphql.type()
            class Model1(BaseModel):
                t_int: str = Field(..., graphql_scalar=GraphQLScalar("Model1"))

    def test_name_conflict(self) -> None:
        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException):

            @fast_graphql.query()
            def sample_query1() -> bool:
                return False  # pragma: no cover

            @fast_graphql.query(name="sample_query1")
            def sample_query2() -> bool:
                return False  # pragma: no cover

        with pytest.raises(GraphQLSchemaException):

            @fast_graphql.query()
            def sample_query3() -> bool:
                return False  # pragma: no cover

            @fast_graphql.mutation(name="sample_query3")
            def sample_query4() -> bool:
                return False  # pragma: no cover

        with pytest.raises(GraphQLSchemaException):

            @fast_graphql.mutation()
            def sample_query5() -> bool:
                return False  # pragma: no cover

            @fast_graphql.query(name="sample_query5")
            def sample_query6() -> bool:
                return False  # pragma: no cover
