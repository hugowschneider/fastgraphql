from datetime import datetime
from typing import List

from fastgraphql import FastGraphQL
from fastgraphql.schema import GraphQLDate, GraphQLTime, GraphQLDateTime
from fastgraphql.utils import get_env_bool, FAST_GRAPHQL_DEBUG

try:
    from ariadne import (
        make_executable_schema as ariadne_make_executable_schema,
        MutationType,
        QueryType,
        SchemaBindable,
        ScalarType,
    )
    from ariadne.asgi import GraphQL

except ImportError as e:
    raise ImportError(f"{e}.\nPlease use `pip install fastgraphql[ariadne]`")
from graphql import GraphQLSchema


def make_executable_schema(fast_graqhql: FastGraphQL) -> GraphQLSchema:
    mutation = MutationType()
    query = QueryType()
    bindables: List[SchemaBindable] = []
    if len(fast_graqhql.schema.scalars):
        for name, scalar in fast_graqhql.schema.scalars.items():
            if isinstance(scalar, GraphQLDate):
                bindables.append(
                    ScalarType(
                        scalar.name,
                        serializer=lambda x: x.strftime(fast_graqhql.date_format),
                        value_parser=lambda x: datetime.strptime(
                            x, fast_graqhql.date_format
                        ).date(),
                    )
                )
            elif isinstance(scalar, GraphQLTime):
                bindables.append(
                    ScalarType(
                        scalar.name,
                        serializer=lambda x: x.strftime(fast_graqhql.date_format),
                        value_parser=lambda x: datetime.strptime(
                            x, fast_graqhql.time_format
                        ).time(),
                    )
                )
            elif isinstance(scalar, GraphQLDateTime):
                bindables.append(
                    ScalarType(
                        scalar.name,
                        serializer=lambda x: x.strftime(fast_graqhql.date_format),
                        value_parser=lambda x: datetime.strptime(
                            x, fast_graqhql.date_time_format
                        ),
                    )
                )

    if len(fast_graqhql.schema.queries):
        bindables.append(query)
        for name, query_ in fast_graqhql.schema.queries.items():
            if r := query_.resolver:
                query.set_field(name, r)

    if len(fast_graqhql.schema.mutations):
        bindables.append(mutation)
        for name, mutation_ in fast_graqhql.schema.mutations.items():
            if r := mutation_.resolver:
                mutation.set_field(name, r)

    return ariadne_make_executable_schema(fast_graqhql.render(), *bindables)


def make_graphql_asgi(fast_graqhql: FastGraphQL) -> GraphQL:
    return GraphQL(
        make_executable_schema(fast_graqhql),
        debug=get_env_bool(FAST_GRAPHQL_DEBUG, default_value=False),
    )
