from fastapi import FastAPI
from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

app = FastAPI()
fast_graphql = FastGraphQL()


@fast_graphql.query()
def hello() -> str:
    return f"Hello FastGraphQL!!!"


app.include_router(make_ariadne_fastapi_router(fast_graphql=fast_graphql))
