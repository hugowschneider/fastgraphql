import inspect

from datetime import date, datetime, time
from inspect import Parameter
from typing import (
    Any,
    Callable,
    Dict,
    ForwardRef,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
)

from pydantic import BaseModel
from pydantic.fields import ModelField

from fastgraphql.context import AdaptContext
from fastgraphql.exceptions import GraphQLFactoryException
from fastgraphql.injection import Injectable, InjectableFunction
from fastgraphql.scalars import (
    GraphQLBoolean,
    GraphQLDate,
    GraphQLDateTime,
    GraphQLFloat,
    GraphQLInteger,
    GraphQLScalar,
    GraphQLString,
    GraphQLTime,
)
from fastgraphql.schema import GraphQLSchema, SelfGraphQL
from fastgraphql.types import (
    GraphQLArray,
    GraphQLDataType,
    GraphQLDelayedType,
    GraphQLFunction,
    GraphQLFunctionField,
    GraphQLType,
    GraphQLTypeAttribute,
)
from fastgraphql.utils import DefaultCase, DefaultUnchanged, MutableString

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
    GraphQL type factory produces GraphQL definition based on SQLAlchemy and
    Pydantic models. The definition include schemas and input types.
    """

    def __init__(
        self,
        schema: GraphQLSchema,
        date_formats: _DateFormats,
        default_case: Optional[DefaultCase],
        input_factory: bool = False,
    ) -> None:
        self.schema = schema
        self.default_case = default_case
        self.input_factory = input_factory
        self.date_formats = date_formats
        self.sqlalchemy_base: Optional[Type[Any]] = None
        self.delayed_definitions: Dict[str, List[AdaptContext]] = {}

    def handle_generic_types(
        self,
        python_type: Type[Any],
        context: Optional[AdaptContext],
    ) -> Tuple[GraphQLDataType, bool]:
        if (
            get_origin(python_type) == Union
            and Optional[get_args(python_type)[0]] == python_type
        ):
            inner_type, _ = self.create_graphql_type(
                get_args(python_type)[0], context=context
            )
            return inner_type, True
        if issubclass(cast(type, get_origin(python_type)), List):
            inner_type, nullable = self.create_graphql_type(
                get_args(python_type)[0],
                context=context.list_context() if context else None,
            )
            return GraphQLArray(inner_type.ref(nullable=nullable)), False

        raise GraphQLFactoryException(
            f"Generic type {python_type.__class__} is still"
            "not implemented. Only supported types are Optional and List"
        )

    def delay_definition(self, type_name: str, context: AdaptContext) -> None:
        if type_name not in self.delayed_definitions:
            self.delayed_definitions[type_name] = []
        self.delayed_definitions[type_name].append(context)

    def create_graphql_type(
        self,
        python_type: Type[Any],
        context: Optional[AdaptContext],
        default_case: Optional[DefaultCase] = None,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Tuple[GraphQLDataType, bool]:

        if isinstance(python_type, ForwardRef):
            if python_type.__forward_evaluated__:
                python_type = python_type.__forward_value__
            else:
                self.delay_definition(python_type.__forward_arg__, context)
                return GraphQLDelayedType(python_type), False

        if get_origin(python_type):
            return self.handle_generic_types(python_type=python_type, context=context)
        if issubclass(python_type, BaseModel):
            return (
                self.adapt_pydantic_graphql(
                    python_type=python_type,
                    name=name,
                    context=context,
                    exclude_model_attrs=exclude_model_attrs,
                    default_case=default_case,
                ),
                False,
            )

        if (base := self.sqlalchemy_base) and issubclass(python_type, base):
            return self.handle_sqlalchemy_type(
                python_type=python_type,
                name=name,
                context=context,
                exclude_model_attrs=exclude_model_attrs,
                default_case=next(
                    (
                        d
                        for d in [default_case, self.default_case, DefaultUnchanged()]
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
            f"Type {python_type.__class__.__name__} is"
            "still not implement but pydantic should have caught this error"
        )

    def handle_sqlalchemy_type(
        self,
        python_type: Type[T],
        name: Optional[str],
        exclude_model_attrs: Optional[List[str]],
        default_case: DefaultCase,
        context: Optional[AdaptContext],
    ) -> Tuple[GraphQLDataType, bool]:
        from fastgraphql.sqlalchemy import adapt_sqlalchemy_graphql

        def parse_function(
            python_type_: Type[Any],
            exclude_model_attrs_: Optional[List[str]],
            name_: Optional[str],
            context_: Optional[AdaptContext],
        ) -> Tuple[GraphQLDataType, bool]:
            return self.create_graphql_type(
                python_type=python_type_,
                exclude_model_attrs=exclude_model_attrs_,
                name=name_,
                context=context_,
            )

        return (
            adapt_sqlalchemy_graphql(
                python_type=python_type,
                name=name,
                schema=self.schema,
                context=context,
                exclude_model_attrs=exclude_model_attrs,
                parse_type_func=parse_function,
                as_input=self.input_factory,
                default_case=default_case,
            ),
            False,
        )

    def adapt_pydantic_graphql(
        self,
        python_type: Type[T],
        context: Optional[AdaptContext],
        name: Optional[str] = None,
        exclude_model_attrs: Optional[List[str]] = None,
        default_case: Optional[DefaultCase] = None,
    ) -> GraphQLDataType:

        defaults = next(
            (
                d
                for d in [default_case, self.default_case, DefaultUnchanged()]
                if d is not None
            )
        )

        if exclude_model_attrs is None:
            exclude_model_attrs = []

        if not name:
            name = defaults(python_type.__name__)

        if graphql_type := SelfGraphQL.check_if_exists(
            python_type=python_type, as_input=self.input_factory
        ):
            return graphql_type

        field: ModelField
        graphql_type = GraphQLType(
            name=name, as_input=self.input_factory, python_type=python_type
        )

        SelfGraphQL.add_type_metadata(
            python_type=python_type,
            graphql_type=graphql_type,
            as_input=self.input_factory,
        )

        for _, field in python_type.__fields__.items():
            if field.name in exclude_model_attrs:
                continue

            if "graphql_name" in field.field_info.extra:
                field_name = field.field_info.extra["graphql_name"]
            else:
                field_name = defaults(field.name)

            graphql_attr_type, nullable = self.model_field_factory(
                field,
                AdaptContext(
                    parent_context=context,
                    graphql_field=field_name,
                    python_field=field.name,
                    graphql_type=graphql_type,
                ),
            )

            graphql_type.add_attribute(
                GraphQLTypeAttribute(
                    graphql_name=field_name,
                    python_name=field.name,
                    type_reference=graphql_attr_type.ref(
                        nullable=field.allow_none or nullable
                    ),
                )
            )

        self.resolve_delayed_types(python_type=python_type, graphql_type=graphql_type)

        if self.input_factory:
            self.schema.add_input_type(graphql_type=graphql_type)
        else:
            self.schema.add_type(graphql_type=graphql_type)

        return graphql_type

    def resolve_delayed_types(
        self, python_type: Type[T], graphql_type: GraphQLType
    ) -> None:
        if python_type.__name__ in self.delayed_definitions:
            for context_ in self.delayed_definitions[python_type.__name__]:
                delayed_attr = context_.graphql_type.attrs[context_.graphql_field]
                if context_.in_list:
                    array_type = delayed_attr.type_reference.referenced_type
                    assert isinstance(array_type, GraphQLArray)
                    attr_type = GraphQLArray(
                        graphql_type.ref(array_type.item_type.nullable)
                    ).ref(delayed_attr.type_reference.nullable)
                else:
                    attr_type = graphql_type.ref(delayed_attr.type_reference.nullable)
                context_.graphql_type.attrs[
                    context_.graphql_field
                ] = GraphQLTypeAttribute(
                    graphql_name=context_.graphql_field,
                    python_name=context_.python_field,
                    type_reference=attr_type,
                )

            del self.delayed_definitions[python_type.__name__]

    def model_field_factory(
        self, field: ModelField, context: AdaptContext
    ) -> Tuple[GraphQLDataType, bool]:
        if "graphql_type" in field.field_info.extra:
            graphql_attr_type, nullable = (
                field.field_info.extra["graphql_type"],
                field.allow_none,
            )
        else:
            graphql_attr_type, nullable = self.create_graphql_type(
                python_type=field.annotation, context=context
            )
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
        default_case: Optional[DefaultCase],
        mutation_factory: bool = False,
    ) -> None:
        self.schema = schema
        self.default_case = default_case
        self.mutation_factory = mutation_factory
        self.input_factory = input_factory
        self.type_factory = type_factory

    def create_function(
        self,
        func: Callable[..., T_ANY],
        name: Optional[str] = None,
        default_case: Optional[DefaultCase] = None,
    ) -> GraphQLFunction:

        defaults = next(
            (
                d
                for d in [default_case, self.default_case, DefaultUnchanged()]
                if d is not None
            )
        )

        if not name:
            name = defaults(func.__name__)
        func_signature = inspect.signature(func)

        if func_signature.return_annotation == inspect.Parameter.empty:
            raise GraphQLFactoryException(
                f"{'Mutation' if self.mutation_factory else 'Query'} "
                f"{name} implemented in {func.__qualname__}"
                f" does not have a return type annotation"
            )

        graphql_type, nullable = self.type_factory.create_graphql_type(
            func_signature.return_annotation, context=None
        )

        graphql_query = GraphQLFunction(
            name=name, return_type=graphql_type.ref(nullable)
        )

        for param_name, definition in func_signature.parameters.items():
            if definition.default is inspect.Parameter.empty or isinstance(
                definition.default, GraphQLFunctionField
            ):
                graphql_query.add_parameter(
                    self.parameter_factory(definition, func, param_name, defaults)
                )
            elif isinstance(definition.default, Injectable):
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
        defaults: DefaultCase,
    ) -> GraphQLFunctionField:
        func_parameter: GraphQLFunctionField = (
            definition.default
            if definition.default is not inspect.Parameter.empty
            else GraphQLFunctionField()
        )
        func_parameter.set_python_name(param_name)
        if definition.annotation == inspect.Parameter.empty:
            raise GraphQLFactoryException(
                f"Method {func.__qualname__} defines a {GraphQLFunctionField.__name__} "
                "without type definition."
            )
        graphql_type, nullable = self.input_factory.create_graphql_type(
            definition.annotation, context=None
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

    def dependency_injection_factory(self, injectable: Injectable) -> Injectable:

        if isinstance(injectable, InjectableFunction):
            assert injectable.callable
            func_signature = inspect.signature(injectable.callable)

            for param_name, definition in func_signature.parameters.items():
                if isinstance(definition.default, Injectable):
                    injectable.dependencies[
                        param_name
                    ] = self.dependency_injection_factory(definition.default)

        return injectable
