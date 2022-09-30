import inspect
from datetime import date, datetime, time
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
    Any,
)

from pydantic.fields import ModelField
from pydantic import BaseModel

from fastgraphql.exceptions import GraphQLFactoryException
from fastgraphql.injection import InjectableFunction
from fastgraphql.schema import (
    GraphQLSchema,
    SelfGraphQL,
    SelfGraphQLType,
    SelfGraphQLFunction,
)
from fastgraphql.types import (
    GraphQLDataType,
    GraphQLTypeAttribute,
    GraphQLType,
    GraphQLArray,
    GraphQLFunctionField,
    GraphQLFunction,
)
from fastgraphql.scalars import (
    GraphQLScalar,
    GraphQLBoolean,
    GraphQLInteger,
    GraphQLString,
    GraphQLFloat,
    GraphQLDateTime,
    GraphQLDate,
    GraphQLTime,
)
from fastgraphql.utils import MutableString

T = TypeVar("T", bound=BaseModel)
T_ANY = TypeVar("T_ANY")


class _DateFormats:
    def __init__(
        self, date_format: str, time_format: str, date_time_format: str
    ) -> None:
        self.date_format = MutableString(date_format)
        self.time_format = MutableString(time_format)
        self.date_time_format = MutableString(date_time_format)


class GraphQLTypeFactory:
    """
    GraphQL type factory produces GraphQL definition based on SQLAlchemy and Pydantic models. The definition include
    schemas and input types.
    """

    def __init__(
        self,
        schema: GraphQLSchema,
        date_formats: _DateFormats,
        input_factory: bool = False,
    ) -> None:
        self.schema = schema
        self.input_factory = input_factory
        self.date_formats = date_formats

    def create_graphql_type(
        self,
        python_type: Type[Any],
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Tuple[GraphQLDataType, bool]:

        if get_origin(python_type):
            if (
                get_origin(python_type) == Union
                and Optional[get_args(python_type)[0]] == python_type
            ):
                inner_type, _ = self.create_graphql_type(get_args(python_type)[0])
                return inner_type, True
            if issubclass(cast(type, get_origin(python_type)), Iterable):
                inner_type, nullable = self.create_graphql_type(
                    get_args(python_type)[0]
                )
                return GraphQLArray(inner_type.ref(nullable=nullable)), False

        if issubclass(python_type, BaseModel):
            return (
                self.adapt_pydantic_graphql(
                    python_type=python_type,
                    name=name,
                    exclude_model_attrs=exclude_model_attrs,
                ),
                False,
            )
        if issubclass(python_type, str):
            return GraphQLString(), False
        if issubclass(python_type, bool):
            return GraphQLBoolean(), False
        if issubclass(python_type, int):
            return GraphQLInteger(), False
        if issubclass(python_type, float):
            return GraphQLFloat(), False
        if issubclass(python_type, datetime):
            return GraphQLDateTime(self.date_formats.date_time_format), False
        if issubclass(python_type, time):
            return GraphQLTime(self.date_formats.time_format), False
        if issubclass(python_type, date):
            return GraphQLDate(self.date_formats.date_format), False

        raise GraphQLFactoryException(
            f"Type {python_type.__class__.__name__} is still not implement but pydantic should have caught this error"
        )

    def adapt_pydantic_graphql(
        self,
        python_type: Type[T],
        name: Optional[str] = None,
        exclude_model_attrs: Optional[List[str]] = None,
    ) -> GraphQLDataType:

        if exclude_model_attrs is None:
            exclude_model_attrs = []

        if not name:
            name = str(python_type.__name__)

        if i := SelfGraphQL.introspect(python_type):
            if self.input_factory and (graphql_type := i.as_input):
                return graphql_type
            elif not self.input_factory and (graphql_type := i.as_type):
                return graphql_type

        field: ModelField
        graphql_type = GraphQLType(
            name=name, as_input=self.input_factory, python_type=python_type
        )
        for _, field in python_type.__fields__.items():
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
                and not graphql_attr_type.default_scalar
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

        self.add_graphql_metadata(python_type, graphql_type)
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
            raise GraphQLFactoryException(
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
                func_parameter.set_python_name(param_name)

                if definition.annotation == inspect.Parameter.empty:
                    raise GraphQLFactoryException(
                        f"Method {func.__qualname__} defines a {GraphQLFunctionField.__name__} without type definition."
                    )
                graphql_type, nullable = self.input_factory.create_graphql_type(
                    definition.annotation
                )
                if func_parameter.reference:
                    graphql_type = func_parameter.reference.referenced_type
                if (
                    isinstance(graphql_type, GraphQLScalar)
                    and not graphql_type.default_scalar
                ):
                    self.schema.add_scalar(graphql_type)

                func_parameter.reference = graphql_type.ref(nullable=nullable)
                if isinstance(graphql_type, GraphQLType):
                    func_parameter.python_type = graphql_type.python_type
                if not func_parameter.name:
                    func_parameter.set_name(param_name)
                graphql_query.add_parameter(func_parameter)
            elif isinstance(definition.default, InjectableFunction):
                graphql_query.add_injected_parameter(
                    name=param_name,
                    injectable=self.dependency_injection_factory(definition.default),
                )
        self.add_graphql_metadata(func=func, graphql_function=graphql_query)

        return graphql_query

    def dependency_injection_factory(
        self, injectable_function: InjectableFunction
    ) -> InjectableFunction:
        assert injectable_function.callable
        func_signature = inspect.signature(injectable_function.callable)

        for param_name, definition in func_signature.parameters.items():
            if isinstance(definition.default, InjectableFunction):
                injectable_function.dependencies[
                    param_name
                ] = self.dependency_injection_factory(definition.default)

        return injectable_function

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
