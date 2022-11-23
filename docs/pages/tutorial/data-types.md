# Type System and Python Types

Before we dive deeper on how to use *FastGraphQL* to create and
deploy your GraphQL API, lets look into the supported data types
and how *FastGraphQL* connect python types with GraphQL Type

# Native Python Types

In the following table, you can see types *FastGraphQL* supports
and how this will map to GraphQL Types:

## Primitive Python Types

| Python Type   | GraphQL Scalar |
| --------------|----------------|
| `#!python int`           | `Integer!`      |
| `#!python bool`          | `Boolean!`       |
| `#!python str`           | `String!`        |
| `#!python float`         | `Float!`         |

It is very important to highlight that all types are translated to 
**non-null** GraphQL types. If you would like to have nullable 
types, you should add `#!python Optional[...]` in the 
declaration

| Python Type   | GraphQL Scalar |
| --------------|----------------|
| `#!python Optional[int]`           | `Integer`      |
| `#!python Optional[bool]`          | `Boolean`       |
| `#!python Optional[str]`           | `String`        |
| `#!python Optional[float]`         | `Float`         |

Extracting a more generic rule we can consider it like

| Python Type   | GraphQL Scalar |
| --------------|----------------|
| `#!python T`           | `T!`      |
| `#!python Optional[T]`           | `T`      |

where `T` is any supported type by **FastGraqhQL**

## Lists

Assuming that `T` is any supported type by **FastGraqhQL**, python lists are translated as follows:

| Python Type   | GraphQL Scalar |
| --------------|----------------|
| `#!python List[T]`           | `[T!]!`      |
| `#!python Optional[List[T]]`           | `[T!]`      |
| `#!python List[Optional[T]]`           | `[T]!`      |
| `#!python Optional[List[Optional[T]]]`           | `[T]`      |


## Enums

Unfortunetly, GraphQL Enums are yet not supported. I hope it will change soonish :sweat_smile:.


