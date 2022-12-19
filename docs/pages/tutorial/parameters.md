# Parameters

Of course, we expect that queries and mutation should
accept parameters, and of course, **FastGraphQL** gives
us an easy way to deal with them.

Putting semantics aside, **FastGraphQL
handles queries and mutations in the exact same way**
and everything we need to ensure that **all parameters
and return values have type hints**


## Heads Up!

To simplify documentation, remember that both method signatures,
`#!python FastGraphQL.query()` and `#!python FastGraphQL.mutation()`,
have the same signature and therefore we will use only
`#!python FastGraphQL.query()` in the next examples.
