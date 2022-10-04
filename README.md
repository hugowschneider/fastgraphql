# FastGraphQL
FastGraphQL is intended to help developer create code driven GraphQL APIs.

![pypi](https://img.shields.io/pypi/v/fastgraphql)
![Python Versions](https://img.shields.io/pypi/pyversions/fastgraphql.svg?color=%2334D058)
![License](https://img.shields.io/pypi/l/fastgraphql)

[![codecov](https://codecov.io/gh/hugowschneider/fastgraphql/branch/main/graph/badge.svg?token=FCC5LMA0IQ)](https://codecov.io/gh/hugowschneider/fastgraphql)
![tests](https://github.com/hugowschneider/fastgraphql/actions/workflows/test.yaml/badge.svg)


[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=hugowschneider_fastgraphql&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=hugowschneider_fastgraphql)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=hugowschneider_fastgraphql&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=hugowschneider_fastgraphql)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=hugowschneider_fastgraphql&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=hugowschneider_fastgraphql)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=hugowschneider_fastgraphql&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=hugowschneider_fastgraphql)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=hugowschneider_fastgraphql&metric=bugs)](https://sonarcloud.io/summary/new_code?id=hugowschneider_fastgraphql)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=hugowschneider_fastgraphql&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=hugowschneider_fastgraphql)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=hugowschneider_fastgraphql&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=hugowschneider_fastgraphql)

# Disclaimer

*This is still a work in progress*

# Motivation

So far most of the projects that uses GraphQL need to duplicate
many definitions to be able to have a consistent GraphQL API schema 
alongside well-defined models that governs the development and the application.

FastGraphQL tries to shortcut the path between python models and GraphQL schema
using **Pydantic** models. This ensures not only a single source of truth when comes to 
type, inputs, query and mutation definition reflected in classes and methods, but also the
ability to use **Pydantic** to validate models.

# Installation

```commandline
pip install fastgraphql
```


# Usage

## GraphQL Types and Inputs

Using annotation driven definitions and **Pydantic**, defining GraphQL types
and inputs can be done by simple annotating **Pydantic** models with `FastGraphQL.graphql_type()`
of `FastGraphQL.graphql_input()`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastgraphql import FastGraphQL

fast_graphql = FastGraphQL()


@fast_graphql.type()
class Model(BaseModel):
    t_int: int
    t_opt_int: Optional[int]
    t_str: str
    t_opt_str: Optional[str]
    t_float: float
    t_opt_float: Optional[float]
    t_datatime: datetime
    t_opt_datatime: Optional[datetime]
    t_boolean: bool
    t_opt_boolean: Optional[bool]


@fast_graphql.input()
class Input(BaseModel):
    t_int: int


print(fast_graphql.render())
```

The above code example generates a schema as follows:

```graphql
scalar DateTime

type Model {
    t_int: Int!
    t_opt_int: Int
    t_str: String!
    t_opt_str: String
    t_float: Float!
    t_opt_float: Float
    t_datatime: DateTime!
    t_opt_datatime: DateTime
    t_boolean: Boolean!
    t_opt_boolean: Boolean
}

input Input {
    t_int: Int!
}
```

## Query and Mutation

Following the same approach with annotation driven defitions, query and mutations can
easily be defined using `FastGraphQL.graphql_query` and `FastGraphQL.mutation`.

Note that all function arguments annotated with `FastGraphQL.graphql_query_field`
are considered to be input arguments for the GraphQL API and simples types and 
**Pydantic** models can be used and arguments and also as return type and they don't 
need to be explicitly annotated.

```python
from fastgraphql import FastGraphQL
from pydantic import BaseModel

fast_graphql = FastGraphQL()


class Model(BaseModel):
    param: str


@fast_graphql.query()
def my_first_query(
        model: Model = fast_graphql.parameter(),
        param: str = fast_graphql.parameter()
) -> str:
    ...

@fast_graphql.mutation()
def my_first_mutation(
        model: Model = fast_graphql.parameter(),
        param: str = fast_graphql.parameter()
) -> str:
    ...


print(fast_graphql.render())

```

The above code example generates a schema as follows:

```graphql
input Model {
    param: String!
}
type Query {
    my_first_query(model: Model!, param: String!): String!
}

type Query {
    my_first_mutation(model: Model!, param: String!): String!
}
```

# Dependecy Injection
Query and Mutation can have dependencies injected using `FastGraphQL.depende(...)` as showed bellow:`

```python
from fastgraphql import FastGraphQL
from pydantic import BaseModel

fast_graphql = FastGraphQL()


class Model(BaseModel):
    param: str


def create_dependency() -> str:
    return ""


@fast_graphql.query()
def my_first_query(
        model: Model = fast_graphql.parameter(),
        dependecy: str = fast_graphql.depends(create_dependency)
) -> str:
    ...

```
In this example the parameter `dependecy` will be injected once the query is called. 

# Integrations

## Ariadne
The developed GraphQL API can be easily integration 
with [Ariadne](https://ariadnegraphql.org).

```shell
pip install fastgraphql[ariadne]
```

The method `make_executable_schema` in the module `fastgraphql.ariadne`
can create the ariadne's executable schema to integrate to other
frameworks like FastAPI. See https://ariadnegraphql.org/docs/starlette-integration

## FastAPI
The developed GraphQL API can be easily served using [Ariadne](https://ariadnegraphql.org).  
and [FastAPI](https://fastapi.tiangolo.com).

```shell
pip install fastgraphql[ariadne,fastapi]
```

_Note that Ariadne is needed to serve GraphQL APIs through FastAPI
because no other GraphQL framework are yet integrated_ 

To create the router that server the GraphQL API, `make_ariadne_fastapi_router`
from the module `fastgraphql.fastapi` should be used. For example:

```python
from fastgraphql import FastGraphQL
from fastapi import FastAPI
from fastgraphql.fastapi import make_ariadne_fastapi_router

app = FastAPI()
fast_graphql = FastGraphQL()

...

app.include_router(
    make_ariadne_fastapi_router(fast_graphql=fast_graphql)
)
    


```


## SQLAlchemy

To integrate SQLAlchemy models to the GraphQL API first all 
dependency for SQLAlchemy should be installed using:

```shell
pip install fastgraphql[sqlalchemy]
```

SQLAlchemy, then, models can be incorporated to the GraphQL API 
by first telling FastGraphQLwhat which is the base class to be 
considered:

```python
from fastgraphql import FastGraphQL
from sqlalchemy.ext.declarative import declarative_base

fast_graphql = FastGraphQL()
...
Base = declarative_base(...)
...

fast_graphql.set_sqlalchemy_base(Base)
```

and after that, any SQLAlchemy model can be using as types and inputs.
The models can also be used as query's and mutation's inputs and outpus. For example:

```python
from fastgraphql import FastGraphQL
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

fast_graphql = FastGraphQL()
...
Base = declarative_base(...)
...
fast_graphql.set_sqlalchemy_base(Base)

@fast_graphql.type()
class MyModel(Base):
    id = Column(Integer, primary_key=True)

@fast_graphql.mutation()
def mutation(input: int) -> MyModel:
    ...

```

# Acknowledgment

Thanks [FastAPI](https://fastapi.tiangolo.com) for inspiration