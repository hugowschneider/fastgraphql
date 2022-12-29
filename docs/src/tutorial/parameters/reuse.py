from fastapi import FastAPI
from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router
from pydantic import BaseModel

app = FastAPI()
fast_graphql = FastGraphQL()


# @fast_graphql.input(name="ModelInput")
class Model(BaseModel):
    value: str


@fast_graphql.query()
def model_query(input: Model) -> Model:
    return Model(value=input.value)


app.include_router(make_ariadne_fastapi_router(fast_graphql=fast_graphql))
