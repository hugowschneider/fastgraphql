from fastgraphql import FastGraphQL
from fastgraphql.ariadne import make_graphql_asgi

try:
    from fastapi.routing import APIRouter
except ImportError as e:  # pragma: no cover
    raise ImportError(f"{e}.\nPlease use `pip install fastgraphql[ariadne]`") from e


def make_ariadne_fastapi_router(
    fast_graphql: FastGraphQL, path: str = "/graphql"
) -> APIRouter:
    router = APIRouter()
    router.add_route(path, make_graphql_asgi(fast_graphql))
    return router
