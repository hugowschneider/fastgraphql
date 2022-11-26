from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from fastgraphql import FastGraphQL
from fastgraphql.scalars import GraphQLScalar
from fastgraphql.schema import SelfGraphQL


class TestQueryRendering:
    def test_mutation_without_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.mutation()
        def sample_mutation() -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_mutation: String!""".strip()

        expected_graphql_definition = f"""
type Mutation {{
    {expected_query_definition}
}}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_mutation)
        assert self_graphql
        assert self_graphql.as_mutation
        assert self_graphql.as_mutation.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_renamed_query(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.mutation(name="q1")
        def sample_query() -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
q1: String!
        """.strip()

        expected_graphql_definition = f"""
type Mutation {{
    {expected_query_definition}
}}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_query)
        assert self_graphql
        assert self_graphql.as_mutation
        assert self_graphql.as_mutation.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_mutation_simple_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.mutation()
        def sample_mutation(
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
            return ""  # pragma: no cover

        expected_query_definition = """
sample_mutation(t_int: Int!, t_opt_int: Int, t_str: String!, t_opt_str: String, t_float: Float!, t_opt_float: Float, t_datatime: DateTime!, t_opt_datatime: DateTime, t_boolean: Boolean!, t_opt_boolean: Boolean): String!
        """.strip()  # noqa

        expected_graphql_definition = f"""
scalar DateTime

type Mutation {{
    {expected_query_definition}
}}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_mutation)
        assert self_graphql
        assert self_graphql.as_mutation
        assert self_graphql.as_mutation.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_mutation_renamed_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.mutation()
        def sample_mutation(
            t_int: int = fast_graphql.parameter(name="x"),
        ) -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_mutation(x: Int!): String!
        """.strip()

        expected_graphql_definition = f"""
type Mutation {{
    {expected_query_definition}
}}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_mutation)
        assert self_graphql
        assert self_graphql.as_mutation
        assert self_graphql.as_mutation.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_mutation_retyped_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.mutation()
        def sample_mutation(
            t_int: int = fast_graphql.parameter(
                name="x", graphql_scalar=GraphQLScalar("CustomScalar")
            )
        ) -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_mutation(x: CustomScalar!): String!
        """.strip()

        expected_graphql_definition = f"""
scalar CustomScalar

type Mutation {{
    {expected_query_definition}
}}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_mutation)
        assert self_graphql
        assert self_graphql.as_mutation
        assert self_graphql.as_mutation.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_mutation_complex_parameter(self) -> None:
        fast_graphql = FastGraphQL()

        class Model(BaseModel):
            t_int: int

        @fast_graphql.mutation()
        def sample_mutation(
            model1: Model = fast_graphql.parameter(),
            model2: Model = fast_graphql.parameter(),
        ) -> str:
            return ""  # pragma: no cover

        expected_query_definition = """
sample_mutation(model1: Model!, model2: Model!): String!
        """.strip()

        expected_graphql_definition = f"""
input Model {{
    t_int: Int!
}}

type Mutation {{
    {expected_query_definition}
}}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_mutation)
        assert self_graphql
        assert self_graphql.as_mutation
        assert self_graphql.as_mutation.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition

    def test_mutation_return_complex(self) -> None:
        fast_graphql = FastGraphQL()

        class Model(BaseModel):
            t_int: int

        @fast_graphql.mutation()
        def sample_mutation() -> Model:
            return Model()  # pragma: no cover

        @fast_graphql.mutation()
        def sample_mutation2() -> Model:
            return Model()  # pragma: no cover

        expected_query_definition = """
sample_mutation: Model!
        """.strip()

        expected_graphql_definition = f"""
type Model {{
    t_int: Int!
}}

type Mutation {{
    {expected_query_definition}
    sample_mutation2: Model!
}}""".strip()

        self_graphql = SelfGraphQL.introspect(sample_mutation)
        assert self_graphql
        assert self_graphql.as_mutation
        assert self_graphql.as_mutation.render() == expected_query_definition
        assert fast_graphql.render() == expected_graphql_definition
