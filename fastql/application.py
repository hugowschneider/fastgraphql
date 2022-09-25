import inspect
import logging

from fastql.factory import GraphQLTypeFactory

from typing import (
    Type,
    TypeVar,
    Optional,
    Union,
    Callable,
    List,
)
from pydantic import BaseModel

from fastql.schema import GraphQLType, GraphQLSchema, SelfGraphQL

T = TypeVar("T", bound=BaseModel)


class FastQL:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.schema = GraphQLSchema()

    def render(self) -> str:
        return self.schema.render()

    def graphql_model(
        self,
        type_: Optional[Type[T]] = None,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Union[Callable[..., Type[T]], Type[T]]:
        if exclude_model_attrs is None:
            exclude_model_attrs = []

        def decorator(type_: Type[T]) -> Type[T]:

            self.logger.info(f"Constructing GraphQL type for {type_.__qualname__}")
            factory = GraphQLTypeFactory(schema=self.schema)
            graphql_type, _ = factory.create_graphql_type(
                type_=type_,
                name=name,
                exclude_model_attrs=exclude_model_attrs,
            )
            if not isinstance(graphql_type, GraphQLType):  # pragma: no cover
                raise Exception("Something went wrong")

            return type_

        if (t := type_) and inspect.isclass(t):
            return decorator(t)
        else:
            return decorator

    def graphql_input(
        self,
        type_: Optional[Type[T]] = None,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Union[Callable[..., Type[T]], Type[T]]:
        if exclude_model_attrs is None:
            exclude_model_attrs = []

        def decorator(type_: Type[T]) -> Type[T]:

            self.logger.info(f"Constructing GraphQL type for {type_.__qualname__}")
            factory = GraphQLTypeFactory(schema=self.schema, input_factory=True)
            graphql_type, _ = factory.create_graphql_type(
                type_=type_,
                name=name,
                exclude_model_attrs=exclude_model_attrs,
            )
            if not isinstance(graphql_type, GraphQLType):  # pragma: no cover
                raise Exception("Something went wrong")

            return type_

        if (t := type_) and inspect.isclass(t):
            return decorator(t)
        else:
            return decorator
