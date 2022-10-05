from pydantic import BaseModel, Field

from fastgraphql import FastGraphQL
from fastgraphql.schema import SelfGraphQL
from fastgraphql.utils import DefaultToCamelCase, DefaultUnchanged


class TestFactoryFunctionParsing:
    def test_pydantic_custom_field_name(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class Model(BaseModel):
            custom_field: str = Field(graphql_name="customField")

        expected_graphql_def = """
type Model {
    customField: String!
}""".strip()
        self_graphql = SelfGraphQL.introspect(Model)
        assert self_graphql
        assert self_graphql.as_type

        assert self_graphql.as_type.render() == expected_graphql_def

    def test_pydantic_global_default_name(self) -> None:
        fast_graphql = FastGraphQL(default_names=DefaultToCamelCase())

        @fast_graphql.type()
        class Model(BaseModel):
            to_camel_case_field: str

        expected_graphql_def = """
type Model {
    toCamelCaseField: String!
}""".strip()
        self_graphql = SelfGraphQL.introspect(Model)
        assert self_graphql
        assert self_graphql.as_type

        assert self_graphql.as_type.render() == expected_graphql_def

    def test_pydantic_local_default_name(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.type(default_names=DefaultToCamelCase())
        class Model(BaseModel):
            to_camel_case_field: str

        expected_graphql_def = """
type Model {
    toCamelCaseField: String!
}""".strip()
        self_graphql = SelfGraphQL.introspect(Model)
        assert self_graphql
        assert self_graphql.as_type

        assert self_graphql.as_type.render() == expected_graphql_def

    def test_pydantic_local_override_default_name(self) -> None:
        fast_graphql = FastGraphQL(default_names=DefaultUnchanged())

        @fast_graphql.type(default_names=DefaultToCamelCase())
        class Model(BaseModel):
            to_camel_case_field: str

        expected_graphql_def = """
type Model {
    toCamelCaseField: String!
}""".strip()
        self_graphql = SelfGraphQL.introspect(Model)
        assert self_graphql
        assert self_graphql.as_type
        assert self_graphql.as_type.render() == expected_graphql_def

    def test_pydantic_name_override_all_default(self) -> None:
        fast_graphql = FastGraphQL(default_names=DefaultUnchanged())

        @fast_graphql.type(default_names=DefaultToCamelCase())
        class Model(BaseModel):
            to_camel_case_field: str = Field(graphql_name="customName")

        expected_graphql_def = """
type Model {
    customName: String!
}""".strip()
        self_graphql = SelfGraphQL.introspect(Model)
        assert self_graphql
        assert self_graphql.as_type
        assert self_graphql.as_type.render() == expected_graphql_def