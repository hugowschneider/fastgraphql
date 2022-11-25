from typing import Any, Callable, Dict, ForwardRef, List, Optional, Type, TypeVar

from fastgraphql.exceptions import GraphQLRuntimeError
from fastgraphql.injection import Injectable, InjectableRequestType
from fastgraphql.utils import DEFAULT_TAB

T_ANY = TypeVar("T_ANY")
T = TypeVar("T")


class GraphQLDataType:
    def __init__(self, name: str, python_type: Optional[Type[Any]]):
        self.name = name
        self.python_type = python_type

    def ref(self, nullable: bool = False) -> "GraphQLReference":
        raise NotImplementedError  # pragma: no cover

    def render(self) -> str:
        raise NotImplementedError  # pragma: no cover

    def map_from_input(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        return kwargs

    def map_to_output(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        return kwargs


class GraphQLReference:
    def __init__(
        self, referenced_type: GraphQLDataType, nullable: bool = False
    ) -> None:
        self.python_type = referenced_type.python_type
        self.referenced_type = referenced_type
        self.nullable = nullable

    def render(self) -> str:
        return f"{self.referenced_type.name}{'' if self.nullable else '!'}"


class GraphQLTypeAttribute:
    def __init__(
        self, graphql_name: str, python_name: str, type_reference: GraphQLReference
    ):
        self.graphql_name = graphql_name
        self.python_name = python_name
        self.type_reference = type_reference

    def render(self) -> str:
        return f"{self.graphql_name}: {self.type_reference.render()}"


class GraphQLType(GraphQLDataType):
    def __init__(
        self,
        name: str,
        python_type: Type[T],
        attrs: Optional[Dict[str, GraphQLTypeAttribute]] = None,
        as_input: bool = False,
    ):
        super().__init__(name=name, python_type=python_type)
        if not attrs:
            attrs = {}
        self.attrs = attrs
        self.as_input = as_input

    def add_attribute(self, field: GraphQLTypeAttribute) -> None:
        self.attrs[field.graphql_name] = field

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(self, nullable=nullable)

    def map_from_input(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        mapped_kwargs: Dict[str, Any] = {}
        for attr in self.attrs.values():
            mapped_kwargs[
                attr.python_name
            ] = attr.type_reference.referenced_type.map_from_input(
                kwargs[attr.graphql_name]
            )

        return mapped_kwargs

    def map_to_output(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        mapped_kwargs: Dict[str, Any] = {}
        for attr in self.attrs.values():
            mapped_kwargs[
                attr.graphql_name
            ] = attr.type_reference.referenced_type.map_to_output(
                kwargs[attr.python_name]
            )

        return mapped_kwargs

    def render(self) -> str:
        separator = f"\n{DEFAULT_TAB}"
        decl = "input" if self.as_input else "type"
        return f"""
{decl} {self.name} {{
    {separator.join([attr.render() for attr in self.attrs.values()])}
}}
        """.strip()


class GraphQLDelayedReference(GraphQLReference):
    def __init__(
        self, referenced_type: GraphQLDataType, nullable: bool = False
    ) -> None:
        super().__init__(referenced_type, nullable)

    def render(self) -> str:
        raise GraphQLRuntimeError(
            f'Python ForwardRef "{self.referenced_type.name}" '
            "must be resolved before rendering the GraphQL schema"
        )


class GraphQLDelayedType(GraphQLType):
    def __init__(self, forward_ref: ForwardRef):
        super().__init__(forward_ref.__forward_arg__, ForwardRef)

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLDelayedReference(referenced_type=self, nullable=nullable)

    def render(self) -> str:
        raise GraphQLRuntimeError(
            f'Python ForwardRef "{self.name}" must be resolved'
            "before rendering the GraphQL schema"
        )


class GraphQLArray(GraphQLDataType):
    def __init__(self, item_type: GraphQLReference):
        if isinstance(item_type, GraphQLDelayedReference):
            name = f"[{item_type.referenced_type.name}]"
        else:
            name = f"[{item_type.render()}]"
        super().__init__(python_type=list, name=name)

        self.item_type = item_type

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return self.item_type.__class__(referenced_type=self, nullable=nullable)


class GraphQLFunctionField(InjectableRequestType):
    def __init__(
        self,
        graphql_type: Optional[GraphQLReference] = None,
        name: Optional[str] = None,
    ):
        super().__init__(python_type=graphql_type.python_type if graphql_type else None)
        self.name = name
        self.reference = graphql_type
        self.python_name: str = ""

    def set_name(self, name: str) -> None:
        self.name = name

    def set_python_name(self, python_name: str) -> None:
        self.python_name = python_name

    def render(self) -> str:
        assert self.reference
        return f"{self.name}: {self.reference.render()}"

    def map_from_input(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        assert self.reference
        return self.reference.referenced_type.map_from_input(kwargs)


class GraphQLQueryField(GraphQLFunctionField):
    ...


class GraphQLFunction:
    def __init__(
        self,
        name: str,
        return_type: GraphQLReference,
        parameters: Optional[List[GraphQLFunctionField]] = None,
    ):
        self.name = name
        self.return_type = return_type
        self.parameters: List[GraphQLFunctionField] = parameters if parameters else []
        self.resolver: Optional[Callable[..., T_ANY]] = None
        self.injected_parameters: Dict[str, Injectable] = {}

    def add_parameter(self, parameter: GraphQLFunctionField) -> None:
        self.parameters.append(parameter)

    def add_injected_parameter(self, name: str, injectable: Injectable) -> None:
        self.injected_parameters[name] = injectable

    def render(self) -> str:
        parameters = ", ".join([p.render() for p in self.parameters])
        if parameters:
            parameters = f"({parameters})"
        return f"{self.name}{parameters}: {self.return_type.render()}"

    def map_to_output(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        return self.return_type.referenced_type.map_to_output(kwargs)
