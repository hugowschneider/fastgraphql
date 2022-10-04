import pytest
from pydantic import BaseModel, Field

from fastgraphql import FastGraphQL
from fastgraphql.schema import SelfGraphQL


@pytest.fixture(scope="function")
def fast_graphql() -> FastGraphQL:
    return FastGraphQL()


class TestFactoryFunctionParsing:
    def test_pydantic_custom_field_name(self, fast_graphql: FastGraphQL) -> None:
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
