import pytest
from pydantic import BaseModel, Field

from fastgraphql import FastGraphQL
from fastgraphql.schema import GraphQLSchemaException, GraphQLScalar


class TestNameConflict:

    def test_type_conflict(self):
        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException) as e:

            @fast_graphql.graphql_type()
            class Model1(BaseModel):
                t_int : int

            @fast_graphql.graphql_type(name="Model1")
            class Model2(BaseModel):
                t_int : int

        assert e

    def test_type_input_conflict(self):
        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException) as e:

            @fast_graphql.graphql_type()
            class Model1(BaseModel):
                t_int : int

            @fast_graphql.graphql_input(name="Model1")
            class Model2(BaseModel):
                t_int : int

        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException) as e:
            @fast_graphql.graphql_type()
            @fast_graphql.graphql_input()
            class Model1(BaseModel):
                t_int: int

    def test_type_scalar_conflict(self):
        fast_graphql = FastGraphQL()
        with pytest.raises(GraphQLSchemaException) as e:

            @fast_graphql.graphql_type()
            class Model1(BaseModel):
                t_int : str = Field(..., graphql_scalar = GraphQLScalar("Model1"))

