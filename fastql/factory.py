from datetime import date
from typing import (
    Iterable,
    List,
    Type,
    TypeVar,
    Optional,
    Union,
    Tuple,
    get_origin,
    get_args,
    cast,
)

from pydantic.fields import ModelField
from pydantic import BaseModel

from fastql.schema import (
    GraphQLDataType,
    GraphQLArray,
    GraphQLString,
    GraphQLBoolean,
    GraphQLInteger,
    GraphQLFloat,
    GraphQLScalar,
    GraphQLType,
    GraphQLTypeAttribute,
    GraphQLSchema,
    SelfGraphQL,
)

T = TypeVar("T", bound=BaseModel)


class GraphQLTypeFactory:
    """
    GraphQL type factory produces GraphQL definition based on SQLAlchemy and Pydantic models. The definition include
    schemas and input types.
    """

    def __init__(self, schema: GraphQLSchema, input_factory: bool = False) -> None:
        self.schema = schema
        self.input_factory = input_factory

    def create_graphql_type(
        self,
        type_: Type[T],
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Tuple[GraphQLDataType, bool]:

        if get_origin(type_):
            if get_origin(type_) == Union and Optional[get_args(type_)[0]] == type_:
                inner_type, _ = self.create_graphql_type(get_args(type_)[0])
                return inner_type, True
            if issubclass(cast(type, get_origin(type_)), Iterable):
                inner_type, nullable = self.create_graphql_type(get_args(type_)[0])
                return GraphQLArray(inner_type.ref(nullable=nullable)), False

        if issubclass(type_, BaseModel):
            return (
                self.adapt_pydantic_graphql(
                    type_=type_,
                    name=name,
                    exclude_model_attrs=exclude_model_attrs,
                ),
                False,
            )
        if issubclass(type_, str):
            return GraphQLString(), False
        if issubclass(type_, bool):
            return GraphQLBoolean(), False
        if issubclass(type_, int):
            return GraphQLInteger(), False
        if issubclass(type_, float):
            return GraphQLFloat(), False
        if issubclass(type_, date):
            scalar = GraphQLScalar("Date")
            self.schema.add_scalar(scalar)
            return scalar, False

        raise RuntimeError(  # pragma: no cover
            f"Type {type_.__class__.__name__} is still not implement but pydantic should have caught this error"
        )

    def adapt_pydantic_graphql(
        self,
        type_: Type[T],
        name: Optional[str] = None,
        exclude_model_attrs: Optional[List[str]] = None,
    ) -> GraphQLDataType:

        if exclude_model_attrs is None:
            exclude_model_attrs = []

        if not name:
            name = self.render_name(type_)

        if i := SelfGraphQL.introspect(type_):
            if self.input_factory and (graphql_type := i.as_input):
                return graphql_type
            elif graphql_type := i.as_type:
                return graphql_type

        field: ModelField
        graphql_type = GraphQLType(name=name, as_input=self.input_factory)
        for _, field in type_.__fields__.items():
            if field.name in exclude_model_attrs:
                continue
            if "graphql_scalar" in field.field_info.extra:
                graphql_attr_type, nullable = (
                    field.field_info.extra["graphql_scalar"],
                    field.allow_none,
                )
            else:
                graphql_attr_type, nullable = self.create_graphql_type(field.annotation)

            graphql_type.add_attribute(
                GraphQLTypeAttribute(
                    name=field.name,
                    attr_type=graphql_attr_type.ref(
                        nullable=field.allow_none or nullable
                    ),
                )
            )

        self.add_graphql_metadata(type_, graphql_type)
        if self.input_factory:
            self.schema.add_input_type(graphql_type=graphql_type)
        else:
            self.schema.add_type(graphql_type=graphql_type)
        return graphql_type

    def add_graphql_metadata(
        self, input_type: Type[T], graphql_type: GraphQLDataType
    ) -> None:
        if not hasattr(input_type, "__graphql__"):
            setattr(input_type, "__graphql__", SelfGraphQL())
        if i := SelfGraphQL.introspect(input_type):
            if self.input_factory:
                i.as_input = graphql_type
            else:
                i.as_type = graphql_type

    def render_name(self, type_: Type[T]) -> str:
        return str(type_.__name__)
