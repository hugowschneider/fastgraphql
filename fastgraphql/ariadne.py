from typing import List

from fastgraphql import FastGraphQL
from fastgraphql.utils import FAST_GRAPHQL_DEBUG, get_env_bool

try:
    from ariadne import (
        MutationType,
        QueryType,
        ScalarType,
        SchemaBindable,
        make_executable_schema as ariadne_make_executable_schema,
    )
    from ariadne.asgi import GraphQL
    from graphql import GraphQLSchema

except ImportError as e:  # pragma: no cover
    raise ImportError("Please use `pip install fastgraphql[ariadne]`") from e


def make_executable_schema(fast_graqhql: FastGraphQL) -> GraphQLSchema:
    mutation = MutationType()
    query = QueryType()
    bindables: List[SchemaBindable] = []
    if len(fast_graqhql.schema.scalars):
        bind_scalars(bindables, fast_graqhql)

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


def bind_scalars(bindables: List[SchemaBindable], fast_graqhql: FastGraphQL) -> None:
    for name, scalar in fast_graqhql.schema.scalars.items():
        if not scalar.default_scalar and (scalar.decoder or scalar.encoder):
            bindables.append(
                ScalarType(
                    scalar.name,
                    serializer=scalar.encoder,
                    value_parser=scalar.decoder,
                )
            )


def make_graphql_asgi(fast_graqhql: FastGraphQL) -> GraphQL:
    return GraphQL(
        make_executable_schema(fast_graqhql),
        debug=get_env_bool(FAST_GRAPHQL_DEBUG, default_value=False),
    )
