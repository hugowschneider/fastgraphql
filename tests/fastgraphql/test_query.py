from fastgraphql import FastGraphQL
from fastgraphql.schema import SelfGraphQL


class TestQueryRendering:
    def test_query_without_parameters(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.graphql_query()
        def sample_query() -> str:
            return ""

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
