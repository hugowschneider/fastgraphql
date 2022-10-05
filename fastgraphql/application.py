import functools
import inspect
import logging

from fastgraphql.exceptions import GraphQLRunTimeError
from fastgraphql.factory import GraphQLTypeFactory, GraphQLFunctionFactory, _DateFormats

from typing import (
    Type,
    TypeVar,
    Optional,
    Callable,
    List,
    Any,
    Tuple,
    Dict,
    cast,
)
from pydantic import BaseModel

from fastgraphql.injection import InjectableFunction
from fastgraphql.schema import GraphQLSchema
from fastgraphql.types import GraphQLType, GraphQLQueryField, GraphQLFunction
from fastgraphql.scalars import GraphQLScalar
from fastgraphql.utils import DefaultNames

T = TypeVar("T", bound=BaseModel)
T_ANY = TypeVar("T_ANY")


class FastGraphQL:
    def __init__(self, default_names: Optional[DefaultNames] = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_names = default_names
        time_format = "%H:%M:%S"
        date_format = "%Y-%m-%d"
        self._date_formats = _DateFormats(
            date_format=date_format,
            time_format=time_format,
            date_time_format=f"{date_format}T{time_format}%z",
        )
        self.schema = GraphQLSchema()
        self.type_factory = GraphQLTypeFactory(
            schema=self.schema,
            input_factory=False,
            date_formats=self._date_formats,
            default_names=default_names,
        )
        self.input_factory = GraphQLTypeFactory(
            schema=self.schema,
            input_factory=True,
            date_formats=self._date_formats,
            default_names=default_names,
        )
        self.query_factory = GraphQLFunctionFactory(
            schema=self.schema,
            mutation_factory=False,
            input_factory=self.input_factory,
            type_factory=self.type_factory,
            default_names=default_names,
        )
        self.mutation_factory = GraphQLFunctionFactory(
            schema=self.schema,
            mutation_factory=True,
            input_factory=self.input_factory,
            type_factory=self.type_factory,
            default_names=default_names,
        )

    def get_date_format(self) -> str:
        return self._date_formats.date_format.value

    def get_time_format(self) -> str:
        return self._date_formats.time_format.value

    def get_date_time_format(self) -> str:
        return self._date_formats.date_time_format.value

    def set_date_format(self, date_format: str) -> None:
        self._date_formats.date_format.set_value(date_format)

    def set_time_format(self, time_format: str) -> None:
        self._date_formats.time_format.set_value(time_format)

    def set_date_time_format(self, date_time_format: str) -> None:
        self._date_formats.date_time_format.set_value(date_time_format)

    def set_sqlalchemy_base(self, base: Any) -> None:
        self.input_factory.sqlalchemy_base = base
        self.type_factory.sqlalchemy_base = base

    def render(self) -> str:
        return self.schema.render()

    def _graphql_model(
        self,
        exclude_model_attrs: Optional[List[str]],
        name: Optional[str],
        as_input: bool,
        default_names: Optional[DefaultNames],
    ) -> Callable[..., Type[T]]:
        if exclude_model_attrs is None:
            exclude_model_attrs = []

        def decorator(python_type: Type[T]) -> Type[T]:
            self.logger.info(
                f"Constructing GraphQL {'input' if as_input else 'type'} for {python_type.__qualname__}"
            )
            if as_input:
                factory = self.input_factory
            else:
                factory = self.type_factory

            graphql_type, _ = factory.create_graphql_type(
                python_type=python_type,
                name=name,
                exclude_model_attrs=exclude_model_attrs,
                default_names=default_names,
            )
            if not isinstance(graphql_type, GraphQLType):  # pragma: no cover
                raise GraphQLRunTimeError("Something went wrong")

            return python_type

        return decorator

    def type(
        self,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
        default_names: Optional[DefaultNames] = None,
    ) -> Callable[..., Type[T]]:
        return self._graphql_model(
            exclude_model_attrs=exclude_model_attrs,
            name=name,
            as_input=False,
            default_names=default_names,
        )

    def input(
        self,
        exclude_model_attrs: Optional[List[str]] = None,
        default_names: Optional[DefaultNames] = None,
        name: Optional[str] = None,
    ) -> Callable[..., Type[T]]:
        return self._graphql_model(
            exclude_model_attrs=exclude_model_attrs,
            name=name,
            as_input=True,
            default_names=default_names,
        )

    def query(
        self,
        name: Optional[str] = None,
        default_names: Optional[DefaultNames] = None,
    ) -> Callable[..., Callable[..., T_ANY]]:
        return self._graphql_function(
            name=name, as_mutation=False, default_names=default_names
        )

    def mutation(
        self,
        name: Optional[str] = None,
        default_names: Optional[DefaultNames] = None,
    ) -> Callable[..., Callable[..., T_ANY]]:
        return self._graphql_function(
            name=name, as_mutation=True, default_names=default_names
        )

    def _graphql_function(
        self,
        name: Optional[str],
        as_mutation: bool,
        default_names: Optional[DefaultNames],
    ) -> Callable[..., Callable[..., T_ANY]]:
        def decorator(func: Callable[..., T_ANY]) -> Callable[..., T_ANY]:
            self.logger.info(
                f"Constructing GraphQL {'mutation' if as_mutation else 'query'} for {func.__qualname__}"
            )
            if as_mutation:
                graphql_type = self.mutation_factory.create_function(
                    func=func, name=name, default_names=default_names
                )
                self.schema.add_mutation(graphql_type)
            else:
                graphql_type = self.query_factory.create_function(
                    func=func, name=name, default_names=default_names
                )
                self.schema.add_query(graphql_type)

            if not isinstance(graphql_type, GraphQLFunction):  # pragma: no cover
                raise GraphQLRunTimeError("Something went wrong")

            @functools.wraps(func)
            def _decorator(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> T_ANY:
                resolved_kwargs: Dict[str, Any] = {}
                for parameter in graphql_type.parameters:
                    python_name = parameter.python_name
                    name = parameter.name
                    assert python_name
                    assert name
                    value = kwargs[name]
                    resolved_kwargs[python_name] = (
                        parameter(**value) if parameter.is_callable() else value
                    )

                for name, injectable in graphql_type.injected_parameters.items():
                    value = injectable()
                    if inspect.isgenerator(value):
                        resolved_kwargs[name] = next(value)
                    else:
                        resolved_kwargs[name] = value

                return_value = func(**resolved_kwargs)
                if isinstance(return_value, BaseModel):
                    return cast(T_ANY, graphql_type.map_to_output(return_value.dict()))
                else:
                    return return_value

            graphql_type.resolver = _decorator

            return _decorator

        return decorator

    def parameter(
        self, name: Optional[str] = None, graphql_scalar: Optional[GraphQLScalar] = None
    ) -> Any:
        if g := graphql_scalar:
            if not g.default_scalar:
                self.schema.add_scalar(graphql_scalar)

            return GraphQLQueryField(name=name, graphql_type=graphql_scalar.ref())

        return GraphQLQueryField(name=name)

    def depends(self, dependency_provider: Callable[..., Any]) -> Any:
        return InjectableFunction(dependency_provider)
