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

@fast_graphql.graphql_type()
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

@fast_graphql.graphql_type()
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

type Input {
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

@fast_graphql.graphql_query()
def my_first_query(
        model: Model = fast_graphql.graphql_query_field(),
        param: str = fast_graphql.graphql_query_field()
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
    
@fast_graphql.graphql_query()
def my_first_query(
        model: Model = fast_graphql.graphql_query_field(),
        dependecy: str = fast_graphql.depends(create_dependency)
) -> str:
    ...

```
In this example the parameter `dependecy` will be injected once the query is called. 

# Integrations

## Ariadne
...

## FastAPI
...

# Acknowledgment

Thanks [FastAPI](https://fastapi.tiangolo.com) for inpirations