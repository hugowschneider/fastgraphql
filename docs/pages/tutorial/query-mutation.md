# Queries and Mutations

Queries and mutations in GraphQL
are the way any consumer will interact with the
server serving the GraphQL API.

Exposing them using *FastGraphQL* is very straightforward
as we saw in the example in the previous section.

Let us go a little deeper into how to define them.

## Queries and mutation in Python code

**FastGraphQL** handles queries and mutations as python functions
that have type annotations for all its parameters and return type.

!!! note "Can Query act as a mutation?"

    "*Because there is no restriction on what can be done inside resolvers,
    technically there’s nothing stopping somebody from making Queries
    act as mutations, taking inputs and executing state-changing logic.*

    *In practice such queries break the contract with client libraries
    such as Apollo-Client that do client-side caching and state management,
    resulting in non-responsive controls or inaccurate information being
    displayed in the UI as the library displays cached data before redrawing
    it to display an actual response from the GraphQL.*"


    Quote from <a href="https://ariadne.readthedocs.io/en/0.1.0/mutations.html" target="_blank">Ariadne GraphQL.</a>

### Queries

As you have already noticed in the previous chapters, defining queries is as simple
as annotating a python function with `#!python FastGraphQL.query()`. Let's see
again the first tutorial example:

```python title="main.py" linenums="1" hl_lines="9"
--8<-- "tutorial/index/main.py"
```

### Mutation

Similar to queries, mutations are defined by annotating a method with
`#!python FastGraphQL.mutation()`. Let's see an example:

```python title="main.py" linenums="1" hl_lines="9"
--8<-- "tutorial/query-mutation/main.py"
```
