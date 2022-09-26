import logging

from fastgraphql.factory import GraphQLTypeFactory, GraphQLFunctionFactory

from typing import (
    Type,
    TypeVar,
    Optional,
    Callable,
    List,
    Any,
)
from pydantic import BaseModel

from fastgraphql.schema import (
    GraphQLSchema,
    GraphQLType,
    GraphQLFunction,
    GraphQLQueryField,
    GraphQLScalar,
)

T = TypeVar("T", bound=BaseModel)
T_ANY = TypeVar("T_ANY")


class FastGraphQL:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.schema = GraphQLSchema()
        self.type_factory = GraphQLTypeFactory(schema=self.schema, input_factory=False)
        self.input_factory = GraphQLTypeFactory(schema=self.schema, input_factory=True)
        self.query_factory = GraphQLFunctionFactory(
            schema=self.schema,
            mutation_factory=False,
            input_factory=self.input_factory,
            type_factory=self.type_factory,
        )
        self.mutation_factory = GraphQLFunctionFactory(
            schema=self.schema,
            mutation_factory=True,
            input_factory=self.input_factory,
            type_factory=self.type_factory,
        )

    def render(self) -> str:
        return self.schema.render()

    def _graphql_model(
        self,
        exclude_model_attrs: Optional[List[str]],
        name: Optional[str],
        as_input: bool,
    ) -> Callable[..., Type[T]]:
        if exclude_model_attrs is None:
            exclude_model_attrs = []

        def decorator(type_: Type[T]) -> Type[T]:
            self.logger.info(
                f"Constructing GraphQL {'input' if as_input else 'type'} for {type_.__qualname__}"
            )
            if as_input:
                factory = self.input_factory
            else:
                factory = self.type_factory

            graphql_type, _ = factory.create_graphql_type(
                type_=type_,
                name=name,
                exclude_model_attrs=exclude_model_attrs,
            )
            if not isinstance(graphql_type, GraphQLType):  # pragma: no cover
                raise Exception("Something went wrong")

            return type_

        return decorator

    def graphql_type(
        self,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Callable[..., Type[T]]:
        return self._graphql_model(
            exclude_model_attrs=exclude_model_attrs, name=name, as_input=False
        )

    def graphql_input(
        self,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Callable[..., Type[T]]:
        return self._graphql_model(
            exclude_model_attrs=exclude_model_attrs, name=name, as_input=True
        )

    def graphql_query(
        self,
        name: Optional[str] = None,
    ) -> Callable[..., Callable[..., Type[T_ANY]]]:
        return self._graphql_function(name=name, as_mutation=False)

    def graphql_mutation(
        self,
        name: Optional[str] = None,
    ) -> Callable[..., Callable[..., Type[T_ANY]]]:
        return self._graphql_function(name=name, as_mutation=True)

    def _graphql_function(
        self,
        name: Optional[str],
        as_mutation: bool,
    ) -> Callable[..., Callable[..., Type[T_ANY]]]:
        def decorator(func: Callable[..., Type[T_ANY]]) -> Callable[..., Type[T_ANY]]:
            self.logger.info(
                f"Constructing GraphQL {'input' if False else 'query'} for {func.__qualname__}"
            )
            if as_mutation:
                graphql_type = self.mutation_factory.create_function(
                    func=func, name=name
                )
                self.schema.add_mutation(graphql_type)
            else:
                graphql_type = self.query_factory.create_function(func=func, name=name)
                self.schema.add_query(graphql_type)

            if not isinstance(graphql_type, GraphQLFunction):  # pragma: no cover
                raise Exception("Something went wrong")

            return func

        return decorator

    def graphql_query_field(
        self, name: Optional[str] = None, graphql_scalar: Optional[GraphQLScalar] = None
    ) -> Any:
        return GraphQLQueryField(name=name, type_=graphql_scalar)
