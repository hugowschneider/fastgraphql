from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from fastgraphql.exceptions import GraphQLSchemaException
from fastgraphql.scalars import GraphQLScalar
from fastgraphql.types import GraphQLFunction, GraphQLType
from fastgraphql.utils import DEFAULT_TAB

T = TypeVar("T")


class GraphQLSchema:
    def __init__(self) -> None:
        self.types: Dict[str, GraphQLType] = {}
        self.scalars: Dict[str, GraphQLScalar] = {}
        self.inputs: Dict[str, GraphQLType] = {}
        self.queries: Dict[str, GraphQLFunction] = {}
        self.mutations: Dict[str, GraphQLFunction] = {}

    def check_type_name_conflict(
        self, graphql_type: Union[GraphQLType, GraphQLScalar]
    ) -> None:
        if graphql_type.name in self.inputs:
            raise GraphQLSchemaException(
                f"The GraphQL name '{graphql_type.name}' is already used as an input. "
                "Please specify another name!"
            )
        if graphql_type.name in self.types:
            raise GraphQLSchemaException(
                f"The GraphQL name '{graphql_type.name}' is already used as an type. "
                "Please specify another name!"
            )
        if graphql_type.name in self.scalars and not isinstance(
            graphql_type, GraphQLScalar
        ):
            raise GraphQLSchemaException(
                f"The GraphQL name '{graphql_type.name}' is already used as an scalar. "
                "Please specify another name!"
            )

    def check_function_name_conflict(self, graphql_type: GraphQLFunction) -> None:
        if graphql_type.name in self.queries:
            raise GraphQLSchemaException(
                f"The GraphQL name '{graphql_type.name}' is already used for a query. "
                "Please specify another name!"
            )
        if graphql_type.name in self.mutations:
            raise GraphQLSchemaException(
                f"The GraphQL name '{graphql_type.name}' is already "
                "used for a mutation. "
                "Please specify another name!"
            )

    def add_type(self, graphql_type: GraphQLType) -> None:
        self.check_type_name_conflict(graphql_type=graphql_type)
        self.types[graphql_type.name] = graphql_type

    def add_scalar(self, graphql_type: GraphQLScalar) -> None:
        self.check_type_name_conflict(graphql_type=graphql_type)
        self.scalars[graphql_type.name] = graphql_type

    def add_input_type(self, graphql_type: GraphQLType) -> None:
        self.check_type_name_conflict(graphql_type=graphql_type)
        self.inputs[graphql_type.name] = graphql_type

    def render(self) -> str:
        separator = "\n\n"
        GT = Union[GraphQLType, GraphQLScalar]

        def sort_and_write(types: Iterable[GT]) -> str:
            sorted_types = sorted(types, key=lambda x: x.name)
            return separator.join([s.render() for s in sorted_types])

        def sort_and_write_functions(
            functions: Iterable[GraphQLFunction], as_mutation: bool
        ) -> str:
            if not any(functions):
                return ""
            decl = "Mutation" if as_mutation else "Query"
            sorted_types = sorted(functions, key=lambda x: x.name)
            queries_str = f"\n{DEFAULT_TAB}".join([s.render() for s in sorted_types])
            return f"""
type {decl} {{
    {queries_str}
}}""".strip()

        s = separator.join(
            s
            for s in [
                sort_and_write(cast(Iterable[GT], self.scalars.values())),
                sort_and_write(cast(Iterable[GT], self.types.values())),
                sort_and_write(cast(Iterable[GT], self.inputs.values())),
                sort_and_write_functions(
                    cast(Iterable[GraphQLFunction], self.queries.values()), False
                ),
                sort_and_write_functions(
                    cast(Iterable[GraphQLFunction], self.mutations.values()), True
                ),
            ]
            if len(s)
        )
        return s

    def add_query(self, graphql_query: GraphQLFunction) -> None:
        self.check_function_name_conflict(graphql_query)
        self.queries[graphql_query.name] = graphql_query

    def add_mutation(self, graphql_mutation: GraphQLFunction) -> None:
        self.check_function_name_conflict(graphql_mutation)
        self.mutations[graphql_mutation.name] = graphql_mutation


class SelfGraphQL:
    @staticmethod
    @overload
    def introspect(type_: Type[Any]) -> Optional["SelfGraphQLType"]:  # pragma: no cover
        ...

    @staticmethod
    @overload
    def introspect(
        type_: Callable[..., Any]
    ) -> Optional["SelfGraphQLFunction"]:  # pragma: no cover
        ...

    @staticmethod
    def introspect(
        type_: Union[Type[Any], Callable[..., Any]]
    ) -> Union["SelfGraphQL", None]:
        if hasattr(type_, "__graphql__"):
            graphql_dict = cast(Dict[str, SelfGraphQL], getattr(type_, "__graphql__"))
            if type_.__name__ in graphql_dict:
                return graphql_dict[type_.__name__]
        return None

    @staticmethod
    def check_if_exists(
        python_type: Type[Any], as_input: bool
    ) -> Optional[GraphQLType]:
        if i := SelfGraphQL.introspect(python_type):
            if as_input and (graphql_input := i.as_input):
                return cast(GraphQLType, graphql_input)
            elif not as_input and (graphql_type := i.as_type):
                return cast(GraphQLType, graphql_type)
        return None

    @classmethod
    def add_type_metadata(
        cls, python_type: Type[T], graphql_type: GraphQLType, as_input: bool
    ) -> None:
        if not hasattr(python_type, "__graphql__"):
            setattr(python_type, "__graphql__", {})

        graphql_dict = getattr(python_type, "__graphql__")
        if python_type.__name__ not in graphql_dict:
            graphql_dict[python_type.__name__] = SelfGraphQLType()

        if i := SelfGraphQL.introspect(python_type):
            if as_input:
                i.as_input = graphql_type
            else:
                i.as_type = graphql_type

    @classmethod
    def add_funtion_metadata(
        cls,
        func: Callable[..., T],
        graphql_function: GraphQLFunction,
        as_mutation: bool = False,
    ) -> None:
        if not hasattr(func, "__graphql__"):
            setattr(func, "__graphql__", {})

        graphql_dict = getattr(func, "__graphql__")
        if func.__name__ not in graphql_dict:
            graphql_dict[func.__name__] = SelfGraphQLFunction()

        if i := SelfGraphQL.introspect(func):
            if as_mutation:
                i.as_mutation = graphql_function
            else:
                i.as_query = graphql_function


class SelfGraphQLType(SelfGraphQL):
    def __init__(self) -> None:
        self.as_type: Optional[GraphQLType] = None
        self.as_input: Optional[GraphQLType] = None


class SelfGraphQLFunction(SelfGraphQL):
    def __init__(self) -> None:
        self.as_query: Optional[GraphQLFunction] = None
        self.as_mutation: Optional[GraphQLFunction] = None
