# Getting Started

In this section we will get started and build our first GraphQL API using **FastGraphQL**.

# Running your application

In this tutorial we will use two integrated components to create our GraphQL API, those are [FastAPI](https://fastapi.tiangolo.com/) and [Ariadne](https://ariadnegraphql.org). 

We will use [uvicorn](https://www.uvicorn.org) to run the application:

```shell
$ uvicorn main:app --reload
```

# My First GraphQL API

Lets create a file:

```python title="main.py" linenums="1" 
--8<-- "tutorial/index/main.py"
```

In the same folder run:

```shell
$ uvicorn main:app --reload
```

!!! note "Running uvicorn"

    * `main` refers to the modeule main defined with `main.py`
    * `app` refers to the FastAPI application variable defined in `main.py`
    * `--reload` monitors changes and reload the application

## Check it

Open your browser at [http://localhost:8000/graphql](http://localhost:8000/graphql).

Doing that you will see the [GraphQL Playground](https://github.com/graphql/graphql-playground) where you can explore your GraphQL API.

## Dissecting the code

### Step 1: Importing

```python title="main.py" linenums="1" hl_lines="2"
--8<-- "tutorial/index/main.py"
```

`#!python FastGraphQL` is a class which is the base for all GraphQL definition and for management of the API calls.
Its instance and methods should be starting point of defining your GraphQL API.

### Step 2: Instanciating

```python title="main.py" linenums="1" hl_lines="6"
--8<-- "tutorial/index/main.py"
```
`#!python fast_graphql = FastGraphQL()` is where everything start. The varible `#!python fast_graphql` will be used
across the code define the complete GraphQLAPI

!!! note "Customizations"
    The class initializer allows customizations to the complete GraphQL Schema generation. This will be covered in [Global Customizations](license.md)

!!! note "Naming"
    The variable name `#!python fast_graphql` was selected to reflect the class `#!python FastGraphQL`, but it could
    have any select name. 
    
    If you choose a different name remember to rename the reference in the annotation covered in 
    the next section and everything will work as described in this documentation.

    Choose variable names wisely.


### Step 3: The First Query

```python title="main.py" linenums="1" hl_lines="9-10"
--8<-- "tutorial/index/main.py"
```
This section of the code is the most interesting part to understand at this point. Lets look into it in all details.

#### Annotating

Annotating a method with `#!python @fast_graphql.query()` will tell **FastGraphQL** that this method should be
handled as a resolver for a query. The query name will be exactly the same as the method, in this case `hello`.

!!! note "Customizations"
    This method allows local customizations to the query schema generation. This will be covered in the [Local Customizations](license.md)

#### Method signature

The most import python feature *FastGraphQL* uses, is type hinting and everything is based on that. Having said that,
the method signature `#!python def hello() -> str:` is able to tell all necessary infomations to *FastGraphQL*, which in
this case are:

1. method name: `hello`
1. return type: `str`

!!! note "Type Hints"
    FastGraphQL is implemented under the assumption all definitions, including methods, parameters and class attributes,
    have type hints annotations. More details to this can be found under [Types](license.md)

### Step 3: Exposing the Schema

```python title="main.py" linenums="1" hl_lines="3 14"
--8<-- "tutorial/index/main.py"
```

app.include_router(make_ariadne_fastapi_router(fast_graphql=fast_graphql))

Lets tear this lines appart:

* `#!python from fastgraphql.fastapi import make_ariadne_fastapi_router` is importing from the FastAPI integration inside FastGraphQL, the 
method we will use to expose our implementation as a GraphQL API.
* `#!python app.include_router(...)` this is part of the FastAPI API and it includer a router 
returned by `#!python make_ariadne_fastapi_router(...)`. See [FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-the-apirouters-for-users-and-items) for more details to this method
* `#!python make_ariadne_fastapi_router(...)` is part of FastAPI and Ariadne integrations. It generates an executable
schema using Ariadne's API and returns a FastAPI router to expose the GraphQL API using the FastAPI application `#!python app`.

## GraphQL Schema

If you would include this line in the file

```python title="main.py" linenums="1" hl_lines="16"
--8<-- "tutorial/index/main.py"

print(fast_graphql.render())
```

and simple run with

```sh
python main.py
```

you will be able to inspect the generated GraphQL schema. 

```gql
type Query {
    hello: String!
}
```
a very simple schema so far :smile:.