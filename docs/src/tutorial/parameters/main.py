from fastapi import FastAPI
from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router
from pydantic import BaseModel

app = FastAPI()
fast_graphql = FastGraphQL()


@fast_graphql.query()
def hello_query(name: str) -> str:
    return f"Hello {name}!!!"


class Model(BaseModel):
    value: str


class QueryInput(BaseModel):
    value: str


@fast_graphql.query()
def model_query(input: QueryInput) -> Model:
    return Model(value=input.value)


app.include_router(make_ariadne_fastapi_router(fast_graphql=fast_graphql))
