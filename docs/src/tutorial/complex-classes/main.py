from fastapi import FastAPI
from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

from pydantic import BaseModel
from typing import List

app = FastAPI()
fast_graphql = FastGraphQL()


@fast_graphql.type()
class Address(BaseModel):
    planet: str


@fast_graphql.type()
class Person(BaseModel):
    first_name: str
    last_name: str
    age: int
    height: float
    addresses: List[Address]
    siblings: List["Person"]


@fast_graphql.query()
def get_person() -> Person:
    return Person(
        first_name="Luke",
        last_name="Skywalker",
        height=1.7,
        age=23,
        siblings=[
            Person(
                first_name="Leia",
                last_name="Organa",
                age=23,
                height=1.6,
                addresses=[],
                siblings=[],
            )
        ],
        addresses=[Address(planet="Tatooine")],
    )


app.include_router(make_ariadne_fastapi_router(fast_graphql=fast_graphql))
