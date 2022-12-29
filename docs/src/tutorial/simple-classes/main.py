from fastapi import FastAPI
from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

from pydantic import BaseModel

app = FastAPI()
fast_graphql = FastGraphQL()


@fast_graphql.type()
class Person(BaseModel):
    first_name: str
    last_name: str
    age: int
    height: float


@fast_graphql.query()
def get_person() -> Person:
    return Person(first_name="Luke", last_name="Skywalker", height=1.7, age=23)


app.include_router(make_ariadne_fastapi_router(fast_graphql=fast_graphql))
