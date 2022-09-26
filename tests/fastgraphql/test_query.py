from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from fastgraphql import FastGraphQL
from fastgraphql.schema import SelfGraphQL, GraphQLScalar


class TestQueryRendering:
    def test_query_without_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.graphql_query()
        def sample_query() -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_query(): String!        
        """.strip()

        expected_graphql_definition = f"""
type Query {
    {expected_query_definition}
}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_query)
        assert self_graphql
        assert self_graphql.as_query
        assert self_graphql.as_query.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_query_simple_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.graphql_query()
        def sample_query(
            t_int: int = fast_graphql.graphql_query_field(),
            t_opt_int: Optional[int] = fast_graphql.graphql_query_field(),
            t_str: str = fast_graphql.graphql_query_field(),
            t_opt_str: Optional[str] = fast_graphql.graphql_query_field(),
            t_float: float = fast_graphql.graphql_query_field(),
            t_opt_float: Optional[float] = fast_graphql.graphql_query_field(),
            t_datatime: datetime = fast_graphql.graphql_query_field(),
            t_opt_datatime: Optional[datetime] = fast_graphql.graphql_query_field(),
            t_boolean: bool = fast_graphql.graphql_query_field(),
            t_opt_boolean: Optional[bool] = fast_graphql.graphql_query_field(),
        ) -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_query(t_int: Int!, t_opt_int: Int, t_str: String!, t_opt_str: String, t_float: Float!, t_opt_float: Float, t_datatime: Date!, t_opt_datatime: Date, t_boolean: Boolean!, t_opt_boolean: Boolean): String!        
        """.strip()

        expected_graphql_definition = f"""
type Query {
    {expected_query_definition}
}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_query)
        assert self_graphql
        assert self_graphql.as_query
        assert self_graphql.as_query.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_query_renamed_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.graphql_query()
        def sample_query(
            t_int: int = fast_graphql.graphql_query_field(name="x"),
        ) -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_query(x: Int!): String!        
        """.strip()

        expected_graphql_definition = f"""
type Query {
    {expected_query_definition}
}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_query)
        assert self_graphql
        assert self_graphql.as_query
        assert self_graphql.as_query.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_query_retyped_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.graphql_query()
        def sample_query(
            t_int: int = fast_graphql.graphql_query_field(
                name="x", graphql_scalar=GraphQLScalar("CustomScalar")
            )
        ) -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_query(x: CustomScalar!): String!        
        """.strip()

        expected_graphql_definition = f"""
scalar CustomScalar

type Query {
    {expected_query_definition}
}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_query)
        assert self_graphql
        assert self_graphql.as_query
        assert self_graphql.as_query.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_query_complex_parameter(self) -> None:
        fast_graphql = FastGraphQL()

        class Model(BaseModel):
            t_int: int

        @fast_graphql.graphql_query()
        def sample_query(
            model1: Model = fast_graphql.graphql_query_field(),
            model2: Model = fast_graphql.graphql_query_field(),
        ) -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_query(model1: Model!, model2: Model!): String!        
        """.strip()

        expected_graphql_definition = f"""
input Model {{
    t_int: Int!
}}

type Query {
    {expected_query_definition}
}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_query)
        assert self_graphql
        assert self_graphql.as_query
        assert self_graphql.as_query.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_query_return_complex(self) -> None:
        fast_graphql = FastGraphQL()

        class Model(BaseModel):
            t_int: int

        @fast_graphql.graphql_query()
        def sample_query() -> Model:
            return Model()  # pragma: no cover

        expected_query_definition = """
sample_query(): Model!        
        """.strip()

        expected_graphql_definition = f"""
type Model {{
    t_int: Int!
}}

type Query {
    {expected_query_definition}
}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_query)
        assert self_graphql
        assert self_graphql.as_query
        assert self_graphql.as_query.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition
