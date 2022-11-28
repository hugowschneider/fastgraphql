from fastapi import FastAPI
from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

app = FastAPI()
fast_graphql = FastGraphQL()


@fast_graphql.mutation()
def dummy_mutation() -> str:
    ... # Implement some state-changing logic
    return "Done!"


app.include_router(make_ariadne_fastapi_router(fast_graphql=fast_graphql))
