# FastGraphQL
![FastGraphQL](docs/pages/assets/logo_text.svg)
<p style="text-align: center;">FastGraphQL is a tool for creating code-driven GraphQL APIs.</p>

----------

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

-------
Documentation: <a href="https://hugowschneider.github.io/fastgraphql" target="_blank">https://hugowschneider.github.io/fastgraphql</a>

Source Code: <a href="https://github.com/hugowschneider/fastgraphql" target="_blank">https://github.com/hugowschneider/fastgraphql</a>

# Disclaimer

*This is still a work in progress and all support is welcomed*

# Motivation

So far most of the projects that use GraphQL need to duplicate
many definitions to be able to have a consistent GraphQL API schema
alongside well-defined models that governs the development and the application.

FastGraphQL proposes to shortcut the path between python models and GraphQL schema
using **Pydantic** models. This ensures not only a single source of truth when comes to
type, input, query and mutation definitions, but also the
ability to use **Pydantic** to features on models and inputs.

# Installation

```shell
$ pip install "fastgraphql[all]"
```
You will also need an ASGI server as well to serve your API

```shell
$ pip install "uvicorn[standard]"
```

# Usage

The very first Hello Work example.

```python
from fastapi import FastAPI
from fastgraphql import FastGraphQL
from fastgraphql.fastapi import make_ariadne_fastapi_router

app = FastAPI()
fast_graphql = FastGraphQL()


@fast_graphql.query()
def hello() -> str:
    return "Hello FastGraphQL!!!"


app.include_router(make_ariadne_fastapi_router(fast_graphql=fast_graphql))

```

```shell
$ uvicorn main:app --reload
```

A simple example will not show you the all **FastGraphQL** capabilities, but it
shows how simple this can be.

# Learn

To start your journey into **FastGraphQL**, please refer to [Getting Started](https://hugowschneider.github.io/fastgraphql/tutorial/).

You can find the API documentation [here](https://hugowschneider.github.io/fastgraphql/api/fastgraphql/).

# Integration

FastGraphQL generates independently of any integration a data structure containing all GraphQL definitions and resolvers, which
generates a GraphQL schema.

With that said, all integration will add functionalities and provide
easy and alternative deployments of the defined API.

You can find out more about the different integrations under [Integrations](https://hugowschneider.github.io//fastgraphql/under-construction/)

# Acknowledgment

Thanks to [FastAPI](https://fastapi.tiangolo.com) for the inspiration!
