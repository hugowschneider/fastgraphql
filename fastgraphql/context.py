from typing import Optional

from fastgraphql.types import GraphQLType


class AdaptContext:
    def __init__(
        self,
        graphql_type: GraphQLType,
        python_field: str,
        graphql_field: str,
        parent_context: Optional["AdaptContext"],
        in_list: bool = False,
    ) -> None:
        self.graphql_type = graphql_type
        self.python_field = python_field
        self.graphql_field = graphql_field
        self.parent_context = parent_context
        self.in_list = in_list

    def list_context(self) -> "AdaptContext":
        return AdaptContext(
            graphql_field=self.graphql_field,
            python_field=self.python_field,
            graphql_type=self.graphql_type,
            parent_context=self,
            in_list=True,
        )
