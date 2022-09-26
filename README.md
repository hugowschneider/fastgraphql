# FastGraphQL
FastGraphQL is intended to help developer create code driven GraphQL APIs.

# Disclaimer

*This is still a work in progress*

# Installation

```commandline
pip install fastgraphql
```


# Usage

Using annotation driven definitions and **Pydantic**, defining GraphQL types is done
by simple annotating **Pydantic** models with `FastGraphQL.graphql_type()`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastgraphql import FastGraphQL

fast_graphql = FastGraphQL()

@fast_graphql.graphql_type()
class TypeWithoutReferences(BaseModel):
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

print(fast_graphql.render())
```

The above code example generates a schema as follows:

```graphql
scalar Date

type TypeWithoutReferences {
    t_int: Int!
    t_opt_int: Int
    t_str: String!
    t_opt_str: String
    t_float: Float!
    t_opt_float: Float
    t_datatime: Date!
    t_opt_datatime: Date
    t_boolean: Boolean!
    t_opt_boolean: Boolean
}
```