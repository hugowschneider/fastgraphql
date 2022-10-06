import inspect
from datetime import date, datetime, time
from inspect import Parameter
from typing import (
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
from fastgraphql.utils import MutableString, DefaultNames, DefaultUnchanged

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
        default_names: Optional[DefaultNames],
        input_factory: bool = False,
    ) -> None:
        self.schema = schema
        self.default_names = default_names
        self.input_factory = input_factory
        self.date_formats = date_formats
        self.sqlalchemy_base: Optional[Type[Any]] = None

    def handle_generic_types(
        self, python_type: Type[Any]
    ) -> Tuple[GraphQLDataType, bool]:
        if (
            get_origin(python_type) == Union
            and Optional[get_args(python_type)[0]] == python_type
        ):
            inner_type, _ = self.create_graphql_type(get_args(python_type)[0])
            return inner_type, True
        if issubclass(cast(type, get_origin(python_type)), List):
            inner_type, nullable = self.create_graphql_type(get_args(python_type)[0])
            return GraphQLArray(inner_type.ref(nullable=nullable)), False

        raise GraphQLFactoryException(
            f"Generic type {python_type.__class__} is still not implemented. Only supported types are Optional and List"
        )

    def create_graphql_type(
        self,
        python_type: Type[Any],
        default_names: Optional[DefaultNames] = None,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Tuple[GraphQLDataType, bool]:

        if get_origin(python_type):
            return self.handle_generic_types(python_type=python_type)
        if issubclass(python_type, BaseModel):
            return (
                self.adapt_pydantic_graphql(
                    python_type=python_type,
                    name=name,
                    exclude_model_attrs=exclude_model_attrs,
                    default_names=default_names,
                ),
                False,
            )

        if (base := self.sqlalchemy_base) and issubclass(python_type, base):
            return self.handle_sqlalchemy_type(
                python_type=python_type,
                name=name,
                exclude_model_attrs=exclude_model_attrs,
                default_names=next(
                    (
                        d
                        for d in [default_names, self.default_names, DefaultUnchanged()]
                        if d is not None
                    )
                ),
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

    def handle_sqlalchemy_type(
        self,
        python_type: Type[T],
        name: Optional[str],
        exclude_model_attrs: Optional[List[str]],
        default_names: DefaultNames,
    ) -> Tuple[GraphQLDataType, bool]:
        from fastgraphql.sqlalchemy import adapt_sqlalchemy_graphql

        def parse_function(
            python_type_: Type[Any],
            exclude_model_attrs_: Optional[List[str]] = None,
            name_: Optional[str] = None,
        ) -> Tuple[GraphQLDataType, bool]:
            return self.create_graphql_type(
                python_type=python_type_,
                exclude_model_attrs=exclude_model_attrs_,
                name=name_,
            )

        return (
            adapt_sqlalchemy_graphql(
                python_type=python_type,
                name=name,
                schema=self.schema,
                exclude_model_attrs=exclude_model_attrs,
                parse_type_func=parse_function,
                as_input=self.input_factory,
                default_names=default_names,
            ),
            False,
        )

    def adapt_pydantic_graphql(
        self,
        python_type: Type[T],
        name: Optional[str] = None,
        exclude_model_attrs: Optional[List[str]] = None,
        default_names: Optional[DefaultNames] = None,
    ) -> GraphQLDataType:

        defaults = next(
            (
                d
                for d in [default_names, self.default_names, DefaultUnchanged()]
                if d is not None
            )
        )

        if exclude_model_attrs is None:
            exclude_model_attrs = []

        if not name:
            name = defaults(python_type.__name__)

        if i := SelfGraphQL.introspect(python_type):
            if self.input_factory and (graphql_input := i.as_input):
                return graphql_input
            elif not self.input_factory and (graphql_type := i.as_type):
                return graphql_type

        field: ModelField
        graphql_type = GraphQLType(
            name=name, as_input=self.input_factory, python_type=python_type
        )
        for _, field in python_type.__fields__.items():
            if field.name in exclude_model_attrs:
                continue
            graphql_attr_type, nullable = self.model_field_factory(field)

            if "graphql_name" in field.field_info.extra:
                field_name = field.field_info.extra["graphql_name"]
            else:
                field_name = defaults(field.name)

            graphql_type.add_attribute(
                GraphQLTypeAttribute(
                    graphql_name=field_name,
                    python_name=field.name,
                    attr_type=graphql_attr_type.ref(
                        nullable=field.allow_none or nullable
                    ),
                )
            )

        SelfGraphQL.add_type_metadata(
            python_type=python_type,
            graphql_type=graphql_type,
            as_input=self.input_factory,
        )
        if self.input_factory:
            self.schema.add_input_type(graphql_type=graphql_type)
        else:
            self.schema.add_type(graphql_type=graphql_type)
        return graphql_type

    def model_field_factory(self, field: ModelField) -> Tuple[GraphQLDataType, bool]:
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

        return graphql_attr_type, nullable


class GraphQLFunctionFactory:
    def __init__(
        self,
        schema: GraphQLSchema,
        type_factory: GraphQLTypeFactory,
        input_factory: GraphQLTypeFactory,
        default_names: Optional[DefaultNames],
        mutation_factory: bool = False,
    ) -> None:
        self.schema = schema
        self.default_names = default_names
        self.mutation_factory = mutation_factory
        self.input_factory = input_factory
        self.type_factory = type_factory

    def create_function(
        self,
        func: Callable[..., T_ANY],
        name: Optional[str] = None,
        default_names: Optional[DefaultNames] = None,
    ) -> GraphQLFunction:

        defaults = next(
            (
                d
                for d in [default_names, self.default_names, DefaultUnchanged()]
                if d is not None
            )
        )

        if not name:
            name = defaults(func.__name__)
        func_signature = inspect.signature(func)

        if func_signature.return_annotation == inspect.Parameter.empty:
            raise GraphQLFactoryException(
                f"{'Mutation' if self.mutation_factory else 'Query'} {name} implemented in {func.__qualname__}"
                f" does not have a return type annotation"
            )

        graphql_type, nullable = self.type_factory.create_graphql_type(
            func_signature.return_annotation
        )

        graphql_query = GraphQLFunction(
            name=name, return_type=graphql_type.ref(nullable)
        )

        for param_name, definition in func_signature.parameters.items():
            if isinstance(definition.default, GraphQLFunctionField):
                graphql_query.add_parameter(
                    self.parameter_factory(definition, func, param_name, defaults)
                )
            elif isinstance(definition.default, InjectableFunction):
                graphql_query.add_injected_parameter(
                    name=param_name,
                    injectable=self.dependency_injection_factory(definition.default),
                )
        SelfGraphQL.add_funtion_metadata(
            func=func, graphql_function=graphql_query, as_mutation=self.mutation_factory
        )

        return graphql_query

    def parameter_factory(
        self,
        definition: Parameter,
        func: Callable[..., Any],
        param_name: str,
        defaults: DefaultNames,
    ) -> GraphQLFunctionField:
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
        if isinstance(graphql_type, GraphQLScalar) and not graphql_type.default_scalar:
            self.schema.add_scalar(graphql_type)
        func_parameter.reference = graphql_type.ref(nullable=nullable)
        if isinstance(graphql_type, GraphQLType):
            func_parameter.python_type = graphql_type.python_type
        if not func_parameter.name:
            func_parameter.set_name(defaults(param_name))
        return func_parameter

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
