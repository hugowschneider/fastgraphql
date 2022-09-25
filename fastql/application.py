import logging

from fastql.factory import GraphQLTypeFactory

from typing import (
    Type,
    TypeVar,
    Optional,
    Callable,
    List,
)
from pydantic import BaseModel

from fastql.schema import GraphQLSchema, GraphQLType

T = TypeVar("T", bound=BaseModel)


class FastQL:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.schema = GraphQLSchema()

    def render(self) -> str:
        return self.schema.render()

    def graphql_model(
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
            factory = GraphQLTypeFactory(schema=self.schema, input_factory=as_input)
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
        return self.graphql_model(
            exclude_model_attrs=exclude_model_attrs, name=name, as_input=False
        )

    def graphql_input(
        self,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Callable[..., Type[T]]:
        return self.graphql_model(
            exclude_model_attrs=exclude_model_attrs, name=name, as_input=True
        )
