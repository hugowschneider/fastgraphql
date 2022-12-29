# Type System and Python Types

Before we dive deeper into how to use *FastGraphQL* to create and
deploy your GraphQL API, it is important to look into the
supported data types and how *FastGraphQL* connects python
types with GraphQL Types.

Starting from the very beginning, let us look together into
native python types.

## Primitive Python Types

All primitive types are translated to GraphQL Scalar as displayed
below

| Python Type   | GraphQL Scalar |
| --------------|----------------|
| `#!python int`           | `Integer!`      |
| `#!python bool`          | `Boolean!`       |
| `#!python str`           | `String!`        |
| `#!python float`         | `Float!`         |

Note that all types are translated to
**non-null** GraphQL types. If you would like to have nullable
types, you should add `#!python Optional[...]` in the
declaration, as shown:

| Python Type   | GraphQL Scalar |
| --------------|----------------|
| `#!python Optional[int]`           | `Integer`      |
| `#!python Optional[bool]`          | `Boolean`       |
| `#!python Optional[str]`           | `String`        |
| `#!python Optional[float]`         | `Float`         |

Extracting a more generic rule we can consider that:

| Python Type   | GraphQL Type |
| --------------|----------------|
| `#!python T`           | `T!`      |
| `#!python Optional[T]`           | `T`      |

for any `T` being a supported type by **FastGraqhQL**

## Lists

Assuming that `T` is any supported type, python lists are translated as follows:

| Python Type   | GraphQL Type |
| --------------|----------------|
| `#!python List[T]`           | `[T!]!`      |
| `#!python Optional[List[T]]`           | `[T!]`      |
| `#!python List[Optional[T]]`           | `[T]!`      |
| `#!python Optional[List[Optional[T]]]`           | `[T]`      |


## Dates, Times and Date-Times

**FastGraphQL** provides three custom GraphQL scalars with respective encoders and
decoders to support date, time and date-time types.

| Python Type   | GraphQL Scalar | Default Format |
| --------------|----------------|----------------|
| `#!python datetime.time`           | `Time`      | `%H:%M:%S` |
| `#!python datetime.date`           | `Date`      |`%Y-%m-%d`|
| `#!python datetime.datetime`       | `DateTime`      |`%H:%M:%ST%Y-%m-%d%z`|

!!! Note "Date and Time format string"
    For all details about format strings please refer to
    <a href="https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes" target="_blank">strftime() and strptime() Format Codes</a>

!!! Note "Date and Time format customization"
    The default format string can be customized. The details about it you
    can find under [Global Customizations](license.md)


## Enums

Unfortunately, GraphQL Enums are yet not supported. I hope it will change soonish :sweat_smile:.


