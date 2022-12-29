"""This Module contains the entry point for all GraphQL definitions"""

import functools
import logging

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from pydantic import BaseModel

from fastgraphql.exceptions import GraphQLRuntimeError
from fastgraphql.factory import GraphQLFunctionFactory, GraphQLTypeFactory, _DateFormats
from fastgraphql.injection import InjectableContext, InjectableFunction, InjectableType
from fastgraphql.scalars import GraphQLScalar
from fastgraphql.schema import GraphQLSchema
from fastgraphql.types import GraphQLFunction, GraphQLQueryField, GraphQLType
from fastgraphql.utils import DefaultCase

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)
T = TypeVar("T")


class FastGraphQL:
    """This class is used to define and generate all code-based GraphQL definition.


    Args:
        default_case (Optional[DefaultNames], optional):
            Defines the default case convention for all GraphQL
            names. Defaults to None, which means all names will
            be exactly the same as the defined python names.
        time_format (str, optional):
            Defines time format for the Time Scalar. Defaults to "%H:%M:%S"
        date_format (str, optional):
            Defines time format for the Time Scalar. Defaults to "%Y-%m-%d"
        date_time_format (str, optional):
            Defines time format for the Time Scalar. Defaults to "%Y-%m-%dT%H:%M:%S%z"
    """

    def __init__(
        self,
        default_case: Optional[DefaultCase] = None,
        time_format: str = "%H:%M:%S",
        date_format: str = "%Y-%m-%d",
        date_time_format: str = "%Y-%m-%dT%H:%M:%S%z",
    ) -> None:

        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_case = default_case
        self._date_formats = _DateFormats(
            date_format=date_format,
            time_format=time_format,
            date_time_format=date_time_format,
        )
        self.schema = GraphQLSchema()
        self.type_factory = GraphQLTypeFactory(
            schema=self.schema,
            input_factory=False,
            date_formats=self._date_formats,
            default_case=default_case,
        )
        self.input_factory = GraphQLTypeFactory(
            schema=self.schema,
            input_factory=True,
            date_formats=self._date_formats,
            default_case=default_case,
        )
        self.query_factory = GraphQLFunctionFactory(
            schema=self.schema,
            mutation_factory=False,
            input_factory=self.input_factory,
            type_factory=self.type_factory,
            default_case=default_case,
        )
        self.mutation_factory = GraphQLFunctionFactory(
            schema=self.schema,
            mutation_factory=True,
            input_factory=self.input_factory,
            type_factory=self.type_factory,
            default_case=default_case,
        )

    def get_date_format(self) -> str:
        """
        Returns the current date format.

        Returns:
            str: Current date format
        """
        return self._date_formats.date_format.value

    def get_time_format(self) -> str:
        """
        Returns the current time format.

        Returns:
            str: Current time format
        """
        return self._date_formats.time_format.value

    def get_date_time_format(self) -> str:
        """
        Returns the current date time format.

        Returns:
            str: Current date time format
        """
        return self._date_formats.date_time_format.value

    def set_sqlalchemy_base(self, base: Any) -> None:
        """This methods enables SQLAlchemy models to be
        transformed into GraphQL types and/or inputs.

        ```python
        Base = declarative_base()
        ...
        fast_graphql = FastGraphQL()
        fast_graphql.set_sqlalchemy_base(base=Base)
        ```

        Args:
            base (Any): The base class of all SQLAlchemy
                        models should be given here

        """
        self.input_factory.sqlalchemy_base = base
        self.type_factory.sqlalchemy_base = base

    def render(self) -> str:
        """This method renders all GraphQL definition

        Returns:
            str: GraphQL definition
        """
        return self.schema.render()

    def _graphql_model(
        self,
        exclude_model_attrs: Optional[List[str]],
        name: Optional[str],
        as_input: bool,
        default_case: Optional[DefaultCase],
    ) -> Callable[..., Type[PydanticModel]]:
        if exclude_model_attrs is None:
            exclude_model_attrs = []

        def decorator(python_type: Type[PydanticModel]) -> Type[PydanticModel]:
            self.logger.info(
                "Constructing GraphQL %s for %s",
                "input" if as_input else "type",
                python_type.__qualname__,
            )
            if as_input:
                factory = self.input_factory
            else:
                factory = self.type_factory

            graphql_type, _ = factory.create_graphql_type(
                python_type=python_type,
                name=name,
                exclude_model_attrs=exclude_model_attrs,
                default_case=default_case,
                context=None,
            )
            if not isinstance(graphql_type, GraphQLType):  # pragma: no cover
                raise GraphQLRuntimeError("Something went wrong")

            return python_type

        return decorator

    def type(
        self,
        exclude_model_attrs: Optional[List[str]] = None,
        name: Optional[str] = None,
        default_case: Optional[DefaultCase] = None,
    ) -> Callable[..., Type[PydanticModel]]:
        """This decorator informs FastGraphQL that the decorated class
        is a GraphQL type.

        ```python
        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class MyType(BaseModel):
            ...
        ```

        Note: *This method is a decorator*

        Args:
            exclude_model_attrs (Optional[List[str]], optional):
                List of class attributes to be excluded from the GraphQL defintion.
                Defaults to None.
            name (Optional[str], optional):
                Custom type name, if `None`, the class name is used.
                Defaults to None.
            default_case (Optional[DefaultCase], optional):
                Defines the default case convention for type and attributes names.
                Defaults to None, which means either it defautls to what is set in
                [fastgraphql.FastGraphQL][] or all names will be exactly the same as
                the defined python names.

                This value overrides the value set in [fastgraphql.FastGraphQL][]

        Raises:
            GraphQLFactoryException: In case of unsupport data types
                                     in a class attribute

        Returns:
            (Callable[..., Type[PydanticModel]]): Python Decorator
        """
        return self._graphql_model(
            exclude_model_attrs=exclude_model_attrs,
            name=name,
            as_input=False,
            default_case=default_case,
        )

    def input(
        self,
        exclude_model_attrs: Optional[List[str]] = None,
        default_case: Optional[DefaultCase] = None,
        name: Optional[str] = None,
    ) -> Callable[..., Type[PydanticModel]]:
        """This decorator informs FastGraphQL that the decorated class
        is a GraphQL input.

        ```python
        fast_graphql = FastGraphQL()

        @fast_graphql.input()
        class MyType(BaseModel):
            ...
        ```

        Note: *This method is a decorator*

        For more details see [fastgraphql.FastGraphQL.type][]

        """
        return self._graphql_model(
            exclude_model_attrs=exclude_model_attrs,
            name=name,
            as_input=True,
            default_case=default_case,
        )

    def query(
        self,
        name: Optional[str] = None,
        default_case: Optional[DefaultCase] = None,
    ) -> Callable[..., Callable[..., T]]:
        """This decorates a method which should be considered by
            FastGraphQL to be a query.

        ```python
        fast_graphql = FastGraphQL()

        @fast_graphql.query()
        def my_query() -> str:
            return "..."
        ```

        Note: *This method is a decorator*

        Args:
            name (Optional[str], optional):
                Custom query name. Defaults to None, which means
                the query name will be the same as the python name
            default_case (Optional[DefaultCase], optional):
                Defines the default case convention for query and parameter names.
                Defaults to None, which means either it defautls to what is set in
                [fastgraphql.FastGraphQL][] or all names will be exactly the same
                as the defined python names. This value overrides the value set
                in [fastgraphql.FastGraphQL][]
        Raises:
            GraphQLFactoryException: In case of unsupport data types in a
                                     class attribute


        Returns:
            (Callable[..., Callable[..., T]]): Python Decorator
        """
        return self._graphql_function(
            name=name, as_mutation=False, default_case=default_case
        )

    def mutation(
        self,
        name: Optional[str] = None,
        default_case: Optional[DefaultCase] = None,
    ) -> Callable[..., Callable[..., T]]:
        """This decorates a method which should be considered by
            FastGraphQL to be a mutation.

        ```python
        fast_graphql = FastGraphQL()

        @fast_graphql.mutation()
        def my_myutation() -> str:
            return "..."
        ```

        Note: *This method is a decorator*

        For more details see [fastgraphql.FastGraphQL.query][]

        """

        return self._graphql_function(
            name=name, as_mutation=True, default_case=default_case
        )

    def _graphql_function(
        self,
        name: Optional[str],
        as_mutation: bool,
        default_case: Optional[DefaultCase],
    ) -> Callable[..., Callable[..., T]]:
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            self.logger.info(
                "Constructing GraphQL %s for %s",
                "mutation" if as_mutation else "query",
                func.__qualname__,
            )
            if as_mutation:
                graphql_type = self.mutation_factory.create_function(
                    func=func, name=name, default_case=default_case
                )
                self.schema.add_mutation(graphql_type)
            else:
                graphql_type = self.query_factory.create_function(
                    func=func, name=name, default_case=default_case
                )
                self.schema.add_query(graphql_type)

            if not isinstance(graphql_type, GraphQLFunction):  # pragma: no cover
                raise GraphQLRuntimeError("Something went wrong")

            @functools.wraps(func)
            def _decorator(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> T:
                parameters_kwargs: Dict[str, Any] = {}
                for parameter in graphql_type.parameters:
                    python_name = parameter.python_name
                    name = parameter.name
                    assert python_name
                    assert name
                    value = kwargs[name]
                    parameters_kwargs[python_name] = (
                        parameter(**value) if parameter.is_callable() else value
                    )

                injected_kwargs: Dict[str, Any] = {}
                for name, injectable in graphql_type.injected_parameters.items():
                    injected_kwargs[name] = injectable(
                        *args, **{**kwargs, **parameters_kwargs}
                    )

                return_value = func(**{**injected_kwargs, **parameters_kwargs})
                if isinstance(return_value, BaseModel):
                    return cast(T, graphql_type.map_to_output(return_value.dict()))

                return return_value

            graphql_type.resolver = _decorator

            return _decorator

        return decorator

    def parameter(
        self, name: Optional[str] = None, graphql_scalar: Optional[GraphQLScalar] = None
    ) -> Any:
        """This method is used to "annotate" query and mutation parameters.
            Any method parameter is considered to be a query or mutation input
            even is not annotated. This method hence not mandatory, opens the
            oportunity to custimaze the behaviour of parameters.

        ```python
        fast_graphql = FastGraphQL()

        @fast_graphql.mutation()
        def my_myutation(param: str = fast_graphql.parameter(name="myParam")) -> str:
            return "..."
        ```

        Args:
            name (Optional[str], optional):
                Name of the parameter. Defaults to None, which
                means, the python name will be used.
            graphql_scalar (Optional[GraphQLScalar], optional):
                A Custom scalar to be use as GraphQL Scalar for
                this parameter. Defaults to None.

        Returns:
            Any: Annotation
        """
        if g := graphql_scalar:
            if not g.default_scalar:
                self.schema.add_scalar(graphql_scalar)

            return GraphQLQueryField(name=name, graphql_type=graphql_scalar.ref())

        return GraphQLQueryField(name=name)

    def depends_on(
        self,
        dependency_provider: Callable[..., Any],
        parameters: Union[bool, Dict[str, str], Literal["*"]] = False,
    ) -> Any:
        """This method implements a dependecy injection pattern by "annotateting"
            query and mutation parameter to have values injected though a dependency
            provider method at runtime.

            This method can also annotate parameters in nested dependency
            provider method.



        ```python

        fast_graphql = FastGraphQL()

        class Person(BaseModel):
            name: str

        def provider(name: str) -> int:
            ...
            return 0

        @fast_graphql.mutation()
        def my_myutation(
            person: Person,
            dependency: int = fast_graphql.depends_on(
                provider,
                {"name": "person.name"}
            )
        ) -> str:
            return "..."
        ```

        Args:
            dependency_provider (Callable[..., Any]):
                Python method which provides a dependency to be injected
            parameters (Union[bool, Dict[str, str], Literal["*"]], optional):
                Parameters to be passed to the provider method. Defaults to False.
                `True` or `"*"` means all parameters will be passed to the provider
                function and names must match. If a Dict ist provided it maps provider
                function parameters (pp) and method paramenters (mp) in the form
                `{"pp": "mp"}`, where method parameters can be in a dot format to
                handle complex types, e.g `{"pp": "A.b[0].c"}`

        Returns:
            Any:
                At runtime it returns the dependecy computed by the
                `dependency_provider` method
        """
        return InjectableFunction(dependency_provider, parameters)

    def depends_on_resolver_info(self) -> Any:
        """Injects the query or mutation request info depending on the used engine.
        For now FastGraphQL only supports engines that implements
        [GraphQL-Core's](https://github.com/graphql-python/graphql-core)
        `GraphQLResolveInfo`

        Returns:
            Any: Instance of `GraphQLResolveInfo` given to the query handler at runtime
        """
        return InjectableContext()

    def depends_on_type(self, python_type: Type[Any]) -> Any:
        """Injects the first instance of `python_type` found in the query or mutation
        request info at runtime.

        Args:
            python_type (Type[Any]): The python type FastGraphQL should look for

        Returns:
            Any: The first found instance of `python_type` or None
        """
        return InjectableType(python_type=python_type)
