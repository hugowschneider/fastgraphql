from fastapi.routing import APIRouter

from fastgraphql import FastGraphQL
from fastgraphql.ariadne import make_graphql_asgi


def make_ariadne_fastapi_router(
    fast_graphql: FastGraphQL, path: str = "/graphql"
) -> APIRouter:
    router = APIRouter()
    router.add_route(path, make_graphql_asgi(fast_graphql))
    return router
