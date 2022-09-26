import inspect
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
    Callable,
)

from pydantic.fields import ModelField
from pydantic import BaseModel

from fastgraphql.exceptions import GraphQLResolverException
from fastgraphql.schema import (
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
    GraphQLFunction,
    GraphQLFunctionField,
    SelfGraphQLType,
    SelfGraphQLFunction,
)

T = TypeVar("T", bound=BaseModel)
T_ANY = TypeVar("T_ANY")


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
            name = str(type_.__name__)

        if i := SelfGraphQL.introspect(type_):
            if self.input_factory and (graphql_type := i.as_input):
                return graphql_type
            elif not self.input_factory and (graphql_type := i.as_type):
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

            if (
                isinstance(graphql_attr_type, GraphQLScalar)
                and not graphql_attr_type._default_scalar
            ):
                self.schema.add_scalar(graphql_attr_type)

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
        self, input_type: Type[T], graphql_type: GraphQLType
    ) -> None:
        if not hasattr(input_type, "__graphql__"):
            setattr(input_type, "__graphql__", SelfGraphQLType())
        if i := SelfGraphQL.introspect(input_type):
            if self.input_factory:
                i.as_input = graphql_type
            else:
                i.as_type = graphql_type


class GraphQLFunctionFactory:
    def __init__(
        self,
        schema: GraphQLSchema,
        type_factory: GraphQLTypeFactory,
        input_factory: GraphQLTypeFactory,
        mutation_factory: bool = False,
    ) -> None:
        self.schema = schema
        self.mutation_factory = mutation_factory
        self.input_factory = input_factory
        self.type_factory = type_factory

    def create_function(
        self, func: Callable[..., T_ANY], name: Optional[str] = None
    ) -> GraphQLFunction:
        if not name:
            name = str(func.__name__)
        func_signature = inspect.signature(func)

        if func_signature.return_annotation == inspect.Parameter.empty:
            raise GraphQLResolverException(
                f"{'Mutation' if self.mutation_factory else 'Query'} {name} implemented in {func.__qualname__} does not have a return type annotation"
            )

        graphql_type, nullable = self.type_factory.create_graphql_type(
            func_signature.return_annotation
        )

        graphql_query = GraphQLFunction(
            name=name, return_type=graphql_type.ref(nullable)
        )

        for param_name, definition in func_signature.parameters.items():
            if isinstance(definition.default, GraphQLFunctionField):
                func_parameter: GraphQLFunctionField = definition.default
                if definition.annotation == inspect.Parameter.empty:
                    raise Exception(
                        f"Method {func.__qualname__} defines a {GraphQLFunctionField.__name__} without type definition."
                    )
                graphql_type, nullable = self.input_factory.create_graphql_type(
                    definition.annotation
                )
                if func_parameter.type:
                    if (
                        isinstance(func_parameter.type, GraphQLScalar)
                        and not func_parameter.type._default_scalar
                    ):
                        self.schema.add_scalar(func_parameter.type)
                    graphql_type = func_parameter.type

                func_parameter.set_type(graphql_type.ref(nullable=nullable))
                if not func_parameter.name:
                    func_parameter.set_name(param_name)
                graphql_query.add_parameter(func_parameter)

        self.add_graphql_metadata(func=func, graphql_function=graphql_query)

        return graphql_query

    def add_graphql_metadata(
        self, func: Callable[..., T_ANY], graphql_function: GraphQLFunction
    ) -> None:
        if not hasattr(func, "__graphql__"):
            setattr(func, "__graphql__", SelfGraphQLFunction())
        if i := SelfGraphQL.introspect(func):
            if self.mutation_factory:
                i.as_mutation = graphql_function
            else:
                i.as_query = graphql_function
